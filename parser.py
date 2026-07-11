import fitz
import json
import re
from pathlib import Path
from tqdm import tqdm

# ===========================================================
# CONFIG
# ===========================================================

PDF_DIR = Path("pdfs")
OUTPUT_DIR = Path("processed/json")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===========================================================
# SECTION REGEX
# ===========================================================

SECTION_PATTERN = re.compile(
    r"^(\d+(\.\d+)*)(\s+)(.+)$"
)

# ===========================================================
# HELPERS
# ===========================================================

def is_section_heading(text):
    text = text.strip()

    if len(text) > 150:
        return False

    return SECTION_PATTERN.match(text)


# ===========================================================
# PARSER
# ===========================================================

def parse_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    paper = {

        "paper_id": pdf_path.stem,

        "pages": [],

        "nodes": []
    }

    node_id = 0

    current_section = None

    # --------------------------------------------

    for page_number in range(len(doc)):

        page = doc.load_page(page_number)

        blocks = page.get_text("dict")["blocks"]

        page_node = {

            "page": page_number + 1,

            "blocks": []
        }

        # ----------------------------------------

        for block in blocks:

            if "lines" not in block:
                continue

            spans = []

            for line in block["lines"]:

                for span in line["spans"]:

                    spans.append(span["text"])

            text = " ".join(spans).strip()

            if text == "":
                continue

            bbox = block["bbox"]

            node = {

                "id": f"node_{node_id}",

                "page": page_number + 1,

                "bbox": bbox,

                "text": text,

                "type": "paragraph",

                "parent": current_section,

                "children": []
            }

            # ------------------------------------
            # SECTION DETECTION
            # ------------------------------------

            match = is_section_heading(text)

            if match:

                sec_no = match.group(1)

                sec_title = match.group(4)

                current_section = f"section_{sec_no}"

                node["type"] = "section"

                node["section_number"] = sec_no

                node["section_title"] = sec_title

            paper["nodes"].append(node)

            page_node["blocks"].append(node["id"])

            node_id += 1

        paper["pages"].append(page_node)

    doc.close()

    return paper


# ===========================================================
# MAIN
# ===========================================================

pdfs = sorted(PDF_DIR.glob("*.pdf"))

for pdf in tqdm(pdfs):

    result = parse_pdf(pdf)

    out_file = OUTPUT_DIR / f"{pdf.stem}.json"

    with open(out_file, "w", encoding="utf-8") as f:

        json.dump(result, f, indent=2, ensure_ascii=False)

print("\nDone.")