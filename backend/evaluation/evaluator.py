import json
import time
import os
import traceback
import sys

from backend.evaluation.question_generator import generate_questions
from backend.evaluation.metrics import evaluate_retrieval, evaluate_answer
from backend.evaluation.diagnostics import diagnose_failure
from backend.evaluation.report_writer import write_iteration_report, append_metrics_history, append_benchmark_history

from backend.rag.chat import single_paper_chat

def load_config():
    with open("backend/evaluation/configs/evaluation_config.json", "r") as f:
        return json.load(f)

def run_evaluation(dataset_file, iteration_num, modified_files=None):
    """
    Runs the full evaluation loop over a dataset.
    """
    if modified_files is None:
        modified_files = []
        
    print(f"==================================================")
    print(f" Starting Evaluation Iteration {iteration_num}")
    print(f"==================================================")
    
    config = load_config()
    targets = config["targets"]
    
    with open(dataset_file, "r") as f:
        paper_ids = json.load(f)
        
    total_papers = len(paper_ids)
    
    overall_stats = {
        "retrieval_precision": [],
        "retrieval_recall": [],
        "faithfulness": [],
        "groundedness": [],
        "hallucination": [],
        "formatting": [],
        "latency": [],
        "pass_rate": [],
        "context_length": [],
        "prompt_length": [],
        "retrieval_time": [],
        "generation_time": []
    }
    
    per_paper = {}
    per_question = []
    
    start_time_global = time.time()
    questions_completed = 0
    questions_failed = 0
    
    for p_idx, pid in enumerate(paper_ids):
        print(f"\n[Paper {p_idx+1} / {total_papers}] ID: {pid}")
        questions = generate_questions(pid)
        total_q = len(questions)
        
        paper_stats = {
            "retrieval": [],
            "faithfulness": [],
            "latency": []
        }
        
        for q_idx, q in enumerate(questions):
            q_start_time = time.time()
            query_text = q["query"]
            
            print(f"  [Q {q_idx+1} / {total_q}] {query_text} (Intent: {q['intent']})")
            
            try:
                # Use the production pipeline
                res = single_paper_chat(query=query_text, paper=pid)
                
                # Default failure values
                category = "Unknown"
                root_cause = "N/A"
                suggested_fix = "N/A"
                module = "N/A"
                is_pass = 0
                q_metrics = {}
                answer = ""
                trace = "N/A"
                
                if res.get("success"):
                    # Extract variables from production pipeline
                    answer = res.get("answer", "")
                    context = res.get("context", "")
                    prompt = res.get("prompt", "")
                    chunks = res.get("raw_chunks", [])
                    search_time = res.get("search_time", 0)
                    llm_time = res.get("llm_time", 0)
                    
                    # Evaluate
                    ret_metrics = evaluate_retrieval(q, chunks, q["intent"])
                    ans_metrics = evaluate_answer(q, context, answer)
                    
                    latency = time.time() - q_start_time
                    
                    q_metrics = {
                        **ret_metrics, 
                        **ans_metrics, 
                        "latency": latency,
                        "context_length": len(context),
                        "prompt_length": len(prompt),
                        "search_time": search_time,
                        "llm_time": llm_time,
                        "retrieved_count": len(chunks)
                    }
                    
                    category, root_cause, suggested_fix, module = diagnose_failure(q_metrics, targets, q)
                    is_pass = 1 if category == "Passed" else 0
                    
                    # Record for aggregate
                    overall_stats["retrieval_precision"].append(ret_metrics["retrieval_precision"])
                    overall_stats["retrieval_recall"].append(ret_metrics["retrieval_recall"])
                    overall_stats["faithfulness"].append(ans_metrics["faithfulness"])
                    overall_stats["groundedness"].append(ans_metrics["groundedness"])
                    overall_stats["hallucination"].append(ans_metrics["hallucination"])
                    overall_stats["formatting"].append(ans_metrics["formatting"])
                    overall_stats["latency"].append(latency)
                    overall_stats["pass_rate"].append(is_pass * 100.0)
                    overall_stats["context_length"].append(len(context))
                    overall_stats["prompt_length"].append(len(prompt))
                    overall_stats["retrieval_time"].append(search_time)
                    overall_stats["generation_time"].append(llm_time)
                    
                    paper_stats["retrieval"].append(ret_metrics["retrieval_precision"])
                    paper_stats["faithfulness"].append(ans_metrics["faithfulness"])
                    paper_stats["latency"].append(latency)
                    
                    print(f"    -> RetPrec: {ret_metrics['retrieval_precision']:.1f}% | Faithfulness: {ans_metrics['faithfulness']:.1f}% | Latency: {latency:.1f}s | Result: {'PASS' if is_pass else 'FAIL'} ({category})")
                    questions_completed += 1
                else:
                    error_msg = res.get("error", "Unknown Error")
                    category = "Missing Context" if "Missing Context" in error_msg else "Pipeline Error"
                    root_cause = error_msg
                    module = "backend/rag/chat.py"
                    print(f"    -> FAIL: {error_msg}")
                    questions_failed += 1
                    
            except Exception as e:
                category = "Exception"
                root_cause = str(e)
                trace = traceback.format_exc()
                module = "N/A"
                suggested_fix = "Check traceback"
                q_metrics = {}
                answer = ""
                print(f"    -> EXCEPTION: {e}")
                questions_failed += 1
            
            # Save question record
            q_record = {
                "paper_id": pid,
                "query": query_text,
                "intent": q["intent"],
                "type": q["type"],
                "metrics": q_metrics,
                "failure_category": category,
                "root_cause": root_cause,
                "suggested_fix": suggested_fix,
                "module": module,
                "answer": answer,
                "traceback": trace,
                "context_length": q_metrics.get("context_length", 0),
                "prompt_length": q_metrics.get("prompt_length", 0)
            }
            per_question.append(q_record)
            
            # Incremental save per question
            _write_incremental(iteration_num, overall_stats, per_question, per_paper, start_time_global, questions_completed, questions_failed)
            
        # Aggregate paper
        per_paper[pid] = {
            "avg_retrieval": sum(paper_stats["retrieval"]) / len(paper_stats["retrieval"]) if paper_stats["retrieval"] else 0,
            "avg_faithfulness": sum(paper_stats["faithfulness"]) / len(paper_stats["faithfulness"]) if paper_stats["faithfulness"] else 0,
            "avg_latency": sum(paper_stats["latency"]) / len(paper_stats["latency"]) if paper_stats["latency"] else 0,
        }
        
        # Incremental save per paper
        _write_incremental(iteration_num, overall_stats, per_question, per_paper, start_time_global, questions_completed, questions_failed)
        
    # Final aggregation
    final_overall = _calc_overall(overall_stats)
    
    append_metrics_history(iteration_num, final_overall)
    append_benchmark_history(iteration_num, final_overall, modified_files)
    
    print("\n==================================================")
    print(" Evaluation Complete!")
    print("==================================================")
    for k, v in final_overall.items():
        print(f"  {k}: {v:.2f}")
        
    return final_overall

def _calc_overall(stats):
    res = {}
    for k, v in stats.items():
        res[k] = sum(v) / len(v) if v else 0
    return res

def _write_incremental(iteration_num, overall_stats, per_question, per_paper, start_time, completed, failed):
    current_overall = _calc_overall(overall_stats)
    
    duration = time.time() - start_time
    
    current_overall["duration"] = duration
    current_overall["completed"] = completed
    current_overall["failed"] = failed
    
    write_iteration_report(iteration_num, current_overall, per_question, per_paper)

if __name__ == "__main__":
    run_evaluation("backend/evaluation/datasets/development_set.json", 1)
