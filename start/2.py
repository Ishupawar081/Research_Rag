from pathlib import Path
import json
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("pro4")
OUTPUT_DIR = Path("graph4")

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# Resolve one paper
# ==========================================================

def resolve_graph(ir):

    # ---------------------------------------------
    # Build docling_ref -> node_id map
    # ---------------------------------------------

    ref_to_id = {}

    for node in ir["nodes"]:

        ref = node["docling_ref"]

        if ref:

            ref_to_id[ref] = node["id"]

    # ---------------------------------------------
    # Resolve references
    # ---------------------------------------------

    for node in ir["nodes"]:

        # parent

        p = node["parent_ref"]

        node["parent"] = ref_to_id.get(p)

        # children

        node["children"] = [

            ref_to_id[c]

            for c in node["children_refs"]

            if c in ref_to_id

        ]

        # captions

        node["captions"] = [

            ref_to_id[c]

            for c in node["caption_refs"]

            if c in ref_to_id

        ]

        # references

        node["references"] = [

            ref_to_id[c]

            for c in node["reference_refs"]

            if c in ref_to_id

        ]

    return ir


# ==========================================================
# MAIN
# ==========================================================

def process_paper(paper_dir: Path, output_dir: Path):
    ir_file = paper_dir / "ir.json"
    if not ir_file.exists():
        return None
    with open(ir_file, encoding="utf-8") as f:
        ir = json.load(f)
    graph = resolve_graph(ir)
    out_dir = output_dir / paper_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "graph_stage1.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4, ensure_ascii=False)
    return out_file

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper_dir in tqdm(papers):
        process_paper(paper_dir, OUTPUT_DIR)
    print("\nFinished.")