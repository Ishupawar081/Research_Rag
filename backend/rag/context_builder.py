from collections import OrderedDict
import re

# Import intent detection
from backend.rag.retriever import detect_query_intent, SECTION_ALIASES

# ==========================================================
# CONFIG
# ==========================================================

MAX_CHARACTERS = 8000

MAX_CHUNKS = 10

MAX_CHUNKS_PER_SECTION = 4

MAX_SECTION_PERCENTAGE = 0.60

# ==========================================================
# REMOVE DUPLICATES
# ==========================================================

def remove_duplicate_chunks(results):
    """
    Remove duplicate chunk ids while preserving order.
    Bug 8: Only identical chunk_ids are removed.
    """
    seen = set()
    unique = []
    for r in results:
        key = (r["paper_id"], r["chunk_id"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    return unique


# ==========================================================
# SORT RESULTS
# ==========================================================

def sort_results(results):
    """
    Sort by
    1. adjusted_score or similarity score (descending)
    2. page number (ascending)
    """
    return sorted(
        results,
        key=lambda x: (
            -x.get("adjusted_score", x["score"]),
            x.get("page_start", 99999)
        )
    )


# ==========================================================
# LIMIT NUMBER OF CHUNKS
# ==========================================================

def limit_chunks(results):
    return results[:MAX_CHUNKS]


# ==========================================================
# LIMIT CONTEXT SIZE
# ==========================================================

def trim_context(results, intent):
    """
    Stop once maximum character budget is reached.
    Ensure no section occupies more than MAX_SECTION_PERCENTAGE of the final budget.
    """
    # Bug 6: Dynamic Budgets
    budget = 4000
    if intent == "METHOD":
        budget = 3000
    elif intent == "INTRODUCTION":
        budget = 2500
        
    # Bug 5 & 7: 2-Pass trimming algorithm
    required_aliases = []
    if intent == "SUMMARY":
        required_aliases = [
            SECTION_ALIASES["ABSTRACT"], 
            SECTION_ALIASES["INTRODUCTION"], 
            SECTION_ALIASES["METHOD"], 
            SECTION_ALIASES["RESULTS"], 
            SECTION_ALIASES["CONCLUSION"]
        ]
    elif intent in SECTION_ALIASES:
        required_aliases = [SECTION_ALIASES[intent]]
        
    context = []
    total = 0
    max_section_chars = int(budget * MAX_SECTION_PERCENTAGE)
    
    used_chunks = set()
    
    # Pass 1: Grab 1 representative chunk for each required section
    for req in required_aliases:
        for r in results:
            if id(r) in used_chunks:
                continue
            sec_title = str(r.get("section_title") or "").lower()
            if any(a in sec_title for a in req):
                length = len(r.get("text", ""))
                if total + length <= budget:
                    context.append(r)
                    total += length
                    used_chunks.add(id(r))
                    break # Move to next requirement
                    
    # Pass 2: Fill remaining by priority score
    for r in results:
        if id(r) in used_chunks:
            continue
            
        text = r.get("text", "")
        length = len(text)

        if total + length > budget:
            continue

        key = (r.get("paper_id"), r.get("section_number"))
        if key[1] is not None:
            # Compute current section usage dynamically
            sec_total = sum(len(c.get("text", "")) for c in context if (c.get("paper_id"), c.get("section_number")) == key)
            if sec_total + length > max_section_chars:
                continue

        context.append(r)
        total += length

    # Bug 1: Guarantee len >= 1
    if len(context) == 0 and len(results) > 0:
        context.append(results[0])

    # Important: context order here is Pass1 then Pass2.
    # We should re-sort them chronologically at the end anyway, so this is fine.
    return context


# ==========================================================
# LIMIT CHUNKS PER SECTION (NEW)
# ==========================================================

def limit_chunks_per_section(results, intent):
    """
    Limit the number of chunks from the same section to ensure context diversity.
    """
    # Bug 9: Dynamic section limits
    limits = {}
    if intent == "SUMMARY":
        limits = {"abstract": 1, "introduction": 2, "method": 2, "results": 2, "conclusion": 1}
    elif intent == "METHOD":
        limits = {"method": 3, "implementation": 2, "architecture": 2}
        
    section_chunks = {}
    diverse_results = []
    
    for r in results:
        key = (r.get("paper_id"), r.get("section_number"))
        if key[1] is None:
            diverse_results.append(r)
            continue
            
        sec_title = str(r.get("section_title") or "").lower()
        limit = MAX_CHUNKS_PER_SECTION
        
        # Apply specific limits if they exist
        if limits:
            for l_key, l_val in limits.items():
                if l_key in sec_title:
                    limit = l_val
                    break
            
        chunks = section_chunks.get(key, [])
        if len(chunks) >= limit:
            continue
            
        chunks.append(r)
        section_chunks[key] = chunks
        diverse_results.append(r)
            
    return diverse_results

# ==========================================================
# SORT CHRONOLOGICAL (NEW)
# ==========================================================

def sort_chronological(results):
    """
    Sort chunks logically by paper ID and page number so the LLM reads them sequentially.
    """
    return sorted(
        results,
        key=lambda x: (
            x.get("paper_id", ""),
            x.get("page_start", 99999)
        )
    )


# ==========================================================
# BUILD SOURCES
# ==========================================================

def build_sources(results):
    """
    Build source list for UI.

    Returned separately from LLM context.
    """

    sources = []

    for r in results:

        sources.append({

            "paper_id":

                r["paper_id"],

            "paper_title":

                r["paper_title"],

            "chunk_id":

                r["chunk_id"],

            "section_number":

                r["section_number"],

            "section_title":

                r["section_title"],

            "page_start":

                r["page_start"],

            "page_end":

                r["page_end"],

            "score":

                round(r["score"],4)

        })

    return sources


# ==========================================================
# RETRIEVAL POLICIES
# ==========================================================

def apply_retrieval_policies(query: str, results: list, intent: str):
    """
    Filters and scores chunks based on the user's query intent.
    """
    query_lower = query.lower()
    
    metadata_kws = [
        "title", "author", "authors", "affiliation", "affiliations", "institution", "organization", 
        "email", "emails", "corresponding author", "keywords", "conference", "journal", "doi", "arxiv", "publication"
    ]
    has_metadata = intent == "METADATA" or any(re.search(r'\b' + re.escape(k) + r'\b', query_lower) for k in metadata_kws)
    
    has_reference = intent == "REFERENCES" or any(k in query_lower for k in [
        "reference", "references", "citation", "citations", "bibliography", "related work", 
        "prior work", "cited by", "paper cites", "which papers are cited", "what papers does this work reference"
    ])
    
    has_summary = intent == "SUMMARY"
    has_abstract = intent == "ABSTRACT" or "abstract" in query_lower
    has_introduction = intent == "INTRODUCTION" or "introduction" in query_lower
    has_method = intent == "METHOD" or any(k in query_lower for k in ["method", "methods", "methodology", "approach", "architecture", "algorithm", "implementation", "design", "pipeline", "framework"])
    has_results = intent == "RESULTS" or any(k in query_lower for k in ["results", "experiments", "evaluation", "performance", "accuracy", "comparison", "ablation", "analysis"])
    has_conclusion = intent == "CONCLUSION" or any(k in query_lower for k in ["conclusion", "future work", "discussion", "limitations"])

    # 2. Metadata Filtering
    filtered_metadata = []
    for r in results:
        chunk_type = str(r.get("chunk_type") or "")
        if chunk_type == "metadata" and not has_metadata:
            continue
        filtered_metadata.append(r)
        
    # 3. Reference Filtering
    filtered_references = []
    for r in filtered_metadata:
        chunk_id = str(r.get("chunk_id") or "")
        sec_num = str(r.get("section_number") or "").lower()
        sec_title = str(r.get("section_title") or "").lower()
        
        is_reference_chunk = chunk_id.startswith("references_") or sec_num == "references" or "references" in sec_title or "bibliography" in sec_title
        if is_reference_chunk and not has_reference:
            continue
        filtered_references.append(r)
        
    # 4. Reranking
    reranked = []
    for r in filtered_references:
        score = r["score"]
        sec_title = str(r.get("section_title") or "").lower()
        
        if has_abstract and "abstract" in sec_title:
            score += 100.0
        if has_introduction and any(m in sec_title for m in ["introduction", "background", "overview", "motivation", "preliminaries"]):
            score += 100.0
        if has_method and any(m in sec_title for m in ["method", "methodology", "architecture", "approach", "algorithm", "framework", "pipeline", "implementation", "design"]):
            score += 100.0
        if has_results and any(m in sec_title for m in ["result", "experiment", "evaluation", "analysis", "performance"]):
            score += 100.0
        if has_conclusion and any(m in sec_title for m in ["conclusion", "future work", "discussion", "limitations"]):
            score += 100.0
            
        if has_summary and any(m in sec_title for m in ["abstract", "introduction", "method", "result", "conclusion"]):
            score += 100.0
            
        r["adjusted_score"] = score
        reranked.append(r)
        
    # 5. Fallback
    if not reranked:
        for r in results:
            r["adjusted_score"] = r["score"]
        if len(results) > 0:
            return results
        
    return reranked


# ==========================================================
# PIPELINE
# ==========================================================

def preprocess_results(query, results):
    """
    Complete preprocessing pipeline.

    Returns cleaned retrieval results.
    """
    if not results:
        return []
        
    original_results = list(results)
    intent = detect_query_intent(query)
    
    results = apply_retrieval_policies(query, results, intent)

    results = remove_duplicate_chunks(results)

    results = sort_results(results)
    
    results = limit_chunks_per_section(results, intent)

    results = limit_chunks(results)

    results = trim_context(results, intent)
    
    results = sort_chronological(results)
    
    # Bug 1: Guarantee len >= 1 if original had chunks
    if len(results) == 0 and len(original_results) > 0:
        print("Fallback Triggered: True (Preprocessing removed all chunks)", flush=True)
        results = original_results[:1]
        
    print(f"Chunks After Filtering: {len(results)}", flush=True)

    return results


# ==========================================================
# FORMAT ONE CHUNK
# ==========================================================

def format_chunk(chunk):
    """
    Convert one retrieved chunk into a prompt-friendly format.
    """

    paper = chunk.get("paper_title", "Unknown Paper")

    section_number = chunk.get("section_number") or ""

    section_title = chunk.get("section_title") or ""

    pages = f'{chunk.get("page_start")} - {chunk.get("page_end")}'

    text = chunk.get("text", "").strip()
    
    section_info = f"{section_number} {section_title}".strip()
    if not section_info:
        section_info = "N/A"

    formatted = f"""
[PAPER] {paper}
[SECTION] {section_info}
[PAGES] {pages}
[CONTENT]
{text}
""".strip()

    return formatted


# ==========================================================
# BUILD CONTEXT
# ==========================================================

def build_context(results):
    """
    Build one long context string for the LLM.
    """
    context = []

    for chunk in results:

        context.append(

            format_chunk(chunk)

        )

    ans = "\n\n".join(context)
    return ans


# ==========================================================
# BUILD PROMPT
# ==========================================================

def build_prompt(query, context):
    """
    Final prompt sent to the LLM.
    """
    prompt = f"""
You are a research assistant.

Answer ONLY using the provided context.

If the answer is not present,
say that the information is not available.

============================================================

USER QUESTION

{query}

============================================================

CONTEXT

{context}

============================================================

ANSWER
"""
    ans = prompt.strip()
    return ans


# ==========================================================
# COMPLETE PIPELINE
# ==========================================================

def prepare_context(query, retrieval_results, user_id=None):
    """
    Complete context preparation pipeline.

    Returns

    prompt

    sources
    """
    cleaned = preprocess_results(

        query,

        retrieval_results

    )

    context = build_context(

        cleaned

    )

    prompt = build_prompt(

        query,

        context

    )

    sources = build_sources(

        cleaned

    )
    
    total_characters = sum(len(c.get("text", "")) for c in cleaned)
    
    sections = set(r.get("section_title") for r in cleaned)
    print(f"Prompt Sections: {list(sections)}", flush=True)
    print(f"Context Characters: {total_characters}", flush=True)
    print(f"Prompt Tokens: {len(prompt.split())}", flush=True)

    return {

        "prompt": prompt,

        "context": context,

        "sources": sources,

        "chunks": cleaned,
        
        "chunk_count": len(cleaned),
        
        "total_characters": total_characters,
        
        "context_length": len(context)

    }

# ==========================================================
# PREPARE COMPARISON CONTEXT (NEW)
# ==========================================================

def prepare_comparison_context(paper_title: str, retrieved_chunks: list):
    """
    Comparison mode specific context builder.
    Sorts chunks according to paper structure and builds a formatted string.
    """
    
    # Preferred order of sections
    preferred_order = [
        "abstract", "introduction", "related work", "background", "method",
        "architecture", "dataset", "training", "experiments", "results",
        "analysis", "discussion", "limitations", "future work", "conclusion"
    ]
    
    def get_section_rank(section_title):
        sec_lower = str(section_title).lower()
        for idx, preferred in enumerate(preferred_order):
            if preferred in sec_lower:
                return idx
        return len(preferred_order) # Put unknown sections at the end
        
    # Group chunks by section
    from collections import defaultdict
    sections_dict = defaultdict(list)
    
    sources = []
    
    for chunk in retrieved_chunks:
        sec_title = chunk.get("section_title")
        if not sec_title:
            sec_title = "Uncategorized"
            
        sections_dict[sec_title].append(chunk)
        
        sources.append({
            "paper_id": chunk.get("paper_id"),
            "paper_title": chunk.get("paper_title"),
            "section": chunk.get("section_title"),
            "pages": f"{chunk.get('page_start')} - {chunk.get('page_end')}"
        })
        
    # Sort sections by preferred order
    sorted_sections = sorted(sections_dict.keys(), key=get_section_rank)
    
    # Build context string
    context = ""
    for sec_title in sorted_sections:
        context += f"## {sec_title}\n"
        # Sort chunks within section by page start to keep logical order
        sorted_chunks = sorted(sections_dict[sec_title], key=lambda x: x.get("page_start", 99999))
        for chunk in sorted_chunks:
            context += f"{chunk.get('text', '')}\n\n"
            
    return context.strip(), sources

# ==========================================================
# BUILD STAGE CONTEXT (NEW)
# ==========================================================

def prepare_specific_comparison_context(query: str, title_a: str, retrieved_a: list, title_b: str, retrieved_b: list, user_id: str = None):
    """
    Comparison mode specific context builder.
    Isolates paper chunks and manages budget per paper independently to prevent hallucination.
    """
    # 1. Preprocess individually to remove duplicates and apply policies
    cleaned_a = preprocess_results(query, retrieved_a)
    cleaned_b = preprocess_results(query, retrieved_b)
    
    # 2. Sort by page logic
    cleaned_a.sort(key=lambda c: c.get("page_start", 99999))
    cleaned_b.sort(key=lambda c: c.get("page_start", 99999))
    
    budget_per_paper = 2750 # Max 5500 total
    
    def _build_for_paper(title, chunks, budget):
        sources = []
        text_out = f"============================\nPAPER: {title}\n============================\n"
        current_len = 0
        
        for chunk in chunks:
            sec = chunk.get("section_title", "Unknown")
            text = chunk.get("text", "").strip()
            
            entry = f"[SECTION] {sec}\n[CONTENT]\n{text}\n\n"
            entry_len = len(entry)
            
            if current_len + entry_len > budget:
                remaining = budget - current_len
                if remaining > 100:
                    text_out += entry[:remaining] + "...\n\n"
                    sources.append({
                        "paper_id": chunk.get("paper_id"),
                        "paper_title": chunk.get("paper_title"),
                        "section": sec,
                        "pages": f"{chunk.get('page_start')} - {chunk.get('page_end')}"
                    })
                break
                
            text_out += entry
            current_len += entry_len
            
            sources.append({
                "paper_id": chunk.get("paper_id"),
                "paper_title": chunk.get("paper_title"),
                "section": sec,
                "pages": f"{chunk.get('page_start')} - {chunk.get('page_end')}"
            })
            
        if not sources:
            text_out += f"No relevant information found for {title}.\n\n"
            
        return text_out, sources
        
    context_a, sources_a = _build_for_paper(title_a, cleaned_a, budget_per_paper)
    context_b, sources_b = _build_for_paper(title_b, cleaned_b, budget_per_paper)
    
    context = context_a + context_b
    sources = sources_a + sources_b
    
    return {
        "context": context.strip(),
        "sources": sources,
        "chunks": cleaned_a + cleaned_b
    }

# ==========================================================
# BUILD PAPER SUMMARY CONTEXT (NEW - for 3-call comparator)
# ==========================================================

# Sections to exclude entirely
_SKIP_SECTION_KEYWORDS = [
    "references", "bibliography", "acknowledgement", "acknowledgment",
    "appendix", "about the author"
]

def build_paper_summary_context(paper_id: str, max_chars: int = 6000, user_id: str = None):
    """
    Retrieves all meaningful chunks for a paper, deduplicates,
    sorts by page number, and returns a single concatenated context string.

    Only used by the comparator pipeline. Does NOT summarize.
    """
    from backend.rag.loader import resources

    chunks_lookup = resources.load_chunks(user_id, paper_id)
    if not chunks_lookup:
        return "", []

    # Collect, filter, deduplicate
    seen_ids = set()
    collected = []

    for chunk_id, chunk in chunks_lookup.items():
        if chunk_id in seen_ids:
            continue
        seen_ids.add(chunk_id)

        chunk_type = str(chunk.get("chunk_type") or "").lower()
        sec_title = str(chunk.get("section_title") or "").lower()

        # Skip metadata and junk sections
        if chunk_type == "metadata":
            continue
        if chunk_id.startswith("references_"):
            continue
        if any(kw in sec_title for kw in _SKIP_SECTION_KEYWORDS):
            continue

        text = str(chunk.get("text") or "").strip()
        if not text:
            continue

        collected.append({
            "chunk_id": chunk_id,
            "section_title": chunk.get("section_title") or "",
            "page_start": chunk.get("page_start") or 0,
            "page_end": chunk.get("page_end") or 0,
            "text": text,
        })

    # Sort by page number
    collected.sort(key=lambda c: c["page_start"])

    # Build context with character budget
    parts = []
    total = 0
    sources = []

    for c in collected:
        sec = c["section_title"]
        text = c["text"]
        entry = f"[{sec}]\n{text}" if sec else text
        entry_len = len(entry)

        if total + entry_len > max_chars:
            # Include as much as fits
            remaining = max_chars - total
            if remaining > 100:
                parts.append(entry[:remaining] + "...")
                total = max_chars
            break

        parts.append(entry)
        total += entry_len

        sources.append({
            "paper_id": paper_id,
            "section": sec,
            "pages": f"{c['page_start']} - {c['page_end']}",
        })

    context = "\n\n".join(parts)
    return context, sources