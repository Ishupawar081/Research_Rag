import numpy as np
import time
import re
from collections import defaultdict

from backend.rag.loader import resources

# ==========================================================
# QUERY INTENT DETECTION
# ==========================================================

SECTION_ALIASES = {
    "METHOD": ["method", "methodology", "approach", "architecture", "model", "framework", "training", "implementation", "algorithm", "encoder", "decoder"],
    "RESULTS": ["results", "experiments", "evaluation", "performance", "metrics", "benchmarks", "quantitative results"],
    "DATASET": ["dataset", "data", "training data", "evaluation dataset", "corpus"],
    "LIMITATIONS": ["limitations", "discussion", "error analysis", "failure cases", "future work"],
    "CONCLUSION": ["conclusion", "summary", "future work", "discussion"],
    "ABSTRACT": ["abstract"],
    "INTRODUCTION": ["introduction", "background", "motivation"],
    "REFERENCES": ["references", "bibliography"]
}

def detect_query_intent(query: str):
    q = query.lower()
    
    # Bug 13: "compare methods", "compare introductions", etc. are implicitly handled below 
    # since "method" is in "compare methods". But let's be explicitly careful.
    
    metadata_kws = ["author", "authors", "email", "emails", "affiliation", "affiliations", "title", "journal", "conference", "doi", "arxiv", "keywords", "publication"]
    if any(re.search(r'\b' + re.escape(k) + r'\b', q) for k in metadata_kws):
        return "METADATA"
        
    summary_kws = ["summary", "summarize", "main idea", "key contributions", "compare contributions"]
    if any(re.search(r'\b' + re.escape(k) + r'\b', q) for k in summary_kws):
        return "SUMMARY"
        
    for intent, aliases in SECTION_ALIASES.items():
        if any(re.search(r'\b' + re.escape(a) + r'\b', q) for a in aliases):
            return intent
            
    return "GENERAL"


# ==========================================================
# DIRECT RETRIEVAL
# ==========================================================

def _format_chunk(chunk, score=1.0):
    return {
        "score": float(score),
        "paper_id": chunk.get("paper_id"),
        "chunk_id": chunk.get("chunk_id"),
        "paper_title": chunk.get("paper_title"),
        "section_number": chunk.get("section_number"),
        "section_title": chunk.get("section_title"),
        "page_start": chunk.get("page_start"),
        "page_end": chunk.get("page_end"),
        "chunk_type": chunk.get("chunk_type"),
        "text": chunk.get("text"),
        "chunk": chunk
    }

def _direct_retrieval(intent: str, paper_id: str | None = None, max_chunks_per_paper: int | None = None, user_id: str = None):
    results = []
    
    # For SUMMARY, we want them in exact order.
    # Abstract -> Intro -> Method -> Results -> Conclusion
    
    if intent == "SUMMARY":
        summary_sections = ["ABSTRACT", "INTRODUCTION", "METHOD", "RESULTS", "CONCLUSION"]
        for sec in summary_sections:
            sec_results = []
            seen_chunks = set()
            for meta in resources.get_metadata(user_id):
                pid = meta["paper_id"]
                if paper_id and pid != paper_id:
                    continue
                
                chunk_key = (pid, meta["chunk_id"])
                if chunk_key in seen_chunks:
                    continue
                
                chunk = resources.get_chunk(user_id, pid, meta["chunk_id"])
                if not chunk:
                    continue
                
                seen_chunks.add(chunk_key)
                
                sec_title = str(chunk.get("section_title") or "").lower()
                if any(a in sec_title for a in SECTION_ALIASES[sec]):
                    sec_results.append(_format_chunk(chunk, score=1.0))
                    
                    if len(sec_results) >= 2: # At most 2 chunks per section for SUMMARY
                        break
                        
            results.extend(sec_results)
        return results

    paper_counts = defaultdict(int)
    target_aliases = []
    if intent in SECTION_ALIASES:
        target_aliases = SECTION_ALIASES[intent]
        
    seen_chunks = set()
    
    for meta in resources.get_metadata(user_id):
        pid = meta["paper_id"]
        if paper_id and pid != paper_id:
            continue
            
        chunk_key = (pid, meta["chunk_id"])
        if chunk_key in seen_chunks:
            continue
            
        chunk = resources.get_chunk(user_id, pid, meta["chunk_id"])
        if not chunk:
            continue
            
        seen_chunks.add(chunk_key)
        
        match = False
        if intent == "METADATA":
            if chunk.get("chunk_type") == "metadata":
                match = True
        else:
            sec_title = str(chunk.get("section_title") or "").lower()
            chunk_id_str = str(chunk.get("chunk_id") or "").lower()
            if intent == "REFERENCES" and chunk_id_str.startswith("references_"):
                match = True
            elif any(a in sec_title for a in target_aliases):
                match = True
                
        if match:
            if max_chunks_per_paper and paper_counts[pid] >= max_chunks_per_paper:
                continue
            results.append(_format_chunk(chunk, score=1.0))
            paper_counts[pid] += 1
            
    return results

# ==========================================================
# QUERY EMBEDDING
# ==========================================================

def embed_query(query: str):
    print("=================================================", flush=True)
    print("ENTER embed_query", flush=True)
    print("=================================================", flush=True)
    start = time.perf_counter()

    embedding = resources.model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    end = time.perf_counter()
    print("Function: embed_query", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT embed_query", flush=True)
    print("=================================================", flush=True)
    return embedding.astype("float32")


# ==========================================================
# INTERNAL SEARCH HELPER
# ==========================================================

def _fetch_candidates(query: str, search_size: int, paper_id: str | None = None, user_id: str = None):
    """
    Core FAISS search and result formatting.
    Yields retrieved chunks one by one in similarity order.
    """
    print("=================================================", flush=True)
    print("ENTER _fetch_candidates", flush=True)
    print("=================================================", flush=True)
    print("Before embedding query", flush=True)
    query_embedding = embed_query(query)
    print("After embedding query", flush=True)
    
    query_embedding = np.expand_dims(
        query_embedding,
        axis=0
    )

    search_size = min(
        search_size,
        resources.get_index(user_id).ntotal
    )

    print("Before FAISS search", flush=True)
    scores, indices = resources.get_index(user_id).search(
        query_embedding,
        search_size
    )
    print("After FAISS search", flush=True)
    print(f"Number of indices returned: {len(indices[0])}", flush=True)

    seen = set()

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        meta = resources.get_metadata(user_id)[idx]
        print(f"Loaded metadata item: {meta}", flush=True)

        if paper_id is not None and meta["paper_id"] != paper_id:
            continue

        chunk_key = (meta["paper_id"], meta["chunk_id"])
        if chunk_key in seen:
            continue
        seen.add(chunk_key)

        print(f"Loading chunk_id {meta['chunk_id']} from chunk file for paper {meta['paper_id']}", flush=True)
        chunk = resources.get_chunk(
            user_id,
            meta["paper_id"],
            meta["chunk_id"]
        )

        if chunk is None:
            print(f"WARNING: Chunk cannot be found for {meta['paper_id']} {meta['chunk_id']}", flush=True)
            continue

        yield _format_chunk(chunk, score=min(float(score), 1.0))


# ==========================================================
# SEARCH (EXISTING)
# ==========================================================

def search(
    query: str,
    top_k: int = 5,
    paper_id: str | None = None,
    user_id: str = None
):
    """
    Existing search strategy. Returns top_k nearest chunks.
    """
    print("=================================================", flush=True)
    print("ENTER search", flush=True)
    print("=================================================", flush=True)
    start = time.perf_counter()
    
    intent = detect_query_intent(query)
    print(f"Intent: {intent}", flush=True)
    
    # BUG 3 & BUG 12: If direct retrieval finds 0 chunks, fallback to semantic search
    fallback_triggered = False
    
    if intent != "GENERAL":
        results = _direct_retrieval(intent, paper_id, max_chunks_per_paper=top_k, user_id=user_id)
        
        # Do not fallback if a specific intent was detected to avoid contaminating results.
        # e.g., if intent is METHOD, but the paper has no methods section, we want to return 0 chunks 
        # so the LLM explicitly states there is no method, rather than hallucinating from evaluation chunks.
        print(f"Retrieval Mode: DIRECT ({intent})", flush=True)
        print(f"Chunks Before Filtering: {len(results)}", flush=True)
        sections = set(r.get("section_title") for r in results)
        print(f"Matched Sections: {list(sections)}", flush=True)
        
        end = time.perf_counter()
        print("Function: search", flush=True)
        print(f"Execution time: {end - start:.4f}s", flush=True)
        print("=================================================", flush=True)
        print("EXIT search", flush=True)
        print("=================================================", flush=True)
        return results
            
    print("Retrieval Mode: SEMANTIC", flush=True)
    
    search_size = max(top_k * 10, 50)
    
    results = []
    
    for candidate in _fetch_candidates(query, search_size, paper_id, user_id):
        results.append(candidate)
        if len(results) >= top_k:
            break
            
    print(f"Chunks Before Filtering: {len(results)}", flush=True)
    sections = set(r.get("section_title") for r in results)
    print(f"Matched Sections: {list(sections)}", flush=True)
    if fallback_triggered:
        print("Fallback Triggered: True", flush=True)
            
    end = time.perf_counter()
    print("Function: search", flush=True)
    print(f"query: {query}", flush=True)
    print(f"paper_id: {paper_id}", flush=True)
    print(f"retrieved chunk count: {len(results)}", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT search", flush=True)
    print("=================================================", flush=True)
    return results


# ==========================================================
# SEARCH DIVERSE (NEW)
# ==========================================================

def search_diverse(
    query: str,
    top_k: int = 10,
    max_chunks_per_paper: int = 2,
    user_id: str = None
):
    """
    Semantic search ensuring diversity across multiple papers.
    """
    print("=================================================", flush=True)
    print("ENTER search_diverse", flush=True)
    print("=================================================", flush=True)
    start = time.perf_counter()
    
    intent = detect_query_intent(query)
    print(f"Intent: {intent}", flush=True)
    
    diverse_results = []
    
    registry = resources.get_registry(user_id)
    
    for paper in registry:
        pid = paper.get("paper_id")
        if not pid:
            continue
            
        paper_results = search(
            query=query, 
            top_k=max_chunks_per_paper, 
            paper_id=pid, 
            user_id=user_id
        )
        diverse_results.extend(paper_results)
        
    print(f"Chunks Before Filtering: {len(diverse_results)}", flush=True)
    sections = set(r.get("section_title") for r in diverse_results)
    print(f"Matched Sections: {list(sections)}", flush=True)
            
    end = time.perf_counter()
    print("Function: search_diverse", flush=True)
    print(f"query: {query}", flush=True)
    print(f"retrieved chunk count: {len(diverse_results)}", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT search_diverse", flush=True)
    print("=================================================", flush=True)
    return diverse_results

# ==========================================================
# SEARCH COMPARISON (NEW)
# ==========================================================

def search_comparison(
    paper_id: str,
    top_k: int = 100,
    user_id: str = None
):
    """
    Comparison mode specific retrieval.
    Retrieves almost the entire contents of a paper, excluding low-value sections.
    """
    print("=================================================", flush=True)
    print("ENTER search_comparison", flush=True)
    print("=================================================", flush=True)
    start = time.perf_counter()
    
    results = []
    seen_chunks = set()
    
    for meta in resources.get_metadata(user_id):
        if meta["paper_id"] != paper_id:
            continue
            
        chunk_key = (meta["paper_id"], meta["chunk_id"])
        if chunk_key in seen_chunks:
            continue
            
        chunk = resources.get_chunk(user_id, meta["paper_id"], meta["chunk_id"])
        if not chunk:
            continue
            
        seen_chunks.add(chunk_key)
        
        chunk_type = str(chunk.get("chunk_type") or "").lower()
        sec_title = str(chunk.get("section_title") or "").lower()
        chunk_id_str = str(chunk.get("chunk_id") or "").lower()
        
        # Filter out unwanted sections
        if chunk_type == "metadata":
            continue
        if chunk_id_str.startswith("references_"):
            continue
        if any(skip in sec_title for skip in ["references", "bibliography", "acknowledgement", "acknowledgment", "appendix"]):
            continue
            
        results.append(_format_chunk(chunk, score=1.0))
        
        if len(results) >= top_k:
            break
            
    end = time.perf_counter()
    print("Function: search_comparison", flush=True)
    print(f"paper_id: {paper_id}", flush=True)
    print(f"retrieved chunk count: {len(results)}", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT search_comparison", flush=True)
    print("=================================================", flush=True)
    
    return results

# ==========================================================
# RETRIEVE SECTION (NEW)
# ==========================================================

def retrieve_section(paper_id: str, section_aliases: list, top_k: int = 6, user_id: str = None):
    """
    Retrieves chunks belonging to a specific section for comparison.
    """
    print("=================================================", flush=True)
    print(f"ENTER retrieve_section (Aliases: {section_aliases})", flush=True)
    print("=================================================", flush=True)
    start = time.perf_counter()
    
    results = []
    seen_chunks = set()
    
    for meta in resources.get_metadata(user_id):
        if meta["paper_id"] != paper_id:
            continue
            
        chunk_key = (meta["paper_id"], meta["chunk_id"])
        if chunk_key in seen_chunks:
            continue
            
        chunk = resources.get_chunk(user_id, meta["paper_id"], meta["chunk_id"])
        if not chunk:
            continue
            
        seen_chunks.add(chunk_key)
        
        chunk_type = str(chunk.get("chunk_type") or "").lower()
        sec_title = str(chunk.get("section_title") or "").lower()
        chunk_id_str = str(chunk.get("chunk_id") or "").lower()
        
        if chunk_type == "metadata":
            continue
        if chunk_id_str.startswith("references_"):
            continue
        if any(skip in sec_title for skip in ["references", "bibliography", "acknowledgement", "acknowledgment"]):
            continue
            
        # Match against aliases
        if not any(alias in sec_title for alias in section_aliases):
            continue
            
        results.append(_format_chunk(chunk, score=1.0))
        
        if len(results) >= top_k:
            break
            
    end = time.perf_counter()
    print("Function: retrieve_section", flush=True)
    print(f"paper_id: {paper_id}", flush=True)
    print(f"retrieved chunk count: {len(results)}", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT retrieve_section", flush=True)
    print("=================================================", flush=True)
    
    return results