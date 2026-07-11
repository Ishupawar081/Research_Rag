"""
comparator.py
=============
Three-call comparison pipeline.

Call 1: Summarize Paper A
Call 2: Summarize Paper B
Call 3: Compare the two summaries -> final report

Session-level summary cache: if the same paper_id has already been
summarized in this process lifetime, the cached summary is reused.
"""

import time as time_mod
from time import time

from backend.rag.context_builder import build_paper_summary_context
from backend.rag.prompts import (
    build_paper_summary_prompt,
    build_summary_comparison_prompt,
)
from backend.rag.llm import generate

# ==========================================================
# SESSION SUMMARY CACHE
# ==========================================================

_summary_cache: dict[str, str] = {}


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _summarize_paper(paper_id: str, title: str, label: str, user_id: str) -> tuple[str, list, float]:
    """
    Retrieves context for a paper and generates its structured summary.

    Returns (summary_text, sources, elapsed_seconds).
    Uses a session cache to avoid re-generating.
    """
    if paper_id in _summary_cache:
        print(f"[Comparator] Cache hit for {label} ({paper_id})", flush=True)
        return _summary_cache[paper_id], [], 0.0

    print(f"\n[Comparator] Building context {label} ({title})", flush=True)
    ctx_start = time()
    context, sources = build_paper_summary_context(paper_id, user_id=user_id)
    ctx_elapsed = time() - ctx_start

    print(f"  Context length : {len(context)} chars", flush=True)
    print(f"  Chunk count    : {len(sources)}", flush=True)
    print(f"  Context time   : {ctx_elapsed:.2f}s", flush=True)

    if not context.strip():
        print(f"  WARNING: empty context for {label}", flush=True)
        return "", sources, ctx_elapsed

    prompt = build_paper_summary_prompt(context)
    print(f"  Prompt length  : {len(prompt)} chars", flush=True)

    gen_start = time()
    result = generate(prompt=prompt, is_intermediate=True)
    gen_elapsed = time() - gen_start

    print(f"  Generation time: {gen_elapsed:.2f}s", flush=True)

    if not result["success"]:
        error = result.get("error", "LLM failure")
        print(f"  ERROR: {error}", flush=True)
        summary = f"Summary unavailable ({error})"
    else:
        summary = result["answer"]
        print(f"  Summary length : {len(summary)} chars", flush=True)

    _summary_cache[paper_id] = summary
    return summary, sources, ctx_elapsed + gen_elapsed


# ==========================================================
# MAIN COMPARISON FUNCTION
# ==========================================================

def run_comparison(
    query: str,
    resolved_a: dict,
    resolved_b: dict,
    user_id: str
) -> dict:
    """
    Execute the 3-call comparison pipeline.

    Parameters
    ----------
    query      : original user question
    resolved_a : resolve_paper() result for Paper A
    resolved_b : resolve_paper() result for Paper B

    Returns
    -------
    dict with keys: answer, sources, context_length,
                    search_time, llm_time
    """
    print("\n" + "=" * 60, flush=True)
    print("[Comparator] Starting 3-call comparison pipeline", flush=True)
    print("=" * 60, flush=True)

    overall_start = time()

    # ----------------------------------------------------------
    # Call 1 – Summarise Paper A
    # ----------------------------------------------------------
    print("\n[Stage 1/3] Summarising Paper A ...", flush=True)
    summary_a, sources_a, elapsed_a = _summarize_paper(
        resolved_a["paper_id"], resolved_a["title"], "Paper A", user_id
    )

    # ----------------------------------------------------------
    # Call 2 – Summarise Paper B
    # ----------------------------------------------------------
    print("\n[Stage 2/3] Summarising Paper B ...", flush=True)
    summary_b, sources_b, elapsed_b = _summarize_paper(
        resolved_b["paper_id"], resolved_b["title"], "Paper B", user_id
    )

    # ----------------------------------------------------------
    # Call 3 – Compare the two summaries
    # ----------------------------------------------------------
    print("\n[Stage 3/3] Generating final comparison report ...", flush=True)

    final_prompt = build_summary_comparison_prompt(
        query=query,
        summary_a=summary_a,
        title_a=resolved_a["title"],
        summary_b=summary_b,
        title_b=resolved_b["title"],
    )

    print(f"  Final prompt length: {len(final_prompt)} chars", flush=True)

    cmp_start = time()
    cmp_result = generate(prompt=final_prompt, is_comparison=True)
    cmp_elapsed = time() - cmp_start

    print(f"  Final generation time: {cmp_elapsed:.2f}s", flush=True)

    total_elapsed = time() - overall_start

    print("\n" + "-" * 60, flush=True)
    print(f"[Comparator] Paper A pipeline  : {elapsed_a:.2f}s", flush=True)
    print(f"[Comparator] Paper B pipeline  : {elapsed_b:.2f}s", flush=True)
    print(f"[Comparator] Final comparison  : {cmp_elapsed:.2f}s", flush=True)
    print(f"[Comparator] Total time        : {total_elapsed:.2f}s", flush=True)
    print("-" * 60, flush=True)

    if not cmp_result["success"]:
        return {
            "success": False,
            "error": cmp_result.get("error", "Final comparison LLM failure"),
        }

    # Deduplicate sources
    all_sources = sources_a + sources_b
    unique_sources = []
    seen = set()
    for s in all_sources:
        key = (s.get("paper_id"), s.get("section"), s.get("pages"))
        if key not in seen:
            seen.add(key)
            unique_sources.append(s)

    return {
        "success": True,
        "answer": cmp_result["answer"],
        "sources": unique_sources,
        "context_length": len(summary_a) + len(summary_b),
        "search_time": elapsed_a + elapsed_b,
        "llm_time": cmp_elapsed,
    }
