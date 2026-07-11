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
OUTPUT_DIR = Path("processed3")

OUTPUT_DIR.mkdir(exist_ok=True)

pipeline_options = PdfPipelineOptions()

# arXiv PDFs are digital
pipeline_options.do_ocr = False

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)


# ============================================================
# METADATA EXTRACTION
# ============================================================

def extract_metadata(pdf_path: Path):

    result = converter.convert(pdf_path)

    doc = result.document

    metadata = {
        "paper_id": pdf_path.stem,
        "title": "",
        "pages": 0,
    }

    # -----------------------------
    # title
    # -----------------------------

    for item, level in doc.iterate_items():

        if hasattr(item, "label"):

            if str(item.label) == "TITLE":

                metadata["title"] = item.text.strip()

                break

    # -----------------------------
    # number of pages
    # -----------------------------

    metadata["pages"] = len(doc.pages)

    return metadata


# ============================================================
# MAIN
# ============================================================

pdfs = sorted(PDF_DIR.glob("*.pdf"))

for pdf in tqdm(pdfs):

    paper_dir = OUTPUT_DIR / pdf.stem

    paper_dir.mkdir(parents=True, exist_ok=True)

    metadata = extract_metadata(pdf)

    with open(
        paper_dir / "metadata.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
            ensure_ascii=False
        )

print("\nDone.")