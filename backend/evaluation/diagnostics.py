def diagnose_failure(metrics, config_targets, query_info):
    """
    Categorizes failures and suggests the exact module and actionable fix.
    """
    category = "Passed"
    root_cause = "N/A"
    suggested_fix = "N/A"
    module = "N/A"
    
    expected_intent = query_info.get("intent", "Unknown")
    
    if metrics["retrieval_precision"] < config_targets["retrieval_precision"]:
        if expected_intent == "METADATA":
            category = "Wrong Metadata"
            root_cause = f"Expected Metadata chunks, but retrieved standard text."
            suggested_fix = f"Add metadata intent alias for query: '{query_info.get('query')}'"
            module = "backend/rag/retriever.py"
        elif expected_intent == "REFERENCES":
            category = "Wrong References"
            root_cause = f"Expected Reference chunks, but retrieved standard text."
            suggested_fix = f"Add references intent alias for query: '{query_info.get('query')}'"
            module = "backend/rag/retriever.py"
        elif metrics["wrong_section_percent"] > 50:
            category = "Wrong Section"
            root_cause = f"Expected {expected_intent} section aliases, but retrieved irrelevant sections."
            suggested_fix = f"Add specific alias mapping for query keywords: '{query_info.get('query')}'"
            module = "backend/rag/retriever.py"
        else:
            category = "Wrong Chunk"
            root_cause = f"Semantic search pulled irrelevant chunks for intent {expected_intent}."
            suggested_fix = "Improve semantic routing or FAISS search space."
            module = "backend/rag/retriever.py"
            
    elif metrics["duplicate_chunk_percent"] > 0:
        category = "Duplicate Context"
        root_cause = "Deduplication failed to strip identical chunk IDs."
        suggested_fix = "Fix remove_duplicate_chunks logic."
        module = "backend/rag/context_builder.py"
        
    elif metrics.get("context_length", 0) > 6000:
        category = "Prompt Issue"
        root_cause = f"Context exceeded 6000 chars ({metrics.get('context_length')})."
        suggested_fix = "Adjust trim_context budgets based on intent."
        module = "backend/rag/context_builder.py"
        
    elif metrics["faithfulness"] < config_targets["faithfulness"]:
        category = "Hallucination"
        root_cause = "LLM brought in outside knowledge not present in context."
        suggested_fix = "Strengthen 'Answer ONLY using provided context' boundary in system prompt."
        module = "backend/rag/prompts.py"
        
    elif metrics["hallucination"] > config_targets["hallucination"]:
        category = "Hallucination"
        root_cause = "LLM generated unsupported claims."
        suggested_fix = "Add strict hallucination penalties to prompt instruction."
        module = "backend/rag/prompts.py"
        
    elif metrics["formatting"] < 70:
        category = "Formatting"
        root_cause = "Answer structure is poor, unreadable, or missing bullets."
        suggested_fix = "Add explicit structure requirements to prompt (e.g. 'Use markdown bullets')."
        module = "backend/rag/prompts.py"
        
    elif metrics["overall_quality"] < 50:
        category = "Wrong Answer"
        root_cause = "Relevant context provided but LLM failed to extract completeness/faithfulness."
        suggested_fix = "Reduce generation temperature or improve prompt clarity."
        module = "backend/rag/llm.py"
        
    return category, root_cause, suggested_fix, module
