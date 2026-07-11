"""
Stage 6 — Semantic Representation Builder
==========================================
Reads graph.json produced by Stage 5 and emits semantic.json.

Each section in the output contains ONLY its direct content nodes
(Option A).  Subsections become their own separate entries so the chunk
builder (Stage 7) receives a flat, reading-order-sorted list of sections
and can reconstruct the tree from parent_section / section_path.

All fields are computed in a single pass per section to avoid repeated
loops.  No existing fields are removed or renamed.

Fields per section
------------------
  Existing (unchanged)
    section_id, section, title, parent_section,
    page_start, page_end, reading_order, nodes,
    section_path, depth, char_count

  New
    page_count           – page_end - page_start + 1
    reading_order_start  – min reading_order across nodes
    reading_order_end    – max reading_order across nodes
    node_count           – total content nodes
    paragraph_count      – Paragraph nodes
    formula_count        – Formula nodes
    figure_count         – Figure nodes
    table_count          – Table nodes
    list_count           – List nodes
    word_count           – sum of word_count across nodes
    is_leaf              – True when section has no subsections
    has_children         – True when section has at least one subsection
"""

from pathlib import Path
import json
from collections import defaultdict
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR  = Path("graph_a4")
OUTPUT_DIR = Path("semantic_me4")

OUTPUT_DIR.mkdir(exist_ok=True)

# Relations that carry content nodes from a section
CONTENT_RELATIONS = {
    "HAS_PARAGRAPH",
    "HAS_FORMULA",
    "HAS_FIGURE",
    "HAS_TABLE",
    "HAS_LIST",
}

# Named (unnumbered) top-level sections always at depth 1
NAMED_TOP_LEVEL = {
    "abstract",
    "references",
    "appendix",
    "acknowledgements",
    "acknowledgments",
}


# ==========================================================
# GRAPH LOOKUPS
# ==========================================================

def build_lookup(graph: dict) -> tuple[dict, dict]:
    """
    Build two indexes from the raw graph dict:
      node_map  : node_id  -> node dict
      adjacency : source_id -> list of edge dicts
    """
    node_map   = {node["id"]: node for node in graph["nodes"]}
    adjacency  = defaultdict(list)
    for edge in graph["edges"]:
        adjacency[edge["source"]].append(edge)
    return node_map, adjacency


# ==========================================================
# PAPER-LEVEL HELPERS
# ==========================================================

def get_paper_title(graph: dict) -> str:
    """Return the title stored on the Paper node."""
    for node in graph["nodes"]:
        if node["type"] == "Paper":
            return node.get("title", "")
    return ""


def get_metadata_nodes(graph: dict) -> list[dict]:
    """
    Collect nodes that belong to the paper header area:
    These are author names, affiliations, emails, etc.
    Extracts nodes connected to the Paper node via HAS_METADATA.
    Sorted by reading_order.
    """
    metadata_ids = {e["target"] for e in graph["edges"] if e["relation"] == "HAS_METADATA"}
    metadata = [n for n in graph["nodes"] if n["id"] in metadata_ids]
    metadata.sort(key=lambda n: n.get("reading_order", 999_999))
    return metadata


def get_section_nodes(graph: dict) -> list[dict]:
    """
    Return all Section nodes sorted by reading_order.
    Excludes the paper-title pseudo-section (section == None, title == None).
    """
    sections = [
        node for node in graph["nodes"]
        if node["type"] == "Section"
        and (node.get("section") is not None or node.get("title") is not None)
    ]
    sections.sort(key=lambda n: n.get("reading_order", 999_999))
    return sections


# ==========================================================
# SECTION HIERARCHY HELPERS
# ==========================================================

def compute_depth(section_number: str | None) -> int:
    """
    Return the nesting depth for a section.

    Examples
    --------
    None / "abstract" / "references"      -> 1
    "1"                                    -> 1
    "2.1"                                  -> 2
    "3.2.1"                                -> 3
    "appendix_A"                           -> 1
    "appendix_C.1"                         -> 2
    "appendix_A.2.1"                       -> 3
    """
    if not section_number:
        return 1
    if section_number.lower() in NAMED_TOP_LEVEL:
        return 1
    # Handle appendix_ prefixed section numbers
    if section_number.startswith("appendix_"):
        suffix = section_number[len("appendix_"):]   # e.g. "A" or "C.1"
        return len(suffix.split("."))                  # "A"->1, "C.1"->2
    return len(section_number.split("."))


def build_section_path(section_node: dict, node_map: dict) -> list[dict]:
    """
    Walk parent_section pointers upward to build the breadcrumb list.

    Returns a list of dicts ordered from root to immediate parent.
    Each entry: {"section": "3.2", "title": "Optimization"}

    Top-level sections (no parent) return [].
    """
    path    = []
    current = section_node.get("parent_section")

    while current:
        parent = node_map.get(current)
        if parent is None:
            break
        # Prepend so the list runs root → immediate parent
        path.insert(0, {
            "section": parent.get("section"),
            "title":   parent.get("title"),
        })
        current = parent.get("parent_section")

    return path


# ==========================================================
# CONTENT COLLECTION
# ==========================================================

def get_direct_content(
    section_id: str,
    adjacency:  dict,
    node_map:   dict,
) -> list[dict]:
    """
    Collect only the DIRECT content nodes of a section
    (paragraphs, formulas, figures, tables, lists).
    Subsections are NOT included; they appear as their own
    semantic sections in the flat output list.
    Nodes are sorted by reading_order.
    """
    children = [
        node_map[edge["target"]]
        for edge in adjacency.get(section_id, [])
        if edge["relation"] in CONTENT_RELATIONS
        and edge["target"] in node_map
    ]
    children.sort(key=lambda n: n.get("reading_order", 999_999))
    return children


def compute_page_range(
    nodes:        list[dict],
    fallback_page: int | None,
) -> tuple[int | None, int | None]:
    """
    Return (page_start, page_end) from content node pages.
    Falls back to fallback_page when the section has no content nodes.
    """
    pages = [n["page"] for n in nodes if n.get("page") is not None]
    if pages:
        return min(pages), max(pages)
    return fallback_page, fallback_page


def compute_char_count(nodes: list[dict]) -> int:
    """Sum character counts of all content nodes in the section."""
    return sum(n.get("char_count", len(n.get("text", ""))) for n in nodes)


def compute_section_stats(nodes: list[dict]) -> dict:
    """
    Single-pass aggregation over a section's direct content nodes.

    Returns
    -------
    dict with keys:
        node_count, paragraph_count, formula_count, figure_count,
        table_count, list_count, word_count, char_count,
        reading_order_start, reading_order_end
    """
    node_count      = len(nodes)
    paragraph_count = 0
    formula_count   = 0
    figure_count    = 0
    table_count     = 0
    list_count      = 0
    word_count      = 0
    char_count      = 0
    ro_values       = []

    for n in nodes:
        ntype = n.get("type", "")
        if ntype == "Paragraph":
            paragraph_count += 1
        elif ntype == "Formula":
            formula_count += 1
        elif ntype == "Figure":
            figure_count += 1
        elif ntype == "Table":
            table_count += 1
        elif ntype == "List":
            list_count += 1

        word_count += n.get("word_count", len(n.get("text", "").split()))
        char_count += n.get("char_count", len(n.get("text", "")))

        ro = n.get("reading_order")
        if ro is not None:
            ro_values.append(ro)

    return {
        "node_count":          node_count,
        "paragraph_count":     paragraph_count,
        "formula_count":       formula_count,
        "figure_count":        figure_count,
        "table_count":         table_count,
        "list_count":          list_count,
        "word_count":          word_count,
        "char_count":          char_count,
        "reading_order_start": min(ro_values) if ro_values else None,
        "reading_order_end":   max(ro_values) if ro_values else None,
    }


def build_subsection_set(graph: dict) -> set[str]:
    """
    Return the set of section IDs that have at least one child section.

    Used to populate is_leaf / has_children without extra per-section loops.
    """
    parents: set[str] = set()
    for edge in graph["edges"]:
        if edge["relation"] in ("HAS_SECTION", "HAS_SUBSECTION"):
            parents.add(edge["source"])
    return parents


# ==========================================================
# SEMANTIC BUILDER
# ==========================================================

def build_semantic(graph: dict, recursive: bool = False) -> dict:
    """
    Build the semantic representation for one paper.

    Parameters
    ----------
    graph     : Parsed graph.json dict from Stage 5.
    recursive : Unused in Option-A (direct-only) mode.
                Kept as a hook for future recursive collection.

    Returns
    -------
    dict with keys: paper_id, title, metadata, sections
    """
    node_map, adjacency = build_lookup(graph)

    # Pre-compute which section IDs have child sections (one pass)
    sections_with_children = build_subsection_set(graph)

    semantic: dict = {
        "paper_id": graph["paper_id"],
        "title":    get_paper_title(graph),
        "metadata": get_metadata_nodes(graph),
        "sections": [],
    }

    for sec_node in get_section_nodes(graph):
        sec_id = sec_node["id"]

        # --- content (single pass for all stats) ----------------------
        content_nodes = get_direct_content(sec_id, adjacency, node_map)
        stats         = compute_section_stats(content_nodes)

        # --- page range -----------------------------------------------
        page_start, page_end = compute_page_range(
            content_nodes,
            fallback_page=sec_node.get("page"),
        )
        page_count = (
            (page_end - page_start + 1)
            if page_start is not None and page_end is not None
            else 0
        )

        # --- hierarchy metadata ---------------------------------------
        section_path  = build_section_path(sec_node, node_map)
        depth         = compute_depth(sec_node.get("section"))
        has_children  = sec_id in sections_with_children
        is_leaf       = not has_children

        semantic["sections"].append({
            # ── identity ───────────────────────────────────────────────
            "section_id":     sec_id,
            "section":        sec_node.get("section"),
            "title":          sec_node.get("title"),

            # ── hierarchy ──────────────────────────────────────────────
            "parent_section": sec_node.get("parent_section"),
            "section_path":   section_path,
            "depth":          depth,
            "is_leaf":        is_leaf,
            "has_children":   has_children,

            # ── page range ─────────────────────────────────────────────
            "page_start":     page_start,
            "page_end":       page_end,
            "page_count":     page_count,

            # ── reading order ──────────────────────────────────────────
            "reading_order":       sec_node.get("reading_order"),
            "reading_order_start": stats["reading_order_start"],
            "reading_order_end":   stats["reading_order_end"],

            # ── content counts ─────────────────────────────────────────
            "node_count":      stats["node_count"],
            "paragraph_count": stats["paragraph_count"],
            "formula_count":   stats["formula_count"],
            "figure_count":    stats["figure_count"],
            "table_count":     stats["table_count"],
            "list_count":      stats["list_count"],

            # ── text statistics ────────────────────────────────────────
            "word_count":  stats["word_count"],
            "char_count":  stats["char_count"],

            # ── content nodes (full metadata preserved) ────────────────
            "nodes": content_nodes,
        })

    return semantic


# ==========================================================
# VALIDATION SUMMARY
# ==========================================================

def print_validation(paper_id: str, semantic: dict) -> None:
    """Print a per-paper debug summary to stdout."""
    sections   = semantic["sections"]
    n_sections = len(sections)
    n_metadata = len(semantic["metadata"])
    n_leaves   = sum(1 for s in sections if s["is_leaf"])

    node_counts = [s["node_count"] for s in sections]
    avg_nodes   = (sum(node_counts) / n_sections) if n_sections else 0

    largest  = max(sections, key=lambda s: s["node_count"], default=None)
    smallest = min(sections, key=lambda s: s["node_count"], default=None)

    total_words = sum(s["word_count"] for s in sections)

    print(f"\n{'─'*60}")
    print(f"  Paper      : {paper_id}")
    print(f"  Title      : {semantic['title'][:70]}")
    print(f"  Metadata   : {n_metadata} nodes")
    print(f"  Sections   : {n_sections}  (leaves: {n_leaves})")
    print(f"  Avg nodes  : {avg_nodes:.1f}")
    print(f"  Total words: {total_words:,}")

    if largest:
        print(
            f"  Largest    : [{largest['section']}] "
            f"{largest['title']}  ({largest['node_count']} nodes, "
            f"{largest['word_count']} words)"
        )
    if smallest:
        print(
            f"  Smallest   : [{smallest['section']}] "
            f"{smallest['title']}  ({smallest['node_count']} nodes)"
        )
    print(f"{'─'*60}")


# ==========================================================
# MAIN
# ==========================================================

def process_paper(paper_dir: Path, output_dir: Path):
    graph_file = paper_dir / "graph.json"
    if not graph_file.exists():
        return None

    with open(graph_file, encoding="utf-8") as fh:
        graph = json.load(fh)

    semantic = build_semantic(graph)
    print_validation(paper_dir.name, semantic)

    out_dir = output_dir / paper_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "semantic.json"
    
    with open(out_file, "w", encoding="utf-8") as fh:
        json.dump(semantic, fh, indent=4, ensure_ascii=False)
        
    return out_file

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper_dir in tqdm(papers, desc="Building semantic"):
        process_paper(paper_dir, OUTPUT_DIR)
    print("\nDone.")