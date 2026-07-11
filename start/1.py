from pathlib import Path
import json
from tqdm import tqdm

from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    InputFormat,
)
from docling.datamodel.pipeline_options import PdfPipelineOptions

# ============================================================
# CONFIG
# ============================================================

PDF_DIR = Path("pdfs")
OUTPUT_DIR = Path("pro4")

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False

_converter = None

def get_converter():
    global _converter
    if _converter is None:
        print("Loading Docling models...")
        _converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )
        print("Docling models loaded.")
    return _converter

# ============================================================
# HELPERS
# ============================================================

def get_page(item):
    if hasattr(item, "prov") and item.prov:
        return item.prov[0].page_no
    return None


def get_bbox(item):
    if hasattr(item, "prov") and item.prov:
        b = item.prov[0].bbox
        return {
            "left": b.l,
            "top": b.t,
            "right": b.r,
            "bottom": b.b
        }
    return None


def get_text(item):
    if hasattr(item, "text") and item.text:
        return item.text.strip()

    if hasattr(item, "orig") and item.orig:
        return item.orig.strip()

    return ""


# ============================================================
# CONVERT
# ============================================================

def convert_pdf(pdf_path):
    converter = get_converter()
    result = converter.convert(pdf_path)
    doc = result.document

    ir = {
        "paper_id": pdf_path.stem,
        "title": "",
        "num_pages": len(doc.pages),
        "nodes": [],
        "docling_index": {}
    }

    # -------------------------------------------
    # Build nodes
    # -------------------------------------------

    for idx, (item, level) in enumerate(doc.iterate_items()):

        doc_ref = getattr(item, "self_ref", None)

        node = {
            "id": idx,
            "docling_ref": doc_ref,
            "type": type(item).__name__,
            "label": str(getattr(item, "label", "")),
            "level": level,

            "text": get_text(item),

            "page": get_page(item),
            "bbox": get_bbox(item),

            "parent_ref":
                getattr(item.parent, "cref", None)
                if hasattr(item, "parent") and item.parent
                else None,

            "children_refs":
                [c.cref for c in getattr(item, "children", [])],

            "caption_refs":
                [c.cref for c in getattr(item, "captions", [])],

            "reference_refs":
                [c.cref for c in getattr(item, "references", [])],

            "prev_node": idx - 1 if idx > 0 else None,
            "next_node": None
        }

        if idx > 0:
            ir["nodes"][-1]["next_node"] = idx

        if node["label"] == "section_header" and ir["title"] == "":
            ir["title"] = node["text"]

        if doc_ref is not None:
            ir["docling_index"][doc_ref] = idx

        ir["nodes"].append(node)

    return ir


# ============================================================
# MAIN
# ============================================================

def process_pdf(pdf_path: Path, output_dir: Path):
    print(f"Processing {pdf_path.name}")
    out_dir = output_dir / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    ir = convert_pdf(pdf_path)
    with open(out_dir / "ir.json", "w", encoding="utf-8") as f:
        json.dump(ir, f, indent=4, ensure_ascii=False)
    return out_dir / "ir.json"

if __name__ == "__main__":
    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    for pdf in tqdm(pdfs):
        process_pdf(pdf, OUTPUT_DIR)
    print("\nFinished.")