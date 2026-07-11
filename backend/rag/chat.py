import time as time_mod
from time import time

from backend.rag.retriever import search, search_diverse, retrieve_section
from backend.rag.context_builder import prepare_context, prepare_specific_comparison_context, build_paper_summary_context
from backend.rag.prompts import (
    get_prompt,
    build_stage_prompt,
    build_final_comparison_prompt,
    build_paper_summary_prompt,
    METHOD_COMPARISON_PROMPT,
    DATASET_COMPARISON_PROMPT,
    EXPERIMENT_COMPARISON_PROMPT,
    RESULT_COMPARISON_PROMPT,
    ADVANTAGE_COMPARISON_PROMPT,
    CONCLUSION_COMPARISON_PROMPT
)
from backend.rag.llm import generate
from backend.rag.resolver import resolve_paper
from backend.rag.comparator import run_comparison

# ==========================================================
# HELPERS
# ==========================================================

def _error(mode: str, message: str):

    return {

        "success": False,

        "mode": mode,

        "error": message

    }


def _success(
    mode,
    query,
    answer,
    sources,
    papers,
    search_time,
    llm_time,
    context_length,
    context=None,
    prompt=None,
    raw_chunks=None
):

    return {

        "success": True,

        "mode": mode,

        "query": query,

        "answer": answer,

        "sources": sources,

        "papers": papers,
        
        "retrieval_count": len(sources),
        
        "context_length": context_length,

        "search_time": round(search_time, 3),
        
        "llm_time": round(llm_time, 3),
        
        "context": context,
        
        "prompt": prompt,
        
        "raw_chunks": raw_chunks

    }


# ==========================================================
# SUMMARY INTENT DETECTION
# ==========================================================

_SUMMARY_KEYWORDS = {
    "summary", "summarize", "summarise", "summarization", "summarisation",
    "overview", "brief", "tldr", "tl;dr",
    "explain the paper", "explain this paper",
    "paper summary", "paper overview", "brief summary", "brief overview",
    "give me a summary", "give a summary", "give an overview",
    "summarize this paper", "summarise this paper",
    "summarize the paper", "summarise the paper",
    "what is this paper about", "what is the paper about",
    "what does this paper do", "what does the paper do",
    "what is this paper", "explain paper", "paper explained",
    "in brief", "in short",
}

def is_summary_query(query: str) -> bool:
    """
    Return True when the user's query is requesting a paper summary
    rather than a specific factual question.

    Checks:
    - Exact or substring match against _SUMMARY_KEYWORDS (case-insensitive)
    - Query is short (≤ 8 words) and contains a summary-related word
    """
    q = query.strip().lower()
    # Remove trailing punctuation for cleaner matching
    q_clean = q.rstrip("?.!")

    # Exact match
    if q_clean in _SUMMARY_KEYWORDS:
        return True

    # Substring match — catches "can you summarize this paper", etc.
    for kw in _SUMMARY_KEYWORDS:
        if kw in q_clean:
            return True

    return False


# ==========================================================
# GENERAL COMPARE INTENT DETECTION
# ==========================================================

_GENERAL_COMPARE_KEYWORDS = {
    "compare", "comparison", "compare them", "compare these",
    "compare these papers", "compare the papers",
    "give me a comparison", "what are the differences",
    "how do they compare", "compare paper", "paper comparison",
    "summarize comparison", "compare both"
}

_SPECIFIC_COMPARE_KEYWORDS = {
    "abstract", "introduction", "dataset", "data", "result",
    "method", "experiment", "architecture", "conclusion",
    "future work", "contribution", "metric", "evaluation",
    "limitation", "difference in", "performance"
}

def is_general_compare_query(query: str) -> bool:
    """
    Return True when the user's query is asking for a general comparison
    rather than a specific factual comparison (e.g. 'compare datasets').
    """
    q = query.strip().lower().rstrip("?.!")
    
    # If the user mentions specific topics, it is NOT a general comparison
    for kw in _SPECIFIC_COMPARE_KEYWORDS:
        if kw in q:
            return False
            
    # Exact match with general comparison phrases
    if q in _GENERAL_COMPARE_KEYWORDS:
        return True
        
    # Short query containing 'compare' or 'difference' without specific topics
    words = q.split()
    if ("compare" in q or "difference" in q) and len(words) <= 8:
        return True
        
    return False

# ==========================================================
# SINGLE PAPER CHAT
# ===========================================================

def single_paper_chat(

    query: str,

    paper: str,

    top_k: int = 8,
    
    user_id: str = None,

    history=None

):
    """
    Chat with a single research paper.

    Parameters
    ----------
    query : user question

    paper : paper id / title

    top_k : retrieved chunks

    history : reserved for future conversation memory
    """

    print("=================================================", flush=True)
    print("ENTER single_paper_chat", flush=True)
    print("=================================================", flush=True)
    
    start_perf = time_mod.perf_counter()
    start = time()

    if history is None:
        history = []

    # ------------------------------------------------------
    # Resolve Paper
    # ------------------------------------------------------

    resolved = resolve_paper(paper, user_id=user_id)

    if resolved is None:

        return _error(

            "single",

            f"Paper '{paper}' not found."

        )

    if resolved.get("is_ambiguous"):

        return _error(

            "single",

            f"Ambiguous query '{paper}'. Multiple matches found via {resolved.get('strategy')}."

        )

    paper_id = resolved["paper_id"]

    # ----------------------------------------------------------
    # Build shared paper_info (used in both paths)
    # ----------------------------------------------------------
    paper_info = {
        "paper_id":    resolved["paper_id"],
        "title":       resolved["title"],
        "authors":     resolved.get("authors", []),
        "keywords":    resolved.get("keywords", []),
        "num_sections": resolved.get("num_sections"),
        "num_chunks":  resolved.get("num_chunks"),
    }

    # ----------------------------------------------------------
    # Path 2 — Summary: bypass FAISS, use full-paper context
    # ----------------------------------------------------------
    if is_summary_query(query):
        print("[single_paper_chat] Summary intent detected — using full-paper context.", flush=True)

        ctx_start = time()
        context, sources = build_paper_summary_context(paper_id, user_id=user_id)
        search_time = time() - ctx_start

        print(f"[single_paper_chat] Summary context: {len(context)} chars, {len(sources)} sources", flush=True)

        if not context.strip():
            return _error("single", "Could not build paper context for summary.")

        prompt = build_paper_summary_prompt(context)

        llm_start = time()
        result = generate(prompt=prompt, is_intermediate=True)
        llm_time = time() - llm_start

        if not result["success"]:
            return _error("single", result["error"])

        end_perf = time_mod.perf_counter()
        print(f"[single_paper_chat] Summary generated in {end_perf - start_perf:.2f}s", flush=True)

        return _success(
            mode="single",
            query=query,
            answer=result["answer"],
            sources=sources,
            papers=[paper_info],
            search_time=search_time,
            llm_time=llm_time,
            context_length=len(context)
        )

    # ----------------------------------------------------------
    # Path 1 — Normal QA: semantic retrieval
    # ----------------------------------------------------------

    # ------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------

    retrieved = search(
        query=query,
        paper_id=paper_id,
        top_k=top_k,
        user_id=user_id
    )

    if len(retrieved) == 0:

        return _error(

            "single",

            "No relevant information found."

        )

    # ------------------------------------------------------
    # Build Context
    # ------------------------------------------------------

    package = prepare_context(
        query,
        retrieved,
        user_id=user_id
    )

    context = package["context"]

    sources = package["sources"]

    # ------------------------------------------------------
    # Prompt
    # ------------------------------------------------------

    prompt = get_prompt(

        mode="single",

        query=query,

        context=context

    )

    search_time = time() - start

    # ------------------------------------------------------
    # LLM
    # ------------------------------------------------------
    
    llm_start = time()

    print("STEP 1 : Retrieval finished", flush=True)

    print("Context characters:", len(context), flush=True)

    print("Prompt characters:", len(prompt), flush=True)

    print("Calling Ollama...", flush=True)

    if not prompt.strip() or not context.strip():
        return _error(
            "single",
            "Missing Context: Prompt or Context is empty."
        )

    result = generate(prompt=prompt)

    print("Returned from Ollama", flush=True)

    print(result, flush=True)
    
    print("\n" + "="*80)
    print("SINGLE PAPER DEBUG")
    print("="*80)

    print("Paper:", resolved["title"])
    print("Retrieved chunks:", len(retrieved))
    print("Context length:", len(context))
    print("Prompt length:", len(prompt))
    print("Approx prompt tokens:", len(prompt.split()))

    print("\nChunk sizes:")
    for i, c in enumerate(retrieved):
        print(
            i + 1,
            c["paper_id"],
            c["chunk_id"],
            len(c["text"])
        )

    print("="*80)

    if not result["success"]:

        return _error(

            "single",

            result["error"]

        )

    # ------------------------------------------------------
    # Paper Information
    # ------------------------------------------------------

    paper_info = {

        "paper_id":

            resolved["paper_id"],

        "title":

            resolved["title"],

        "authors":

            resolved.get(

                "authors",

                []

            ),

        "keywords":

            resolved.get(

                "keywords",

                []

            ),

        "num_sections":

            resolved.get(

                "num_sections"

            ),

        "num_chunks":

            resolved.get(

                "num_chunks"

            )

    }

    llm_time = time() - llm_start

    end_perf = time_mod.perf_counter()
    print(f"Function: single_paper_chat", flush=True)
    print(f"Execution time: {end_perf - start_perf:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT single_paper_chat", flush=True)
    print("=================================================", flush=True)

    return _success(

        mode="single",

        query=query,

        answer=result["answer"],

        sources=sources,

        papers=[paper_info],

        search_time=search_time,
        
        llm_time=llm_time,
        
        context_length=len(context)

    )

# ==========================================================
# COLLECTION CHAT
# ==========================================================

def collection_chat(

    query: str,

    top_k: int = 10,
    
    user_id: str = None,

    history=None

):
    """
    Chat across the entire paper collection.

    Parameters
    ----------
    query : user question

    top_k : retrieved chunks

    history : reserved for future conversation memory
    """

    print("=================================================", flush=True)
    print("ENTER collection_chat", flush=True)
    print("=================================================", flush=True)
    start_perf = time_mod.perf_counter()
    start = time()

    if history is None:
        history = []

    # ------------------------------------------------------
    # Retrieve from all papers
    # ------------------------------------------------------

    retrieved = search_diverse(
        query=query,
        top_k=top_k,
        user_id=user_id
    )

    if len(retrieved) == 0:

        return _error(

            "collection",

            "No relevant information found."

        )

    # ------------------------------------------------------
    # Build Context
    # ------------------------------------------------------

    package = prepare_context(
        query,
        retrieved,
        user_id=user_id
    )

    semantic_context = package["context"]
    sources = package["sources"]
    chunks = package["chunks"]

    # Load registry
    from backend.rag.loader import ResourceLoader
    registry = ResourceLoader().get_registry(user_id)
    
    catalog_lines = ["\n[PAPER REGISTRY OVERVIEW]"]
    catalog_lines.append("Here is the list of all papers currently in the database. Use this to answer queries about what papers exist:")
    for p in registry:
        title = p.get('title', 'Unknown')
        pid = p.get('paper_id', 'Unknown')
        authors = ", ".join(p.get('authors', []))
        catalog_lines.append(f"- ID: {pid} | Title: {title} | Authors: {authors}")
        
    registry_context = "\n".join(catalog_lines) + "\n\n"
    
    context = registry_context + semantic_context

    # ------------------------------------------------------
    # Prompt
    # ------------------------------------------------------

    prompt = get_prompt(

        mode="collection",

        query=query,

        context=context

    )

    search_time = time() - start

    # ------------------------------------------------------
    # LLM
    # ------------------------------------------------------
    
    llm_start = time()

    result = generate(

        prompt=prompt

    )

    if not result["success"]:

        return _error(

            "collection",

            result.get("error", "LLM failure")

        )

    # ------------------------------------------------------
    # Papers Used
    # ------------------------------------------------------

    papers = {}

    for chunk in chunks:

        pid = chunk["paper_id"]

        if pid in papers:
            continue

        papers[pid] = {

            "paper_id": pid,

            "title": chunk["paper_title"]

        }

    llm_time = time() - llm_start

    end_perf = time_mod.perf_counter()
    print(f"Function: collection_chat", flush=True)
    print(f"Execution time: {end_perf - start_perf:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT collection_chat", flush=True)
    print("=================================================", flush=True)

    return _success(

        mode="collection",

        query=query,

        answer=result["answer"],

        sources=sources,

        papers=list(papers.values()),

        search_time=search_time,
        
        llm_time=llm_time,
        
        context_length=len(context)

    )

# ==========================================================
# COMPARE TWO PAPERS
# ==========================================================

def compare_papers(
    query: str,
    paper_a: str,
    paper_b: str,
    top_k: int = 6,
    user_id: str = None,
    history=None
):
    print("=================================================", flush=True)
    print("ENTER compare_papers (3-call comparator)", flush=True)
    print("=================================================", flush=True)
    start_perf = time_mod.perf_counter()
    start = time()

    if history is None:
        history = []

    # ------------------------------------------------------
    # Resolve Papers
    # ------------------------------------------------------
    resolved_a = resolve_paper(paper_a, user_id=user_id)
    resolved_b = resolve_paper(paper_b, user_id=user_id)

    if resolved_a is None:
        return _error("compare", f"Paper '{paper_a}' not found.")
    if resolved_a.get("is_ambiguous"):
        return _error("compare", f"Ambiguous query '{paper_a}'. Multiple matches found.")
    if resolved_b is None:
        return _error("compare", f"Paper '{paper_b}' not found.")
    if resolved_b.get("is_ambiguous"):
        return _error("compare", f"Ambiguous query '{paper_b}'. Multiple matches found.")
    if resolved_a["paper_id"] == resolved_b["paper_id"]:
        return _error("compare", "Cannot compare a paper to itself. Please select two different papers.")

    papers = [
        {
            "paper_id": resolved_a["paper_id"],
            "title": resolved_a["title"],
            "authors": resolved_a.get("authors", []),
            "keywords": resolved_a.get("keywords", [])
        },
        {
            "paper_id": resolved_b["paper_id"],
            "title": resolved_b["title"],
            "authors": resolved_b.get("authors", []),
            "keywords": resolved_b.get("keywords", [])
        }
    ]

    # ------------------------------------------------------
    # Path 1: General Comparison (3-call pipeline)
    # ------------------------------------------------------
    if is_general_compare_query(query):
        print("[compare_papers] General comparison intent detected — using 3-call comparator.", flush=True)
        cmp = run_comparison(query=query, resolved_a=resolved_a, resolved_b=resolved_b, user_id=user_id)

        if not cmp["success"]:
            return _error("compare", cmp.get("error", "Comparison failed."))

        end_perf = time_mod.perf_counter()
        print(f"Function: compare_papers", flush=True)
        print(f"Execution time: {end_perf - start_perf:.4f}s", flush=True)
        print("=================================================", flush=True)
        print("EXIT compare_papers", flush=True)
        print("=================================================", flush=True)

        return _success(
            mode="compare",
            query=query,
            answer=cmp["answer"],
            sources=cmp["sources"],
            papers=papers,
            search_time=cmp["search_time"],
            llm_time=cmp["llm_time"],
            context_length=cmp["context_length"]
        )

    # ------------------------------------------------------
    # Path 2: Specific Comparison (QA semantic retrieval)
    # ------------------------------------------------------
    print("[compare_papers] Specific comparison intent detected — using semantic retrieval.", flush=True)
    
    # Retrieve relevant chunks for both papers
    retrieved_a = search(query=query, top_k=top_k, paper_id=resolved_a["paper_id"], user_id=user_id)
    retrieved_b = search(query=query, top_k=top_k, paper_id=resolved_b["paper_id"], user_id=user_id)
    
    combined_retrieved = retrieved_a + retrieved_b
    
    if len(combined_retrieved) == 0:
        return _error("compare", "No relevant information found in either paper to answer this question.")
        
    # Build context from combined chunks with specific comparison logic
    package = prepare_specific_comparison_context(
        query, 
        resolved_a["title"], retrieved_a, 
        resolved_b["title"], retrieved_b, 
        user_id=user_id
    )
    context = package["context"]
    sources = package["sources"]
    
    prompt = get_prompt(mode="compare_specific", query=query, context=context)
    search_time = time() - start
    
    print(f"[compare_papers] Retrieved {len(combined_retrieved)} chunks, Context length: {len(context)}", flush=True)
    
    llm_start = time()
    result = generate(prompt=prompt)
    llm_time = time() - llm_start
    
    if not result["success"]:
        return _error("compare", result["error"])

    end_perf = time_mod.perf_counter()
    print(f"Function: compare_papers", flush=True)
    print(f"Execution time: {end_perf - start_perf:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT compare_papers", flush=True)
    print("=================================================", flush=True)

    return _success(
        mode="compare",
        query=query,
        answer=result["answer"],
        sources=sources,
        papers=papers,
        search_time=search_time,
        llm_time=llm_time,
        context_length=len(context)
    )

# ==========================================================
# TEST
# ==========================================================

# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    # ======================================================
    # SINGLE PAPER CHAT
    # ======================================================

    print("\n" + "=" * 100)
    print("SINGLE PAPER CHAT")
    print("=" * 100)

    response = single_paper_chat(

        query="Explain the variation field.",

        paper="2212.00190v2"

    )

    if response["success"]:

        print("\nPaper:")
        print(response["papers"][0]["title"])

        print("\nAnswer:\n")
        print(response["answer"])

        print("\nSources:\n")

        for s in response["sources"]:

            print(
                f"{s['section_number']} | "
                f"{s['section_title']} | "
                f"Score: {s['score']:.4f}"
            )

    else:

        print(response["error"])


    # ======================================================
    # COLLECTION CHAT
    # ======================================================

    print("\n" + "=" * 100)
    print("COLLECTION CHAT")
    print("=" * 100)

    response = collection_chat(

        query="Which papers use transformers?"

    )

    if response["success"]:

        print("\nPapers Retrieved:\n")

        for p in response["papers"]:

            print("-", p["title"])

        print("\nAnswer:\n")
        print(response["answer"])

        print("\nSources:\n")

        for s in response["sources"]:

            print(
                f"{s['paper_title']} | "
                f"{s['section_title']} | "
                f"Score: {s['score']:.4f}"
            )

    else:

        print(response["error"])


    # ======================================================
    # COMPARE PAPERS
    # ======================================================

    print("\n" + "=" * 100)
    print("COMPARE PAPERS")
    print("=" * 100)

    response = compare_papers(

        query="Compare the methodology used in these papers.",

        paper_a="2212.00190v2",

        paper_b="2212.00235v1"

    )

    if response["success"]:

        print("\nPaper A:")
        print(response["papers"][0]["title"])

        print("\nPaper B:")
        print(response["papers"][1]["title"])

        print("\nComparison:\n")
        print(response["answer"])

        print("\nSources:\n")

        for s in response["sources"]:

            print(
                f"{s['paper_title']} | "
                f"{s['section_title']} | "
                f"Score: {s['score']:.4f}"
            )

    else:

        print(response["error"])