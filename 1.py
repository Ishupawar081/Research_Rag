import os
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================================
# CONFIG
# ==========================================================

DATA_DIR = "data"          # Folder containing the JSONL files
OUTPUT_DIR = "pdfs"        # PDFs will be saved here
NUM_PAPERS = 5             # Download first 5 papers from each file

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================================
# DOWNLOAD FUNCTION
# ==========================================================

def download_pdf(record):
    paper_id = record["id"]
    pdf_url = record["pdf_url"]

    save_path = os.path.join(OUTPUT_DIR, f"{paper_id}.pdf")

    # Skip if already downloaded
    if os.path.exists(save_path):
        return f"Skipped: {paper_id}"

    try:
        response = requests.get(pdf_url, timeout=60)
        response.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(response.content)

        return f"Downloaded: {paper_id}"

    except Exception as e:
        return f"Failed: {paper_id} ({e})"

# ==========================================================
# READ ALL JSONL FILES
# ==========================================================

papers = []

for jsonl_file in Path(DATA_DIR).glob("*.jsonl"):
    print(f"\nReading {jsonl_file.name}")

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= NUM_PAPERS:
                break

            try:
                papers.append(json.loads(line))
            except json.JSONDecodeError:
                continue

print(f"\nTotal papers to download: {len(papers)}")

# ==========================================================
# DOWNLOAD
# ==========================================================

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(download_pdf, p) for p in papers]

    for future in as_completed(futures):
        print(future.result())

print("\nDone!")