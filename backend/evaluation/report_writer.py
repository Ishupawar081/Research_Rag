import json
import csv
import os
from datetime import datetime

def write_iteration_report(iteration_num, overall_metrics, per_question, per_paper):
    """
    Writes markdown and json reports for the iteration dynamically.
    """
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_file = f"backend/evaluation/reports/iteration_{iteration_num:03d}.md"
    json_file = f"backend/evaluation/reports/iteration_{iteration_num:03d}.json"
    
    # Write JSON
    with open(json_file, "w") as f:
        json.dump({
            "iteration": iteration_num,
            "timestamp": date_str,
            "overall": overall_metrics,
            "per_question": per_question,
            "per_paper": per_paper
        }, f, indent=4)
        
    # Write Markdown
    md = f"# Evaluation Iteration {iteration_num:03d}\n"
    md += f"**Date:** {date_str}\n\n"
    
    md += "## Execution Summary\n"
    md += f"- **Duration:** {overall_metrics.get('duration', 0):.2f}s\n"
    md += f"- **Completed Questions:** {overall_metrics.get('completed', 0)}\n"
    md += f"- **Failed Questions:** {overall_metrics.get('failed', 0)}\n\n"
    
    md += "## Overall Metrics\n"
    for k, v in overall_metrics.items():
        if k not in ["duration", "completed", "failed"]:
            md += f"- **{k.replace('_', ' ').title()}:** {v:.2f}\n"
        
    md += "\n## Per Paper Scores\n"
    for p, stats in per_paper.items():
        md += f"### {p}\n"
        for k, v in stats.items():
            md += f"- **{k}:** {v:.2f}\n"
            
    md += "\n## Failed Queries Diagnostics\n"
    for q in per_question:
        if q["failure_category"] != "Passed":
            md += f"### Question: {q['query']} (Paper: {q['paper_id']})\n"
            md += f"- **Intent:** {q['intent']}\n"
            md += f"- **Failure Category:** {q['failure_category']}\n"
            md += f"- **Root Cause:** {q['root_cause']}\n"
            md += f"- **Suggested Fix:** {q['suggested_fix']}\n"
            md += f"- **Target Module:** {q['module']}\n"
            md += f"- **Context Length:** {q.get('context_length', 0)}\n"
            md += f"- **Prompt Length:** {q.get('prompt_length', 0)}\n"
            
            trace = q.get('traceback', 'N/A')
            if trace != 'N/A':
                md += f"- **Exception Traceback:**\n```\n{trace}\n```\n"
                
            ans = str(q.get('answer', ''))
            if ans:
                md += f"- **Answer:** {ans[:300]}...\n"
            md += "\n"
            
    with open(report_file, "w") as f:
        f.write(md)
        
def append_metrics_history(iteration_num, metrics):
    """
    Appends overall metrics to CSV.
    """
    csv_file = "backend/evaluation/reports/metrics_history.csv"
    file_exists = os.path.exists(csv_file)
    
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Iteration", "Retrieval Precision", "Retrieval Recall", 
                "Faithfulness", "Groundedness", "Hallucination", "Formatting",
                "Pass Rate", "Avg Latency", "Avg Context Length"
            ])
            
        writer.writerow([
            iteration_num,
            f"{metrics.get('retrieval_precision', 0):.2f}",
            f"{metrics.get('retrieval_recall', 0):.2f}",
            f"{metrics.get('faithfulness', 0):.2f}",
            f"{metrics.get('groundedness', 0):.2f}",
            f"{metrics.get('hallucination', 0):.2f}",
            f"{metrics.get('formatting', 0):.2f}",
            f"{metrics.get('pass_rate', 0):.2f}",
            f"{metrics.get('latency', 0):.2f}",
            f"{metrics.get('context_length', 0):.0f}"
        ])

def append_benchmark_history(iteration_num, metrics, modified_files):
    json_file = "backend/evaluation/reports/benchmark_history.json"
    history = []
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            history = json.load(f)
            
    # Attempt to load LLM config to save it
    config = {}
    try:
        with open("backend/evaluation/configs/evaluation_config.json") as f:
            config = json.load(f)
    except:
        pass
        
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "iteration": iteration_num,
        "config": config,
        "metrics": metrics,
        "modified_files": modified_files
    })
    
    with open(json_file, "w") as f:
        json.dump(history, f, indent=4)
