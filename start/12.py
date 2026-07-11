from pathlib import Path
import json
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("semantic_chunks4")

OUTPUT_DIR = Path("paper_registry")

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# BUILD REGISTRY
# ==========================================================

registry = []

papers = sorted(INPUT_DIR.glob("*"))

for paper in tqdm(papers):

    chunk_file = paper / "chunks.json"

    if not chunk_file.exists():
        continue

    with open(chunk_file, encoding="utf8") as f:

        chunks = json.load(f)

    if len(chunks) == 0:
        continue

    # --------------------------------------------

    metadata = None

    for c in chunks:

        if c["chunk_type"] == "metadata":

            metadata = c

            break

    if metadata is None:
        continue

    # --------------------------------------------

    section_chunks = [

        c

        for c in chunks

        if c["chunk_type"] == "section"

    ]

    titles = [

        c.get("section_title", "")

        for c in section_chunks

    ]

    registry.append({

        "paper_id":

            metadata["paper_id"],

        "title":

            metadata.get("title"),

        "authors":

            metadata.get("authors", []),

        "affiliations":

            metadata.get("affiliations", []),

        "keywords":

            metadata.get("keywords", []),

        "pages":

            metadata.get("pages"),

        "num_chunks":

            len(chunks),

        "num_sections":

            len(section_chunks),

        "section_titles":

            titles,

        "has_references":

            any(

                t == "References"

                for t in titles

            ),

        "has_acknowledgement":

            any(

                "acknowled"

                in t.lower()

                for t in titles

                if t

            )

    })

# ==========================================================
# SAVE
# ==========================================================

registry.sort(

    key=lambda x: x["title"] or ""

)

with open(

    OUTPUT_DIR / "papers.json",

    "w",

    encoding="utf8"

) as f:

    json.dump(

        registry,

        f,

        indent=4,

        ensure_ascii=False

    )

# ==========================================================
# SUMMARY
# ==========================================================

print()

print("=" * 70)

print("Total Papers :", len(registry))

print()

for p in registry[:5]:

    print(p["title"])

print()

print("Registry saved.")