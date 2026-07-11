from pathlib import Path
import json
import re
from tqdm import tqdm

# ============================================================
# CONFIG
# ============================================================

INPUT_DIR  = Path("graph4")
OUTPUT_DIR = Path("graph_po4")

OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# REGEX
# ============================================================
# Supports all common research-paper numbering styles:
#   "1 Introduction"           → ("1", "Introduction")
#   "1. Introduction"          → ("1", "Introduction")
#   "2.1 Related Work"         → ("2.1", "Related Work")
#   "3.2.1. Details"           → ("3.2.1", "Details")
#   "I Introduction"           → ("1", "Introduction")       Roman
#   "II. Background"           → ("2", "Background")         Roman
#   "A Bounding the …"         → ("appendix_A", "Bounding…") Letter
#   "B. Data Guarantees"       → ("appendix_B", "Data…")     Letter
#   "C.1 Tightness of …"      → ("appendix_C.1", "Tight…")  Letter-sub
#   "A.2.1 Details"            → ("appendix_A.2.1", "Det…")  Letter-sub
# ============================================================

# Arabic numeric:  "1 Title" / "2.1. Title" / "3.2.1 Title"
SECTION_RE = re.compile(
    r"^(\d+(?:\.\d+)*)\.?\s+(.+)$"
)

# Roman numeral:  "I Title" / "II. Title" / "XIV Title"
# Supports I–XX (covers virtually all conference papers).
ROMAN_RE = re.compile(
    r"^(I{1,3}|IV|VI{0,3}|IX|X{1,3}|XI{1,3}|XIV|XV|XVI{0,3}|XIX|XX)\.?\s+(.+)$",
    re.IGNORECASE,
)

# Single-letter appendix:  "A Title" / "B. Title"
# Restricted to uppercase A–Z followed by dot-or-space then ≥2 title words
# to avoid matching author initials like "T. Zhang".
LETTER_RE = re.compile(
    r"^([A-Z])\.?\s+(\S+(?:\s+\S+)+)$"
)

# Common unnumbered academic sections
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
    "bibliography",
    "appendix",
    "acknowledgements",
    "acknowledgments",
}

# Letter-dot-number subsection:  "C.1 Title" / "A.2.1 Title" / "B.3. Title"
LETTER_NUM_RE = re.compile(
    r"^([A-Z](?:\.\d+)+)\.?\s+(.+)$"
)

# ============================================================
# Roman numeral → Arabic conversion
# ============================================================

_ROMAN_MAP = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
    "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
    "XI": 11, "XII": 12, "XIII": 13, "XIV": 14, "XV": 15,
    "XVI": 16, "XVII": 17, "XVIII": 18, "XIX": 19, "XX": 20,
}


def _roman_to_arabic(roman: str) -> str:
    """Convert a Roman numeral string to its Arabic string equivalent."""
    return str(_ROMAN_MAP.get(roman.upper(), roman))


# ============================================================
# Helpers
# ============================================================

def parse_section(text: str, seen_references: bool = False) -> tuple[str, str] | None:
    """
    Try to parse a SectionHeaderItem text into
    (section_number, section_title).

    Returns None when the text is not a recognisable section
    header (e.g. author name, affiliation, venue string).

    Supported formats:
      Named:   "Abstract", "References …", "Appendix …",
               "Acknowledgements" / "Acknowledgments"
      Numeric: "1 Introduction" / "2.1. Dataset"
      Roman:   "I Introduction" / "II. Background"
      Letter:  "A Bounding …" / "B. Data Guarantees" (only after references)
      Letter-sub: "C.1 Tightness …" / "A.2.1 Details" (only after references)

    The returned section_number never contains a trailing dot.
    """

    text = text.strip()
    lower = text.lower()

    # ----------------------------------------------------------
    # Named special sections and common unnumbered sections
    # ----------------------------------------------------------

    if lower in COMMON_SECTIONS:
        if lower in ("acknowledgments", "acknowledgements"):
            return ("acknowledgements", text)
        if lower == "bibliography":
            return ("references", text)
        return (lower, text)

    # Some papers prefix references or appendix with numbers, or don't.
    # We still want to catch them if they *start* with these keywords.
    if lower.startswith("references") or lower.startswith("bibliography"):
        return ("references", text)

    if lower.startswith("appendix"):
        return ("appendix", text)

    # ----------------------------------------------------------
    # Numbered section  "1 Introduction" / "2.1. Dataset"
    # ----------------------------------------------------------

    m = SECTION_RE.match(text)
    if m is not None:
        section_number = m.group(1)          # no trailing dot
        section_title  = m.group(2).strip()
        return (section_number, section_title)

    # ----------------------------------------------------------
    # Letter-dot-number subsection  "C.1 Tightness" / "A.2.1 X"
    # (checked BEFORE single-letter to avoid "C.1" matching "C")
    # Only matched if we have seen the references section.
    # ----------------------------------------------------------

    if seen_references:
        m = LETTER_NUM_RE.match(text)
        if m is not None:
            raw_num       = m.group(1)            # e.g. "C.1"
            section_title = m.group(2).strip()
            section_number = f"appendix_{raw_num}"  # → "appendix_C.1"
            return (section_number, section_title)

    # ----------------------------------------------------------
    # Roman numeral section  "I Introduction" / "XIV Experiments"
    # ----------------------------------------------------------

    m = ROMAN_RE.match(text)
    if m is not None:
        arabic        = _roman_to_arabic(m.group(1))
        section_title = m.group(2).strip()
        return (arabic, section_title)

    # ----------------------------------------------------------
    # Single-letter appendix  "A Bounding …" / "B. Data …"
    # Only matched if we have seen the references section.
    # ----------------------------------------------------------

    if seen_references:
        m = LETTER_RE.match(text)
        if m is not None:
            letter        = m.group(1).upper()
            section_title = m.group(2).strip()
            section_number = f"appendix_{letter}"   # → "appendix_A"
            return (section_number, section_title)

    return None


# ============================================================
# Build hierarchy
# ============================================================

def build_graph(ir: dict) -> dict:
    """
    Assign section hierarchy metadata to every node in the IR.

    Algorithm
    ---------
    1. Reset all hierarchy fields on every node.
    2. Walk nodes in document order.
    3. For SectionHeaderItems:
       - parse section number / title
       - compute level = len(section_number.split("."))
         (e.g. "2.1" → level 2, "1" → level 1)
       - pop the stack until it holds at most (level-1) items
       - the top of the stack after popping is the parent
       - push current section
    4. For all other nodes:
       - assign section_parent = current innermost section

    This correctly handles all nesting depths including
    gaps (jumping from 1 to 2.1) and special sections.
    """

    nodes = ir["nodes"]

    # ----------------------------------------------------------
    # 1. Initialise all hierarchy fields
    # ----------------------------------------------------------

    for node in nodes:
        node["section_parent"]   = None
        node["section_children"] = []
        node["section_number"]   = None
        node["section_title"]    = None

    # ----------------------------------------------------------
    # 1.5 Pre-pass to detect inline abstracts
    # ----------------------------------------------------------
    # Some publishers format the abstract as a single TextItem block
    # starting with "ABSTRACT" or "Abstract -", skipping a section header.
    # We dynamically insert a synthetic SectionHeaderItem so that it's
    # parsed as an abstract section.
    
    new_nodes = []
    dummy_counter = max((n["id"] for n in nodes), default=0) + 1
    seen_abstract = False
    
    for node in nodes:
        if node["type"] != "SectionHeaderItem" and not seen_abstract:
            text_lower = str(node.get("text", "")).lower().strip()
            # Must start with "abstract" followed by whitespace or common delimiters,
            # and contain enough words to be an actual inline block.
            if re.match(r"^abstract(?:[\s:\-].*)?$", text_lower) and len(text_lower.split()) > 3:
                seen_abstract = True
                dummy_id = dummy_counter
                dummy_counter += 1
                
                prev_id = node.get("prev_node")
                dummy_node = {
                    "id": dummy_id,
                    "type": "SectionHeaderItem",
                    "text": "Abstract",
                    "page": node.get("page"),
                    "section_parent": None,
                    "section_children": [],
                    "section_number": None,
                    "section_title": None,
                    "prev_node": prev_id,
                    "next_node": node["id"],
                }
                
                # Update the previous node in the linked list
                if prev_id is not None:
                    for n in reversed(new_nodes):
                        if n["id"] == prev_id:
                            n["next_node"] = dummy_id
                            break
                            
                # Update the current node to point back to the dummy
                node["prev_node"] = dummy_id
                
                new_nodes.append(dummy_node)
                
        # Ensure every node has next_node / prev_node to avoid KeyError
        if "next_node" not in node: node["next_node"] = None
        if "prev_node" not in node: node["prev_node"] = None
        
        new_nodes.append(node)
        
    nodes = new_nodes
    ir["nodes"] = nodes

    # ----------------------------------------------------------
    # 2. Stack-based traversal
    # ----------------------------------------------------------
    # section_stack holds (level, node_id) pairs.
    # current_section is the id of the innermost open section.
    # ----------------------------------------------------------

    section_stack:   list[tuple[int, int]] = []
    current_section: int | None            = None
    seen_references: bool                  = False

    for node in nodes:

        # ------------------------------------------------------
        # Non-section nodes: attach to current innermost section
        # ------------------------------------------------------

        if node["type"] != "SectionHeaderItem":

            if current_section is not None:

                node["section_parent"] = current_section

                nodes[current_section]["section_children"].append(
                    node["id"]
                )

            continue

        # ------------------------------------------------------
        # SectionHeaderItem: try to parse a real section header
        # ------------------------------------------------------

        parsed = parse_section(node["text"], seen_references=seen_references)

        if parsed is None:
            # Not a real section (author name, affiliation, …)
            # Leave hierarchy fields as None and skip.
            continue

        sec_no, sec_title = parsed

        if sec_no == "references":
            seen_references = True

        node["section_number"] = sec_no
        node["section_title"]  = sec_title

        # ------------------------------------------------------
        # Determine nesting level
        # ------------------------------------------------------
        # Named sections (abstract, references, appendix, …)
        # are treated as top-level (level 1) so they always
        # pop back to root and never become subsections.
        # ------------------------------------------------------

        if sec_no in ("abstract", "references",
                      "appendix", "acknowledgements"):
            level = 1
        elif sec_no.startswith("appendix_"):
            # "appendix_A" → level 1, "appendix_C.1" → level 2, etc.
            suffix = sec_no[len("appendix_"):]   # e.g. "A" or "C.1"
            level = len(suffix.split("."))        # "A"→1, "C.1"→2
        else:
            level = len(sec_no.split("."))

        # ------------------------------------------------------
        # Pop stack to find the correct parent
        # Pop everything at >= current level so the parent is
        # always strictly shallower than the incoming section.
        # ------------------------------------------------------

        while section_stack and section_stack[-1][0] >= level:
            section_stack.pop()

        if section_stack:
            parent_id = section_stack[-1][1]
            node["section_parent"] = parent_id
            nodes[parent_id]["section_children"].append(node["id"])

        # Push current section
        section_stack.append((level, node["id"]))
        current_section = node["id"]

    return ir


# ============================================================
# MAIN
# ============================================================

def process_paper(paper_dir: Path, output_dir: Path):
    file = paper_dir / "graph_stage1.json"
    if not file.exists():
        return None

    with open(file, encoding="utf-8") as f:
        ir = json.load(f)

    ir = build_graph(ir)

    # ----------------------------------------------------------
    # Debug output — verify hierarchy parsing
    # ----------------------------------------------------------
    detected_sections = [
        node for node in ir["nodes"]
        if node["type"] == "SectionHeaderItem"
        and node["section_number"] is not None
    ]
    print(f"\nPaper: {ir.get('paper_id', paper_dir.name)}")
    print(f"Number of sections: {len(detected_sections)}")
    if detected_sections:
        print("First five detected sections:")
        for sec in detected_sections[:5]:
            print(f"  [{sec['section_number']}]  {sec['section_title']}  (node id={sec['id']})")

    # ----------------------------------------------------------
    # Write output
    # ----------------------------------------------------------
    out = output_dir / paper_dir.name
    out.mkdir(exist_ok=True, parents=True)
    out_file = out / "graph_stage2.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(ir, f, indent=4, ensure_ascii=False)
    
    return out_file

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper_dir in tqdm(papers):
        process_paper(paper_dir, OUTPUT_DIR)
    print("\nFinished.")