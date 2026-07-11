from pathlib import Path
import json
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("graph")
OUTPUT_DIR = Path("graph_stage3")

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# Helpers
# ==========================================================

SECTION_TYPES = {
    "SectionHeaderItem"
}

CONTENT_TYPES = {
    "TextItem",
    "FormulaItem",
    "PictureItem",
    "TableItem",
    "ListItem"
}

# ==========================================================
# Build hierarchy
# ==========================================================

def build_section_graph(ir):

    nodes = ir["nodes"]

    current_sections = {}

    for node in nodes:

        node["section_parent"] = None
        node["section_children"] = []

    # ----------------------------------------------
    # Walk through reading order
    # ----------------------------------------------

    for node in nodes:

        if node["type"] == "SectionHeaderItem":

            level = node["level"]

            current_sections[level] = node["id"]

            # remove deeper levels

            remove = []

            for l in current_sections:

                if l > level:
                    remove.append(l)

            for l in remove:
                del current_sections[l]

            # parent section

            parent = None

            for l in sorted(current_sections.keys()):

                if l < level:
                    parent = current_sections[l]

            node["section_parent"] = parent

            if parent is not None:

                nodes[parent]["section_children"].append(node["id"])

        else:

            if len(current_sections):

                deepest = max(current_sections.keys())

                parent = current_sections[deepest]

                node["section_parent"] = parent

                nodes[parent]["section_children"].append(node["id"])

    return ir

# ==========================================================
# MAIN
# ==========================================================

papers = sorted(INPUT_DIR.glob("*"))

for paper_dir in tqdm(papers):

    file = paper_dir / "graph_stage1.json"

    if not file.exists():
        continue

    with open(file, encoding="utf-8") as f:

        ir = json.load(f)

    ir = build_section_graph(ir)

    out = OUTPUT_DIR / paper_dir.name

    out.mkdir(exist_ok=True)

    with open(out / "graph_stage2.json", "w", encoding="utf-8") as f:

        json.dump(
            ir,
            f,
            indent=4,
            ensure_ascii=False
        )

print("\nFinished.")