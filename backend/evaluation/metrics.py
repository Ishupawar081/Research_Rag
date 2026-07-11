import json
import time
import re

from backend.rag.retriever import SECTION_ALIASES
from backend.rag.llm import generate
from backend.evaluation.evaluator_prompt import EVALUATOR_PROMPT
from backend.rag.loader import resources

def evaluate_retrieval(query_info, retrieved_chunks, detected_intent):
    """
    Computes heuristic retrieval metrics based on intent.
    Returns scores 0-100.
    """
    if not retrieved_chunks:
        return {
            "retrieval_precision": 0.0,
            "retrieval_recall": 0.0,
            "relevant_chunk_percent": 0.0,
            "relevant_section_percent": 0.0,
            "wrong_section_percent": 100.0,
            "duplicate_chunk_percent": 0.0,
            "metadata_precision": 0.0,
            "metadata_recall": 0.0,
            "reference_precision": 0.0,
            "reference_recall": 0.0
        }
        
    expected_intent = query_info["intent"]
    total_chunks = len(retrieved_chunks)
    
    unique_ids = set()
    duplicates = 0
    relevant_chunks = 0
    wrong_sections = 0
    
    metadata_count = 0
    ref_count = 0
    
    expected_aliases = SECTION_ALIASES.get(expected_intent, [])
    
    # 1. Gather all actual available sections for this paper to calculate exact Recall
    paper_id = query_info.get("paper_id")
    available_metadata = False
    available_references = False
    available_target_sections = set()
    
    if paper_id:
        for meta in resources.metadata:
            if meta["paper_id"] == paper_id:
                ct = meta.get("chunk_type", "")
                st = str(meta.get("section_title") or "").lower()
                cid = str(meta.get("chunk_id") or "").lower()
                
                if ct == "metadata":
                    available_metadata = True
                if cid.startswith("references_") or "references" in st:
                    available_references = True
                    
                if expected_intent == "SUMMARY":
                    summary_aliases = SECTION_ALIASES["ABSTRACT"] + SECTION_ALIASES["INTRODUCTION"] + SECTION_ALIASES["METHOD"] + SECTION_ALIASES["RESULTS"] + SECTION_ALIASES["CONCLUSION"]
                    for a in summary_aliases:
                        if re.search(r'\b' + re.escape(a) + r'\b', st):
                            available_target_sections.add(a)
                elif expected_intent != "GENERAL" and expected_intent not in ["METADATA", "REFERENCES"]:
                    for a in expected_aliases:
                        if re.search(r'\b' + re.escape(a) + r'\b', st):
                            available_target_sections.add(a)
                            
    # Track which targeted sections we actually hit
    hit_target_sections = set()
    
    for c in retrieved_chunks:
        cid = c.get("chunk_id")
        if cid in unique_ids:
            duplicates += 1
        unique_ids.add(cid)
        
        chunk_type = str(c.get("chunk_type") or "")
        sec_title = str(c.get("section_title") or "").lower()
        cid_str = str(cid or "").lower()
        
        # Check metadata
        if chunk_type == "metadata":
            metadata_count += 1
            if expected_intent == "METADATA":
                relevant_chunks += 1
            else:
                wrong_sections += 1
            continue
            
        # Check references
        is_ref = cid_str.startswith("references_") or "references" in sec_title
        if is_ref:
            ref_count += 1
            if expected_intent == "REFERENCES":
                relevant_chunks += 1
            else:
                wrong_sections += 1
            continue
            
        if expected_intent in ["METADATA", "REFERENCES"]:
            wrong_sections += 1
            continue
            
        if expected_intent == "GENERAL":
            relevant_chunks += 1
            continue
            
        if expected_intent == "SUMMARY":
            summary_aliases = SECTION_ALIASES["ABSTRACT"] + SECTION_ALIASES["INTRODUCTION"] + SECTION_ALIASES["METHOD"] + SECTION_ALIASES["RESULTS"] + SECTION_ALIASES["CONCLUSION"]
            matched = False
            for a in summary_aliases:
                if re.search(r'\b' + re.escape(a) + r'\b', sec_title):
                    hit_target_sections.add(a)
                    matched = True
            if matched:
                relevant_chunks += 1
            else:
                wrong_sections += 1
            continue
            
        # Specific section intent
        matched = False
        for a in expected_aliases:
            if re.search(r'\b' + re.escape(a) + r'\b', sec_title):
                hit_target_sections.add(a)
                matched = True
        
        if matched:
            relevant_chunks += 1
        else:
            wrong_sections += 1
            
    # Calculate Precision
    precision = (relevant_chunks / total_chunks) * 100.0 if total_chunks else 0.0
    
    # Calculate Recall
    recall = 0.0
    if expected_intent == "GENERAL":
        recall = 100.0 if relevant_chunks > 0 else 0.0
    elif expected_intent == "METADATA":
        if available_metadata:
            recall = 100.0 if metadata_count > 0 else 0.0
        else:
            recall = 100.0 # Can't recall what doesn't exist
    elif expected_intent == "REFERENCES":
        if available_references:
            recall = 100.0 if ref_count > 0 else 0.0
        else:
            recall = 100.0
    else:
        if len(available_target_sections) > 0:
            recall = (len(hit_target_sections) / len(available_target_sections)) * 100.0
        else:
            recall = 100.0 # If paper legitimately lacks this section, recall is 100 if we didn't fail finding it
            
    # Specific metrics
    meta_precision = (metadata_count / total_chunks) * 100.0 if total_chunks else 0.0
    ref_precision = (ref_count / total_chunks) * 100.0 if total_chunks else 0.0
    
    meta_recall = 100.0 if metadata_count > 0 else (0.0 if available_metadata else 100.0)
    ref_recall = 100.0 if ref_count > 0 else (0.0 if available_references else 100.0)

    return {
        "retrieval_precision": precision,
        "retrieval_recall": recall,
        "relevant_chunk_percent": precision,
        "relevant_section_percent": precision,
        "wrong_section_percent": (wrong_sections / total_chunks) * 100.0 if total_chunks else 0.0,
        "duplicate_chunk_percent": (duplicates / total_chunks) * 100.0 if total_chunks else 0.0,
        "metadata_precision": meta_precision if expected_intent == "METADATA" else 0.0,
        "metadata_recall": meta_recall if expected_intent == "METADATA" else 0.0,
        "reference_precision": ref_precision if expected_intent == "REFERENCES" else 0.0,
        "reference_recall": ref_recall if expected_intent == "REFERENCES" else 0.0
    }

def evaluate_answer(query_info, context, answer):
    """
    Uses the local LLM to score the answer.
    """
    prompt = EVALUATOR_PROMPT.format(
        question=query_info["query"],
        context=context,
        answer=answer
    )
    
    try:
        res = generate(prompt)
        text = res.get("text", "")
        # Parse JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            scores = json.loads(json_str)
            return {
                "faithfulness": float(scores.get("faithfulness", 0.0)),
                "completeness": float(scores.get("completeness", 0.0)),
                "groundedness": float(scores.get("groundedness", 0.0)),
                "hallucination": float(scores.get("hallucination_score", 0.0)),
                "formatting": float(scores.get("formatting", 0.0)),
                "overall_quality": (float(scores.get("faithfulness", 0)) + float(scores.get("completeness", 0))) / 2.0
            }
    except Exception as e:
        print(f"LLM Eval failed: {e}")
        pass
        
    return {
        "faithfulness": 0.0,
        "completeness": 0.0,
        "groundedness": 0.0,
        "hallucination": 100.0,
        "formatting": 0.0,
        "overall_quality": 0.0
    }
