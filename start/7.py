"""
Stage 7 — Chunk Builder
========================
Reads semantic.json produced by Stage 6 and emits chunks.json.

One chunk = one section.  Nodes inside each chunk remain in their original
reading_order.  Marker tokens (<FORMULA:id>, <FIGURE:id>, <TABLE:id>) are
inserted exactly once, in document order, immediately before the node's
own OCR text so the surrounding prose stays coherent.

Section filtering
-----------------
All sections are now included — References, Bibliography, Appendix, and
Acknowledgements are no longer skipped.  Instead each carries appropriate
retrieval flags (is_reference, is_appendix, is_acknowledgement) so
downstream consumers can filter them out if desired.

Metadata chunk
--------------
A special chunk_id="metadata" chunk is prepended before all section chunks.
It contains structured fields extracted from the pre-abstract nodes stored
in semantic.json's top-level "metadata" list (title, authors, affiliations,
emails, keywords, DOI, conference, year) plus a readable "text" field.

Output schema (per chunk)
--------------------------
  Identity
    chunk_id, chunk_type, paper_id, paper_title

  Section metadata  (section chunks only)
    section_number, section_title, section_node,
    parent_section, section_path, depth

  Page / reading-order span
    page_start, page_end, page_count,
    reading_order_start, reading_order_end

  Node inventory
    node_ids,
    formula_ids, figure_ids, table_ids, list_ids

  Content statistics
    node_count, paragraph_count,
    formula_count, figure_count, table_count, list_count,
    word_count, char_count

  Retrieval flags
    is_abstract, is_introduction, is_reference,
    is_appendix, is_acknowledgement

  Extracted metadata
    keywords            – list of keyword strings (empty list if absent)

  Text
    text
    text_length         – len(text) in characters
"""

from pathlib import Path
import json
import re
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

# Point at the enriched semantic output from Stage 6
INPUT_DIR  = Path("semantic_me4")
OUTPUT_DIR = Path("semantic_chunks_a4")

OUTPUT_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------
# Section classification sets  (lower-case)
# ----------------------------------------------------------
_REFERENCE_IDS       = {"references", "bibliography", "works cited", "reference"}
_APPENDIX_IDS        = {"appendix"}
_ACKNOWLEDGEMENT_IDS = {"acknowledgement", "acknowledgements", "acknowledgment", "acknowledgments"}
_ABSTRACT_IDS        = {"abstract"}
_INTRO_IDS           = {"introduction"}

# Maximum words per non-reference section chunk before splitting
_CHUNK_WORD_LIMIT = 1200

# Boilerplate patterns to skip during metadata extraction
_BOILERPLATE_PATTERNS = (
    "permission to make digital",
    "association for computing machinery",
    "acm reference format",
    "https://doi.org",
    "xxxx-xxxx",
    "copyright",
    "licensed under",
    "creative commons",
    "all rights reserved",
    "preprint",
    "under review",
    "published in",
    "proceedings of",
    "accepted at",
    "to appear in",
)

# Keyword line prefixes recognised at the end of abstracts
_KEYWORD_PREFIXES = (
    "keywords:",
    "keywords -",
    "keywords—",
    "keywords –",
    "index terms:",
    "index terms -",
    "index terms—",
    "index terms –",
)

# Simple email regex
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# CHANGE: target word budget per reference sub-chunk
_REF_CHUNK_WORDS = 900

# ==========================================================
# HELPERS
# ==========================================================

def _normalise(s) -> str:
    """Lower-case, strip leading digits/punctuation, strip whitespace.  Safe for None."""
    if not s:
        return ""
    s = str(s).strip().lower()
    # Strip a leading section number like "6 " so "6 acknowledgement" → "acknowledgement"
    s = re.sub(r"^\d+[\s.]+", "", s).strip()
    return s


def _title_matches(sec_num, sec_title, id_set: set) -> bool:
    """
    Return True when either the raw normalised section number/title,
    or the de-numbered title, is a member of id_set.
    Also checks for partial containment for multi-word ids like 'works cited'.
    """
    norm_num   = _normalise(sec_num)
    norm_title = _normalise(sec_title)

    if norm_num in id_set or norm_title in id_set:
        return True
    # check every id phrase against title via substring
    for phrase in id_set:
        if phrase in norm_title:
            return True
    return False


# ==========================================================
# RETRIEVAL FLAGS
# ==========================================================

def compute_retrieval_flags(section: dict) -> dict:
    """
    Compute boolean retrieval flags for a section using case-insensitive,
    prefix-stripped matching.

    Returns
    -------
    dict with keys:
        is_abstract, is_introduction, is_reference,
        is_appendix, is_acknowledgement
    """
    sec_num   = section.get("section")
    sec_title = section.get("title")

    is_abstract       = _title_matches(sec_num, sec_title, _ABSTRACT_IDS)
    is_introduction   = (
        _title_matches(sec_num, sec_title, _INTRO_IDS)
        or str(sec_num).strip() == "1"    # Section 1 is almost always intro
    )
    is_reference      = _title_matches(sec_num, sec_title, _REFERENCE_IDS)
    is_appendix       = (
        _title_matches(sec_num, sec_title, _APPENDIX_IDS)
        or _normalise(sec_title).startswith("appendix")
        or _normalise(sec_num).startswith("appendix")
        # Handle appendix_A, appendix_B, appendix_C.1 from Stage 4
        or (sec_num or "").startswith("appendix_")
    )
    is_acknowledgement = _title_matches(sec_num, sec_title, _ACKNOWLEDGEMENT_IDS)

    return {
        "is_abstract":        is_abstract,
        "is_introduction":    is_introduction,
        "is_reference":       is_reference,
        "is_appendix":        is_appendix,
        "is_acknowledgement": is_acknowledgement,
    }


# ==========================================================
# KEYWORD EXTRACTION
# ==========================================================

def extract_keywords(text: str) -> tuple:
    """
    Look for a keyword line at the very end of the abstract text.

    Recognises lines that start with any of the _KEYWORD_PREFIXES
    (case-insensitive).  When found:
      - removes the keyword line from the returned text
      - splits the keywords on commas and returns them as a list

    If no keyword line is found, returns the original text unchanged
    and an empty list.

    Returns
    -------
    (cleaned_text, keywords_list)
    """
    if not text:
        return text, []

    lines = text.split("\n")

    keyword_line_idx = None
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        for prefix in _KEYWORD_PREFIXES:
            if stripped.lower().startswith(prefix):
                keyword_line_idx = i
                break
        break  # only inspect the last non-blank line

    if keyword_line_idx is None:
        return text, []

    raw_kw_line = lines[keyword_line_idx].strip()

    keyword_payload = raw_kw_line
    for prefix in _KEYWORD_PREFIXES:
        if keyword_payload.lower().startswith(prefix):
            keyword_payload = keyword_payload[len(prefix):].strip()
            break

    keywords = [kw.strip() for kw in keyword_payload.split(",") if kw.strip()]

    cleaned_lines = lines[:keyword_line_idx]
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()

    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text, keywords


# ==========================================================
# TEXT CONSTRUCTION
# ==========================================================

def build_text(nodes: list) -> str:
    """
    Assemble chunk text from nodes in their existing reading_order.

    Rules
    -----
    - Nodes are already sorted by Stage 6; do NOT re-sort here.
    - Formula / Figure / Table / List nodes get a marker token first,
      then the OCR/caption text on the same logical block.
    - Paragraph nodes contribute raw text only.
    - Footnote-labelled nodes are prefixed with [FOOTNOTE].
    - Empty text is silently skipped so no blank paragraphs leak in.
    - Marker tokens are emitted exactly once per node.
    """
    pieces: list = []

    for node in nodes:
        node_type = node.get("type", "")
        node_text = node.get("text", "").strip()
        node_id   = node.get("id", "")
        label     = node.get("label", "")

        if node_type == "Formula":
            pieces.append(f"<FORMULA:{node_id}>")
            if node_text:
                pieces.append(node_text)

        elif node_type == "Figure":
            pieces.append(f"<FIGURE:{node_id}>")
            if node_text:
                pieces.append(node_text)

        elif node_type == "Table":
            pieces.append(f"<TABLE:{node_id}>")
            if node_text:
                pieces.append(node_text)

        elif node_type == "List":
            pieces.append(f"<LIST:{node_id}>")
            if node_text:
                pieces.append(node_text)

        else:
            if node_text:
                # Mark footnotes so they can be distinguished from body text
                if label == "footnote":
                    pieces.append(f"[FOOTNOTE] {node_text}")
                else:
                    pieces.append(node_text)

    return "\n\n".join(pieces)


# ==========================================================
# NODE STATISTICS
# ==========================================================

def collect_node_stats(nodes: list) -> dict:
    """
    Single-pass aggregation over a section's content nodes.

    Returns a dict with:
        node_ids, formula_ids, figure_ids, table_ids, list_ids,
        node_count, paragraph_count,
        formula_count, figure_count, table_count, list_count,
        word_count, char_count,
        reading_orders, pages
    """
    node_ids       : list = []
    formula_ids    : list = []
    figure_ids     : list = []
    table_ids      : list = []
    list_ids       : list = []
    reading_orders : list = []
    pages          : list = []

    paragraph_count = 0
    formula_count   = 0
    figure_count    = 0
    table_count     = 0
    list_count      = 0
    word_count      = 0
    char_count      = 0

    for node in nodes:
        nid   = node.get("id", "")
        ntype = node.get("type", "")
        text  = node.get("text", "")

        node_ids.append(nid)

        if ntype == "Formula":
            formula_ids.append(nid)
            formula_count += 1
        elif ntype == "Figure":
            figure_ids.append(nid)
            figure_count += 1
        elif ntype == "Table":
            table_ids.append(nid)
            table_count += 1
        elif ntype == "List":
            list_ids.append(nid)
            list_count += 1
        else:
            paragraph_count += 1

        ro = node.get("reading_order")
        if ro is not None:
            reading_orders.append(ro)

        pg = node.get("page")
        if pg is not None:
            pages.append(pg)

        wc = node.get("word_count")
        word_count += wc if wc is not None else len(text.split())

        cc = node.get("char_count")
        char_count += cc if cc is not None else len(text)

    return {
        "node_ids":        node_ids,
        "formula_ids":     formula_ids,
        "figure_ids":      figure_ids,
        "table_ids":       table_ids,
        "list_ids":        list_ids,
        "node_count":      len(node_ids),
        "paragraph_count": paragraph_count,
        "formula_count":   formula_count,
        "figure_count":    figure_count,
        "table_count":     table_count,
        "list_count":      list_count,
        "word_count":      word_count,
        "char_count":      char_count,
        "reading_orders":  reading_orders,
        "pages":           pages,
    }


# ==========================================================
# METADATA CHUNK
# ==========================================================

def _looks_like_email(text: str) -> bool:
    return bool(_EMAIL_RE.search(text))


def _is_boilerplate(text: str) -> bool:
    """Return True if text is a copyright notice, publisher boilerplate, etc."""
    lowered = text.lower()
    return any(pat in lowered for pat in _BOILERPLATE_PATTERNS)


def _looks_like_affiliation(text: str) -> bool:
    """
    Heuristic: affiliations often contain institution keywords or
    long mixed-case phrases with numbers (department, university, lab…).
    Uses regex word boundaries to avoid false positives.
    """
    lowered = text.lower()
    markers = [
        r"\buniversity\b", r"\binstitute\b", r"\bdepartment\b", r"\blab\b", r"\blaboratory\b",
        r"\bcollege\b", r"\bschool\b", r"\bcenter\b", r"\bcentre\b", r"\bresearch\b", r"\btechnology\b",
        r"\bfaculty\b", r"\bacademy\b", r"\bgroup\b", r"\bcorporation\b", r"\binc\.?\b", r"\bltd\.?\b",
        r"\bai\b", r"\blabs\b", r"\bgoogle\b", r"\bsony\b", r"\bhospital\b", r"\bclinic\b", r"\bcompany\b",
        r"\bgmbh\b", r"\bllc\b", r"\bsciences\b", r"\bengineering\b", r"\bdept\.?\b", r"\buniv\.?\b", r"\binst\.?\b",
        r"\bnational\b", r"\binternational\b"
    ]
    
    for m in markers:
        if re.search(m, lowered):
            return True
    return False


def _split_name_from_affiliation(text: str) -> tuple[str | None, str]:
    """
    Attempt to split concatenated name+affiliation strings like:
      "Dongqi Cai Beiyou Shenzhen Institute"
    into (name, affiliation).

    Heuristic: the author name is the first 2 words (covers most
    "FirstName LastName" patterns), and the rest is the affiliation.
    Only splits when the text contains an institution keyword AND
    there are at least 2 words before the first institution keyword
    boundary (looking at the broader text, not just the prefix).

    Returns (name, remaining_text) if a split point is found,
    or (None, text) if no institution keyword boundary is detected.
    """
    lowered = text.lower()
    markers = (
        "university", "institute", "department", "lab", "laboratory",
        "college", "school", "center", "centre", "technology",
        "faculty", "academy",
    )
    # Check that text actually contains an institution keyword
    has_marker = any(m in lowered for m in markers)
    if not has_marker:
        return None, text

    words = text.split()
    if len(words) < 3:
        return None, text

    # Take first 2 words as the name if both start with uppercase
    # and the remaining text contains the institution keyword
    w0 = words[0].strip(",")
    w1 = words[1].strip(",")
    if w0 and w1 and w0[0].isupper() and w1[0].isupper():
        name = f"{w0} {w1}"
        remaining = " ".join(words[2:]).strip().strip(",").strip()
        return name, remaining

    return None, text


# ------------------------------------------------------------------
# CHANGE: improved author parsing and metadata extraction
# ------------------------------------------------------------------

_GROUPED_EMAIL_RE = re.compile(r"\{([^}]+)\}\s*@\s*([A-Za-z0-9.\-]+\.[A-Za-z]{2,})")

_AUTHOR_STRIP_RE = re.compile(
    r"[\*∗†‡§¶#]"
    r"|\b\d+(?:,\d+)*\b"
    r"|\bemail\b"
    r"|\bcorresponding\b"
    r"|[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]",
    re.IGNORECASE,
)

_BLACKLIST = {
    'university', 'institute', 'department', 'lab', 'laboratory',
    'college', 'school', 'center', 'centre', 'research', 'technology',
    'faculty', 'academy', 'group', 'corporation', 'inc', 'ltd',
    'ai', 'labs', 'google', 'sony', 'hospital', 'clinic', 'company',
    'gmbh', 'llc', 'sciences', 'engineering', 'dept', 'univ', 'inst',
    'national', 'international'
}

_PARTICLES = {'van', 'de', 'der', 'la', 'von', 'di', 'del', 'le', 'al', 'bin', 'ibn', 'da', 'dos', 'das'}


def _split_affiliations(text: str) -> list:
    """Split affiliations by numbers followed by uppercase letters."""
    if not text:
        return []
    parts = re.split(r"(?:^|\s)\d+(?=\s+[A-Z])", text)
    result = []
    for p in parts:
        p = p.strip().strip(",").strip()
        if p:
            result.append(p)
    return result if result else [text.strip()]


def _parse_metadata_texts(raw_texts: list[str]) -> tuple[list[str], list[str], list[str]]:
    """
    Combined multi-stage parsing for metadata blocks:
    1. Expand and extract emails (including {a,b}@domain).
    2. Split by lines, commas, or superscripts.
    3. Classify remaining fragments as Notes, Affiliations, or Authors.
    """
    combined = "\n".join(raw_texts)
    
    emails = []
    for match in _GROUPED_EMAIL_RE.finditer(combined):
        users_str, domain = match.groups()
        for user in users_str.split(','):
            user = user.strip()
            if user:
                emails.append(f"{user}@{domain}")
    combined = _GROUPED_EMAIL_RE.sub("", combined)
    
    for match in _EMAIL_RE.finditer(combined):
        emails.append(match.group(0))
    combined = _EMAIL_RE.sub("", combined)
    
    seen_emails = set()
    deduped_emails = []
    for e in emails:
        if e not in seen_emails:
            seen_emails.add(e)
            deduped_emails.append(e)

    extracted_authors = []
    extracted_affiliations = []
    
    lines = []
    for line in combined.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        word_count = len(line.split())
        if word_count > 50:
            continue
        if word_count > 15 and "," not in line and ";" not in line:
            continue
            
        if ',' in line or ' and ' in line.lower():
            l = re.sub(r"\band\b", ",", line, flags=re.IGNORECASE)
            for part in l.split(','):
                if part.strip(): lines.append(part.strip())
        else:
            parts = re.split(r"(?:^|\s)[0-9,α-ωΑ-Ω*∗†‡§¶#]+\s+(?=[A-Z])", line)
            if len(parts) > 1:
                for part in parts:
                    if part.strip(): lines.append(part.strip())
            else:
                lines.append(line)

    for line in lines:
        if not line: continue
        
        l_lower = line.lower()
        
        if _is_boilerplate(line) or 'equal contribution' in l_lower or 'corresponding author' in l_lower or 'supported by' in l_lower:
            continue
            
        if any(m in l_lower for m in _BLACKLIST):
            extracted_affiliations.extend(_split_affiliations(line))
            continue
            
        clean_name = _AUTHOR_STRIP_RE.sub("", line)
        clean_name = re.sub(r"\s+", " ", clean_name).strip().strip(".,")
        
        if not clean_name: continue
        if any(c in clean_name for c in '&+|@'): 
            extracted_affiliations.extend(_split_affiliations(line))
            continue
            
        words = clean_name.split()
        if not (2 <= len(words) <= 6):
            extracted_affiliations.extend(_split_affiliations(line))
            continue
            
        is_valid = True
        for w in words:
            w_lower = w.lower().strip('.,')
            if w_lower in _BLACKLIST: 
                is_valid = False
                break
            if not (w[0].isupper() or w_lower in _PARTICLES or len(w) <= 2):
                is_valid = False
                break
                
        if is_valid:
            extracted_authors.append(clean_name)
        else:
            extracted_affiliations.extend(_split_affiliations(line))
            
    return deduped_emails, extracted_authors, extracted_affiliations


def build_metadata_chunk(doc: dict) -> dict:
    """
    Build a special metadata chunk from the document-level fields and the
    pre-abstract nodes stored in doc['metadata'].

    Extracted (when available):
        title, authors, affiliations, emails, keywords, doi, conference, year

    All fields default to [] or null if unavailable — no guessing.

    The 'text' field is a human-readable summary of all extracted fields.
    """
    paper_id    = doc.get("paper_id", "")
    paper_title = doc.get("title", "") or ""

    # doc-level structured metadata (may or may not exist)
    doc_meta: dict = {}
    if isinstance(doc.get("metadata"), dict):
        doc_meta = doc["metadata"]

    # pre-abstract node list (Stage 6 stores them here when metadata is a list)
    pre_nodes: list = []
    if isinstance(doc.get("metadata"), list):
        pre_nodes = doc["metadata"]

    # ── harvest from pre-abstract nodes ──────────────────────────────────
    raw_texts = [n.get("text", "").strip() for n in pre_nodes if n.get("text", "").strip()]

    deduped_emails, extracted_authors, extracted_affiliations = _parse_metadata_texts(raw_texts)

    # Filter out paper title from authors to prevent false positives
    if paper_title:
        title_lower = paper_title.lower()
        extracted_authors = [a for a in extracted_authors if a.lower() != title_lower]

    # ── pull from doc-level structured fields when present ───────────────
    title        = paper_title or doc_meta.get("title") or None
    authors      = doc_meta.get("authors", extracted_authors) or extracted_authors
    affiliations = doc_meta.get("affiliations", extracted_affiliations) or extracted_affiliations
    emails       = doc_meta.get("emails", deduped_emails) or deduped_emails
    keywords     = doc_meta.get("keywords", []) or []
    doi          = doc_meta.get("doi") or None
    conference   = doc_meta.get("conference") or doc_meta.get("venue") or None
    year         = doc_meta.get("year") or None

    # normalise to lists
    if isinstance(authors, str):
        authors = [authors]
    if isinstance(affiliations, str):
        affiliations = [affiliations]
    if isinstance(emails, str):
        emails = [emails]
    if isinstance(keywords, str):
        keywords = [keywords]

    # ── build readable text ──────────────────────────────────────────────
    lines = []
    lines.append(f"Title: {title or 'N/A'}")
    lines.append(f"Authors: {', '.join(authors) if authors else 'N/A'}")
    lines.append(f"Affiliations: {' | '.join(affiliations) if affiliations else 'N/A'}")
    lines.append(f"Emails: {', '.join(emails) if emails else 'N/A'}")
    lines.append(f"Keywords: {', '.join(keywords) if keywords else 'N/A'}")
    lines.append(f"DOI: {doi or 'N/A'}")
    lines.append(f"Conference: {conference or 'N/A'}")
    lines.append(f"Year: {year or 'N/A'}")
    text = "\n".join(lines)

    chunk: dict = {
        # ── identity ──────────────────────────────────────────────────────
        "chunk_id":   "metadata",
        "chunk_type": "metadata",
        "paper_id":   paper_id,
        "paper_title": title or "",

        # ── structured metadata fields ────────────────────────────────────
        "title":        title,
        "authors":      authors      if authors      else [],
        "affiliations": affiliations if affiliations else [],
        "emails":       emails       if emails       else [],
        "keywords":     keywords     if keywords     else [],
        "doi":          doi,
        "conference":   conference,
        "year":         year,

        # ── text ──────────────────────────────────────────────────────────
        "text":        text,
        "text_length": len(text),
    }

    return chunk


# ------------------------------------------------------------------
# CHANGE: reference section splitter
# ------------------------------------------------------------------

def _split_reference_section(
    section: dict,
    paper_id: str,
    paper_title: str,
    flags: dict,
    ref_idx_start: int,
) -> list:
    """
    CHANGE: split a large References section into sub-chunks of
    approximately _REF_CHUNK_WORDS words each, preserving node order
    and all metadata fields.

    If the section is small enough to fit in one chunk, a single-element
    list is returned (same structure as the normal section chunk).

    chunk_id format: references_0, references_1, …
    """
    nodes = section.get("nodes", [])
    if not nodes:
        return []

    # Partition nodes into word-budget buckets
    buckets: list = [[]]
    bucket_words = 0
    for node in nodes:
        wc = node.get("word_count") or len(node.get("text", "").split())
        if bucket_words + wc > _REF_CHUNK_WORDS and buckets[-1]:
            buckets.append([])
            bucket_words = 0
        buckets[-1].append(node)
        bucket_words += wc

    result = []
    for sub_idx, bucket in enumerate(buckets):
        stats = collect_node_stats(bucket)
        pages = stats["pages"]
        page_start = min(pages) if pages else section.get("page_start")
        page_end   = max(pages) if pages else section.get("page_end")
        page_count = (
            (page_end - page_start + 1)
            if page_start is not None and page_end is not None else 0
        )
        ros = stats["reading_orders"]
        text = build_text(bucket)
        chunk: dict = {
            "chunk_id":    f"references_{ref_idx_start + sub_idx}",
            "chunk_type":  "section",
            "paper_id":    paper_id,
            "paper_title": paper_title,
            "section_number": section.get("section"),
            "section_title":  section.get("title"),
            "section_node":   section.get("section_id"),
            "parent_section": section.get("parent_section"),
            "section_path":   section.get("section_path", []),
            "depth":          section.get("depth", 1),
            "page_start": page_start,
            "page_end":   page_end,
            "page_count": page_count,
            "reading_order_start": min(ros) if ros else None,
            "reading_order_end":   max(ros) if ros else None,
            "node_ids":    stats["node_ids"],
            "formula_ids": stats["formula_ids"],
            "figure_ids":  stats["figure_ids"],
            "table_ids":   stats["table_ids"],
            "list_ids":    stats["list_ids"],
            "node_count":      stats["node_count"],
            "paragraph_count": stats["paragraph_count"],
            "formula_count":   stats["formula_count"],
            "figure_count":    stats["figure_count"],
            "table_count":     stats["table_count"],
            "list_count":      stats["list_count"],
            "word_count":      stats["word_count"],
            "char_count":      stats["char_count"],
            "is_abstract":        flags["is_abstract"],
            "is_introduction":    flags["is_introduction"],
            "is_reference":       flags["is_reference"],
            "is_appendix":        flags["is_appendix"],
            "is_acknowledgement": flags["is_acknowledgement"],
            "keywords": [],
            "text":        text,
            "text_length": len(text),
        }
        result.append(chunk)
    return result


def _split_large_section(
    section: dict,
    paper_id: str,
    paper_title: str,
    flags: dict,
    chunk_idx: int,
) -> list:
    """
    Split a large non-reference section into sub-chunks of approximately
    _CHUNK_WORD_LIMIT words each, preserving node order and metadata.

    chunk_id format: chunk_{chunk_idx}_0, chunk_{chunk_idx}_1, …

    Returns an empty list if the section fits in a single chunk (no split needed).
    """
    nodes = section.get("nodes", [])
    if not nodes:
        return []

    # Partition nodes into word-budget buckets
    buckets: list = [[]]
    bucket_words = 0
    for node in nodes:
        wc = node.get("word_count") or len(node.get("text", "").split())
        if bucket_words + wc > _CHUNK_WORD_LIMIT and buckets[-1]:
            buckets.append([])
            bucket_words = 0
        buckets[-1].append(node)
        bucket_words += wc

    # If only one bucket, no splitting needed — return empty to signal caller
    if len(buckets) <= 1:
        return []

    result = []
    for sub_idx, bucket in enumerate(buckets):
        stats = collect_node_stats(bucket)
        pages = stats["pages"]
        page_start = min(pages) if pages else section.get("page_start")
        page_end   = max(pages) if pages else section.get("page_end")
        page_count = (
            (page_end - page_start + 1)
            if page_start is not None and page_end is not None else 0
        )
        ros = stats["reading_orders"]
        raw_text = build_text(bucket)

        # keyword extraction for abstract sub-chunks
        if flags["is_abstract"]:
            text, keywords = extract_keywords(raw_text)
        else:
            text, keywords = raw_text, []

        chunk: dict = {
            "chunk_id":    f"chunk_{chunk_idx}_{sub_idx}",
            "chunk_type":  "section",
            "paper_id":    paper_id,
            "paper_title": paper_title,
            "section_number": section.get("section"),
            "section_title":  section.get("title"),
            "section_node":   section.get("section_id"),
            "parent_section": section.get("parent_section"),
            "section_path":   section.get("section_path", []),
            "depth":          section.get("depth", 1),
            "page_start": page_start,
            "page_end":   page_end,
            "page_count": page_count,
            "reading_order_start": min(ros) if ros else None,
            "reading_order_end":   max(ros) if ros else None,
            "node_ids":    stats["node_ids"],
            "formula_ids": stats["formula_ids"],
            "figure_ids":  stats["figure_ids"],
            "table_ids":   stats["table_ids"],
            "list_ids":    stats["list_ids"],
            "node_count":      stats["node_count"],
            "paragraph_count": stats["paragraph_count"],
            "formula_count":   stats["formula_count"],
            "figure_count":    stats["figure_count"],
            "table_count":     stats["table_count"],
            "list_count":      stats["list_count"],
            "word_count":      stats["word_count"],
            "char_count":      stats["char_count"],
            "is_abstract":        flags["is_abstract"],
            "is_introduction":    flags["is_introduction"],
            "is_reference":       flags["is_reference"],
            "is_appendix":        flags["is_appendix"],
            "is_acknowledgement": flags["is_acknowledgement"],
            "keywords": keywords,
            "text":        text,
            "text_length": len(text),
        }
        result.append(chunk)
    return result


# ==========================================================
# BUILD CHUNKS
# ==========================================================

def build_chunks(doc: dict) -> tuple:
    """
    Convert one paper's semantic.json into a flat list of chunks.

    Structure
    ---------
    - chunk_id="metadata"  always first
    - one chunk per section (no sections are skipped)
    - sections with zero direct content nodes are still excluded
      (they are structural parent nodes with no text of their own)

    Returns
    -------
    (chunks, n_empty)  where n_empty counts zero-node sections skipped.
    """
    chunks  : list = []
    n_empty : int  = 0   # sections with no content nodes

    paper_id    = doc.get("paper_id", "")
    paper_title = doc.get("title", "")

    # ── 0. metadata chunk (always first) ─────────────────────────────────
    chunks.append(build_metadata_chunk(doc))

    chunk_idx = 0   # index for section chunks only (keeps existing IDs stable)
    ref_sub_idx = 0  # CHANGE: running counter for references_N sub-chunks

    for section in doc.get("sections", []):

        nodes = section.get("nodes", [])

        # Skip structural parent sections (no direct content).
        if not nodes:
            n_empty += 1
            continue

        # CHANGE: route large reference sections through the splitter
        flags = compute_retrieval_flags(section)
        if flags["is_reference"]:
            ref_chunks = _split_reference_section(
                section, paper_id, paper_title, flags, ref_sub_idx
            )
            chunks.extend(ref_chunks)
            ref_sub_idx += len(ref_chunks)
            # do NOT increment chunk_idx — reference IDs are separate
            continue

        # ── collect stats in one pass ─────────────────────────────────────
        stats = collect_node_stats(nodes)

        # ── page span ─────────────────────────────────────────────────────
        pages      = stats["pages"]
        page_start = min(pages) if pages else section.get("page_start")
        page_end   = max(pages) if pages else section.get("page_end")
        page_count = (
            (page_end - page_start + 1)
            if page_start is not None and page_end is not None
            else 0
        )

        # ── reading-order span ────────────────────────────────────────────
        ros = stats["reading_orders"]
        reading_order_start = min(ros) if ros else None
        reading_order_end   = max(ros) if ros else None

        # ── check for oversized section → split if needed ─────────────────
        if stats["word_count"] > _CHUNK_WORD_LIMIT:
            sub_chunks = _split_large_section(
                section, paper_id, paper_title, flags, chunk_idx
            )
            if sub_chunks:
                chunks.extend(sub_chunks)
                chunk_idx += 1
                continue

        # ── assemble text ─────────────────────────────────────────────────
        raw_text = build_text(nodes)

        # ── keyword extraction (abstract only) ────────────────────────────
        if flags["is_abstract"]:
            text, keywords = extract_keywords(raw_text)
        else:
            text, keywords = raw_text, []

        chunk: dict = {
            # ── identity ─────────────────────────────────────────────────
            "chunk_id":    f"chunk_{chunk_idx}",
            "chunk_type":  "section",
            "paper_id":    paper_id,
            "paper_title": paper_title,

            # ── section metadata ──────────────────────────────────────────
            "section_number": section.get("section"),
            "section_title":  section.get("title"),
            "section_node":   section.get("section_id"),
            "parent_section": section.get("parent_section"),
            "section_path":   section.get("section_path", []),
            "depth":          section.get("depth", 1),

            # ── page span ─────────────────────────────────────────────────
            "page_start": page_start,
            "page_end":   page_end,
            "page_count": page_count,

            # ── reading-order span ────────────────────────────────────────
            "reading_order_start": reading_order_start,
            "reading_order_end":   reading_order_end,

            # ── node inventory ────────────────────────────────────────────
            "node_ids":    stats["node_ids"],
            "formula_ids": stats["formula_ids"],
            "figure_ids":  stats["figure_ids"],
            "table_ids":   stats["table_ids"],
            "list_ids":    stats["list_ids"],

            # ── content statistics ────────────────────────────────────────
            "node_count":      stats["node_count"],
            "paragraph_count": stats["paragraph_count"],
            "formula_count":   stats["formula_count"],
            "figure_count":    stats["figure_count"],
            "table_count":     stats["table_count"],
            "list_count":      stats["list_count"],
            "word_count":      stats["word_count"],
            "char_count":      stats["char_count"],

            # ── retrieval flags ───────────────────────────────────────────
            "is_abstract":        flags["is_abstract"],
            "is_introduction":    flags["is_introduction"],
            "is_reference":       flags["is_reference"],
            "is_appendix":        flags["is_appendix"],
            "is_acknowledgement": flags["is_acknowledgement"],

            # ── extracted metadata ────────────────────────────────────────
            "keywords": keywords,

            # ── content text ──────────────────────────────────────────────
            "text":        text,
            "text_length": len(text),
        }

        chunks.append(chunk)
        chunk_idx += 1

    # ── propagate keywords from abstract chunk to metadata chunk ─────────
    abstract_keywords = []
    for c in chunks:
        if c.get("is_abstract") and c.get("keywords"):
            abstract_keywords = c["keywords"]
            break
    if abstract_keywords:
        for c in chunks:
            if c.get("chunk_id") == "metadata":
                c["keywords"] = abstract_keywords
                break

    return chunks, n_empty


# ==========================================================
# VALIDATION
# ==========================================================

def validate_chunks(chunks: list, paper_id: str) -> None:
    """
    Post-build sanity checks.  Prints warnings; does not raise.

    Checks:
      1. Exactly one metadata chunk exists (chunk_id == "metadata").
      2. References appear as chunks (is_reference == True somewhere).
      3. Flags are boolean.
    """
    meta_chunks = [c for c in chunks if c.get("chunk_id") == "metadata"]
    if len(meta_chunks) != 1:
        print(f"  [WARN] {paper_id}: expected 1 metadata chunk, found {len(meta_chunks)}")

    has_ref = any(c.get("is_reference") for c in chunks)
    # Not a hard error — some papers genuinely have no reference section
    if not has_ref:
        print(f"  [INFO] {paper_id}: no is_reference chunk found")

    for c in chunks:
        for flag in ("is_abstract", "is_introduction", "is_reference",
                     "is_appendix", "is_acknowledgement"):
            if flag in c and not isinstance(c[flag], bool):
                print(f"  [WARN] {paper_id}: flag {flag} is not bool in {c['chunk_id']}")


# ==========================================================
# MAIN
# ==========================================================

def process_paper(paper: Path, output_dir: Path):
    semantic_file = paper / "semantic.json"
    if not semantic_file.exists():
        return None

    with open(semantic_file, encoding="utf-8") as fh:
        doc = json.load(fh)

    chunks, n_empty = build_chunks(doc)

    # run validation
    validate_chunks(chunks, doc.get("paper_id", paper.name))

    out_dir = output_dir / paper.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "chunks.json"

    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(chunks, fh, indent=4, ensure_ascii=False)

    # --- per-paper summary ------------------------------------------------
    section_chunks = [c for c in chunks if c.get("chunk_type") == "section"]

    total_words    = sum(c["word_count"]    for c in section_chunks)
    total_nodes    = sum(c["node_count"]    for c in section_chunks)
    total_formulas = sum(c["formula_count"] for c in section_chunks)
    total_figures  = sum(c["figure_count"]  for c in section_chunks)
    total_tables   = sum(c["table_count"]   for c in section_chunks)

    n_refs  = sum(1 for c in section_chunks if c["is_reference"])
    n_appx  = sum(1 for c in section_chunks if c["is_appendix"])
    n_ack   = sum(1 for c in section_chunks if c["is_acknowledgement"])

    abstract_chunk = next((c for c in section_chunks if c["is_abstract"]), None)

    print(f"\n{'═'*70}")
    print(f"  Paper   : {doc.get('paper_id', '?')}")
    print(f"  Title   : {doc.get('title', '')[:65]}")
    print(f"  Chunks  : {len(chunks)} total  ({len(section_chunks)} sections + 1 metadata)  (empty-node skipped: {n_empty})")
    print(f"  Nodes   : {total_nodes}  |  Words: {total_words:,}")
    print(
        f"  Formulas: {total_formulas}  "
        f"Figures: {total_figures}  "
        f"Tables: {total_tables}"
    )
    print(f"  Refs: {n_refs}  Appendix: {n_appx}  Acknowledgements: {n_ack}")

    if abstract_chunk and abstract_chunk.get("keywords"):
        kw_preview = ", ".join(abstract_chunk["keywords"][:5])
        print(f"  Keywords: {kw_preview}")

    if section_chunks:
        c0 = section_chunks[0]
        print(
            f"\n  chunk_0  [{c0.get('section_number')}] {c0.get('section_title')}"
            f"  p{c0.get('page_start')}–{c0.get('page_end')}"
            f"  {c0.get('word_count')} words"
            f"  depth={c0.get('depth')}"
            f"  text_length={c0.get('text_length')}"
        )

    return out_file

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper in tqdm(papers, desc="Building chunks"):
        process_paper(paper, OUTPUT_DIR)
    print("\nDone.")