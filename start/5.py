from pathlib import Path
import json
import copy
import re
import networkx as nx
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR  = Path("graph_po4")
OUTPUT_DIR = Path("graph_a4")

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# TYPE MAP
# ==========================================================

TYPE_MAP = {
    "SectionHeaderItem": "Section",
    "TextItem":          "Paragraph",
    "FormulaItem":       "Formula",
    "PictureItem":       "Figure",
    "TableItem":         "Table",
    "ListItem":          "List",
}

# ==========================================================
# Section Detection
# ==========================================================
# Research papers contain SectionHeaderItems that are NOT real
# sections: paper titles, author names, conference names, etc.
# is_real_section() distinguishes true section headers so the
# graph builder can skip false positives.
# ==========================================================

COMMON_SECTIONS = {
    "abstract",
    "introduction",
    "background",
    "related work",
    "method",
    "methods",
    "methodology",
    "approach",
    "experiments",
    "experimental setup",
    "results",
    "discussion",
    "conclusion",
    "conclusions",
    "references",
    "appendix",
    "acknowledgements",
    "acknowledgments",
}

# "1 Introduction" / "2.1 Related Work" style
NUMBERED = re.compile(r"^(\d+(\.[\d]+)*)\s+.+")

# "I Introduction" / "II. Background" style
ROMAN = re.compile(
    r"^(I{1,3}|IV|VI{0,3}|IX|X{1,3}|XI{1,3}|XIV|XV|XVI{0,3}|XIX|XX)\.?\s+.+",
    re.IGNORECASE,
)


def is_real_section(node: dict) -> bool:
    """
    Return True if a SectionHeaderItem represents a genuine document
    section rather than metadata (title, author, affiliation, etc.).

    A node qualifies as a real section when ANY of the following hold:
      - It already has a non-null section_number (Stage 4 assigned one)
      - Its lowercased text matches a known academic section name
      - Its text matches a numbered or Roman-numeral pattern

    All other SectionHeaderItems are treated as metadata/non-section
    headers (paper titles, author names, affiliations, venue strings,
    conference headers, etc.).

    Note: Single-letter patterns ("A. Appendix") are NOT checked here
    because they produce too many false positives with author initials.
    Stage 4 now handles letter-prefix sections via parse_section() and
    assigns section_number, so they pass the first check above.
    """
    text = (node.get("text") or "").strip()

    # Stage 4 already resolved a real section number → trust it
    if node.get("section_number"):
        return True

    # Matches a well-known academic section name
    if text.lower() in COMMON_SECTIONS:
        return True

    # Numbered section pattern
    if NUMBERED.match(text):
        return True

    # Roman numeral section pattern
    if ROMAN.match(text):
        return True

    # Everything else is metadata / non-section
    return False

# ==========================================================
# GraphML Sanitization
# ==========================================================
# GraphML only supports: str, int, float, bool.
# None, dict, list, tuple, and any other Python object will
# crash nx.write_graphml().  The helpers below convert every
# attribute value to a GraphML-safe primitive BEFORE the
# graph is handed to the exporter.  The original NetworkX
# graph (and graph.json) are left untouched.
# ==========================================================

# Default fallback values when None is encountered for
# well-known attribute names.  For any unknown attribute
# that is None we fall back to the empty-string sentinel.
_NONE_DEFAULTS: dict = {
    "page":           -1,
    "text":           "",
    "section":        "",
    "title":          "",
    "type":           "",
    "relation":       "",
    "docling_ref":    "",
    "label":          "",
    "level":          -1,
    "parent_section": "",
    "reading_order":  -1,
    "char_count":     0,
    "word_count":     0,
}


def _sanitize_value(value, key: str = "") -> str | int | float | bool:
    """
    Recursively convert *value* into a GraphML-safe primitive.

    Rules
    -----
    - None      → type-appropriate default from _NONE_DEFAULTS, else ""
    - bool      → kept as-is  (GraphML supports xs:boolean)
    - int/float → kept as-is
    - str       → kept as-is
    - dict      → JSON-serialised string
    - list      → JSON-serialised string
    - tuple     → JSON-serialised string (converted to list first)
    - anything else → str(value)
    """
    if value is None:
        return _NONE_DEFAULTS.get(key, "")

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return value

    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        # Recursively sanitize the dict's values, then serialise.
        safe_dict = {k: _sanitize_value(v, k) for k, v in value.items()}
        return json.dumps(safe_dict, ensure_ascii=False)

    if isinstance(value, (list, tuple)):
        # Recursively sanitize each element, then serialise.
        safe_list = [_sanitize_value(item) for item in value]
        return json.dumps(safe_list, ensure_ascii=False)

    # Fallback: stringify anything else (e.g. custom objects).
    return str(value)


def _sanitize_attr_dict(attrs: dict) -> dict:
    """Return a new dict with every value replaced by its sanitized form."""
    return {k: _sanitize_value(v, k) for k, v in attrs.items()}


def make_graphml_safe(G: nx.DiGraph) -> nx.DiGraph:
    """
    Return a *deep copy* of *G* where every node attribute and every
    edge attribute has been sanitized to a GraphML-compatible primitive.

    The original graph *G* is never modified.

    The copy is suitable for:
      - nx.write_graphml()
      - Gephi / Neo4j / Cytoscape / NetworkX import
    """
    H: nx.DiGraph = copy.deepcopy(G)

    # Sanitize node attributes
    for node_id, attr in H.nodes(data=True):
        safe = _sanitize_attr_dict(attr)
        H.nodes[node_id].clear()
        H.nodes[node_id].update(safe)

    # Sanitize edge attributes
    for u, v, attr in H.edges(data=True):
        safe = _sanitize_attr_dict(attr)
        H.edges[u, v].clear()
        H.edges[u, v].update(safe)

    return H

# ==========================================================
# Node Attribute Helpers
# ==========================================================

def _semantic_flags(node_type: str, label: str = "") -> dict:
    """
    Return a dict of boolean semantic flags for a given mapped node type.
    Avoids repeated isinstance / string checks in later pipeline stages.
    """
    return {
        "is_section":   node_type == "Section",
        "is_paragraph": node_type == "Paragraph",
        "is_formula":   node_type == "Formula",
        "is_figure":    node_type == "Figure",
        "is_table":     node_type == "Table",
        "is_list":      node_type == "List",
        "is_footnote":  label == "footnote",
    }


def _text_stats(text: str | None) -> dict:
    """
    Return character count and word count for a text string.
    Returns zeros when text is absent.
    """
    if not text:
        return {"char_count": 0, "word_count": 0}
    return {
        "char_count": len(text),
        "word_count": len(text.split()),
    }

# ==========================================================
# Graph Builder
# ==========================================================

def build_graph(ir: dict) -> tuple[nx.DiGraph, dict]:
    """
    Convert an Intermediate Representation (IR) dict into:
      - a NetworkX DiGraph  (raw, with original Python types)
      - a graph_json dict   (for graph.json; also raw)

    None values are preserved here intentionally so that
    graph.json faithfully represents the source data.
    GraphML sanitization is applied separately at export time.
    """

    G = nx.DiGraph()

    graph_json = {
        "paper_id": ir["paper_id"],
        "nodes":    [],
        "edges":    [],
    }

    # ----------------------------------------------------------
    # Identify the paper-title node
    # ----------------------------------------------------------
    # All SectionHeaderItems that appear before the first real
    # section header are treated as metadata/title nodes.  The
    # last such node is tracked as paper_title_id so it can be
    # suppressed from the Section graph.
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # paper_title_id logic has been removed so that metadata
    # (including authors parsed as headers) are not dropped.
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Identify the first real section header id
    # ----------------------------------------------------------
    # All content nodes that appear before this (section_parent=None
    # and not SectionHeaderItem) are metadata nodes (authors,
    # affiliations, etc.) and will receive HAS_METADATA edges from
    # the Paper node.
    # ----------------------------------------------------------

    first_section_idx = None
    first_section_id = None # Keep for compatibility if needed elsewhere
    
    for idx, node in enumerate(ir["nodes"]):
        if node["type"] == "SectionHeaderItem":
            # Must also be a 'real' section (Stage 4 identified it, or it matches headers)
            if is_real_section(node):
                first_section_idx = idx
                first_section_id = node["id"]
                break

    # ----------------------------------------------------------
    # Build a section lookup table  {node_id -> section_node}
    # ----------------------------------------------------------
    # Keyed by numeric IR id.  Used to propagate section_number
    # and section_title to every content node without repeated
    # linear searches through ir["nodes"].
    # ----------------------------------------------------------

    section_lookup: dict[int, dict] = {
        node["id"]: node
        for node in ir["nodes"]
        if node["type"] == "SectionHeaderItem" and is_real_section(node)
    }

    # ----------------------------------------------------------
    # Build a reading-order index  {node_id -> int}
    # ----------------------------------------------------------
    # Docling already provides traversal order via the prev_node /
    # next_node linked list.  The position in ir["nodes"] mirrors
    # that order, so we simply use enumeration here.
    # ----------------------------------------------------------

    reading_order_index: dict[int, int] = {
        node["id"]: idx
        for idx, node in enumerate(ir["nodes"])
    }

    # ----------------------------------------------------------
    # Paper node
    # ----------------------------------------------------------

    paper_node = "paper"

    G.add_node(
        paper_node,
        type="Paper",
        title=ir["title"],
    )

    graph_json["nodes"].append({
        "id":    paper_node,
        "type":  "Paper",
        "title": ir["title"],
    })

    # ----------------------------------------------------------
    # Document content nodes
    # ----------------------------------------------------------

    for node in ir["nodes"]:



        node_type = TYPE_MAP.get(node["type"], node["type"])
        if node["type"] == "SectionHeaderItem" and not is_real_section(node):
            node_type = "Paragraph"
            
        node_id   = f"n_{node['id']}"

        # bbox may be a dict or list – kept raw for JSON, will be
        # serialised to string at GraphML export time.
        bbox = node.get("bbox")

        # ----------------------------------------------------------
        # Propagate section metadata from the parent section.
        # Content nodes in the IR have section_number=null and
        # section_title=null; the real values live on their
        # SectionHeaderItem parent.
        # ----------------------------------------------------------

        parent_id_raw = node.get("section_parent")   # numeric IR id or None

        if node["type"] == "SectionHeaderItem" and is_real_section(node):
            # Section nodes carry their own section_number / section_title.
            section_number = node.get("section_number")
            section_title  = node.get("section_title")
            parent_section = (
                f"n_{parent_id_raw}" if parent_id_raw is not None else None
            )
        else:
            # Content nodes: look up section info from the parent section.
            if parent_id_raw is not None and parent_id_raw in section_lookup:
                sec_node       = section_lookup[parent_id_raw]
                section_number = sec_node.get("section_number")
                section_title  = sec_node.get("section_title")
            else:
                section_number = node.get("section_number")
                section_title  = node.get("section_title")

            parent_section = (
                f"n_{parent_id_raw}" if parent_id_raw is not None else None
            )

        # ----------------------------------------------------------
        # Compute new enrichment attributes
        # ----------------------------------------------------------

        reading_order = reading_order_index.get(node["id"])
        stats         = _text_stats(node.get("text"))
        flags         = _semantic_flags(node_type, node.get("label", ""))

        G.add_node(
            node_id,
            type           = node_type,
            text           = node["text"],
            page           = node["page"],
            section        = section_number,
            title          = section_title,
            parent_section = parent_section,
            docling_ref    = node.get("docling_ref"),
            label          = node.get("label"),
            level          = node.get("level"),
            bbox           = bbox,
            reading_order  = reading_order,
            **stats,
            **flags,
        )

        graph_json["nodes"].append({
            "id":             node_id,
            "type":           node_type,
            "text":           node["text"],
            "page":           node["page"],
            "section":        section_number,
            "title":          section_title,
            "parent_section": parent_section,
            "docling_ref":    node.get("docling_ref"),
            "label":          node.get("label"),
            "level":          node.get("level"),
            "bbox":           bbox,
            "reading_order":  reading_order,
            **stats,
            **flags,
        })

    # ----------------------------------------------------------
    # Paper → Metadata nodes  (HAS_METADATA)
    # ----------------------------------------------------------
    # Content nodes that appear before the first real section
    # header AND have no section_parent are pre-abstract metadata
    # (author names, affiliations, emails, keywords, etc.).
    # Connect them to the Paper node so they are not isolated.
    # ----------------------------------------------------------

    for idx, node in enumerate(ir["nodes"]):

        # Skip actual section headers, but keep metadata headers (e.g., author names)
        if node["type"] == "SectionHeaderItem" and is_real_section(node):
            continue

        # Already claimed by a section — skip
        if node["section_parent"] is not None:
            continue

        # Stop once we pass the first real section header
        if first_section_idx is not None and idx >= first_section_idx:
            break

        node_id = f"n_{node['id']}"

        G.add_edge(paper_node, node_id, relation="HAS_METADATA")

        graph_json["edges"].append({
            "source":   paper_node,
            "target":   node_id,
            "relation": "HAS_METADATA",
        })

    # ----------------------------------------------------------
    # Paper → Top-level sections  (HAS_SECTION)
    # ----------------------------------------------------------

    for node in ir["nodes"]:

        if node["type"] != "SectionHeaderItem" or not is_real_section(node):
            continue



        node_id = f"n_{node['id']}"

        if node["section_parent"] is None:

            G.add_edge(paper_node, node_id, relation="HAS_SECTION")

            graph_json["edges"].append({
                "source":   paper_node,
                "target":   node_id,
                "relation": "HAS_SECTION",
            })

    # ----------------------------------------------------------
    # Section hierarchy  (HAS_SUBSECTION)
    # ----------------------------------------------------------

    for node in ir["nodes"]:

        if node["type"] != "SectionHeaderItem" or not is_real_section(node):
            continue



        node_id = f"n_{node['id']}"
        parent  = node["section_parent"]

        if parent is not None:

            parent_id = f"n_{parent}"
            relation  = "HAS_SUBSECTION"

            G.add_edge(parent_id, node_id, relation=relation)

            graph_json["edges"].append({
                "source":   parent_id,
                "target":   node_id,
                "relation": relation,
            })

    # ----------------------------------------------------------
    # Section → Content  (HAS_PARAGRAPH / HAS_FORMULA / …)
    # ----------------------------------------------------------

    relation_map = {
        "Paragraph": "HAS_PARAGRAPH",
        "Formula":   "HAS_FORMULA",
        "Figure":    "HAS_FIGURE",
        "Table":     "HAS_TABLE",
        "List":      "HAS_LIST",
    }

    for node in ir["nodes"]:

        if node["type"] == "SectionHeaderItem" and is_real_section(node):
            continue

        parent = node["section_parent"]

        if parent is None:
            continue

        parent_id = f"n_{parent}"
        node_id   = f"n_{node['id']}"
        node_type = TYPE_MAP.get(node["type"], node["type"])
        relation  = relation_map.get(node_type)

        if relation is None:
            continue

        G.add_edge(parent_id, node_id, relation=relation)

        graph_json["edges"].append({
            "source":   parent_id,
            "target":   node_id,
            "relation": relation,
        })

    # ----------------------------------------------------------
    # Reading order  (NEXT)
    # ----------------------------------------------------------

    for node in ir["nodes"]:

        nxt = node["next_node"]

        if nxt is None:
            continue



        G.add_edge(
            f"n_{node['id']}",
            f"n_{nxt}",
            relation="NEXT",
        )

        graph_json["edges"].append({
            "source":   f"n_{node['id']}",
            "target":   f"n_{nxt}",
            "relation": "NEXT",
        })

    return G, graph_json

# ==========================================================
# MAIN
# ==========================================================

def process_paper(paper_dir: Path, output_dir: Path):
    ir_file = paper_dir / "graph_stage2.json"
    if not ir_file.exists():
        return None

    with open(ir_file, encoding="utf8") as f:
        ir = json.load(f)

    G, graph = build_graph(ir)

    out_dir = output_dir / paper_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- JSON (unchanged – raw Python types, None preserved) ----
    json_path = out_dir / "graph.json"
    with open(json_path, "w", encoding="utf8") as f:
        json.dump(graph, f, indent=4, ensure_ascii=False)

    # ---- GraphML (sanitized deep copy, original G untouched) ----
    G_safe = make_graphml_safe(G)
    nx.write_graphml(G_safe, out_dir / "graph.graphml")

    return json_path

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper_dir in tqdm(papers):
        process_paper(paper_dir, OUTPUT_DIR)
    print("\nDone.")