from pathlib import Path
import json
from tqdm import tqdm

from docling.document_converter import DocumentConverter

# ============================================================
# CONFIG
# ============================================================

PDF_DIR = Path("pdfs")
OUTPUT_DIR = Path("processed1/json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

converter = DocumentConverter()


# ============================================================
# PARSER
# ============================================================

def parse_pdf(pdf_path: Path):

    print(f"Parsing {pdf_path.name}")

    result = converter.convert(str(pdf_path))

    doc = result.document

    paper = {
        "paper_id": pdf_path.stem,
        "title": "",
        "nodes": []
    }

    node_id = 0

    # --------------------------------------------------------
    # Iterate through document items in reading order
    # --------------------------------------------------------

    for item, level in doc.iterate_items():

        node = {
            "id": f"node_{node_id}",
            "type": type(item).__name__,
            "level": level,
            "text": "",
            "parent": None,
            "children": [],
            "page": None
        }

        # --------------------------------------------
        # Text extraction
        # --------------------------------------------

        if hasattr(item, "text"):

            node["text"] = item.text

        # --------------------------------------------
        # Label
        # --------------------------------------------

        if hasattr(item, "label"):

            node["label"] = str(item.label)

        # --------------------------------------------
        # Page information
        # --------------------------------------------

        if hasattr(item, "prov") and item.prov:

            try:

                node["page"] = item.prov[0].page_no

            except Exception:

                pass

        # --------------------------------------------
        # Title
        # --------------------------------------------

        if node["label"] == "TITLE":

            paper["title"] = node["text"]

        paper["nodes"].append(node)

        node_id += 1

    return paper


# ============================================================
# MAIN
# ============================================================

pdfs = sorted(PDF_DIR.glob("*.pdf"))

for pdf in tqdm(pdfs):

    paper = parse_pdf(pdf)

    out_file = OUTPUT_DIR / f"{pdf.stem}.json"

    with open(out_file, "w", encoding="utf-8") as f:

        json.dump(
            paper,
            f,
            indent=2,
            ensure_ascii=False
        )

print("\nFinished.")