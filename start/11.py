from pathlib import Path
import json
import faiss
from sentence_transformers import SentenceTransformer

# ==========================================================
# CONFIG
# ==========================================================

INDEX_DIR = Path("faiss_index3")
CHUNK_DIR = Path("semantic_chunks4")

MODEL_NAME = "BAAI/bge-base-en-v1.5"

TOP_K = 5

# ==========================================================
# LOAD MODEL
# ==========================================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")

index = faiss.read_index(
    str(INDEX_DIR / "index.faiss")
)

with open(
    INDEX_DIR / "index_metadata.json",
    encoding="utf8"
) as f:
    metadata = json.load(f)

print("Ready.")

# ==========================================================
# CACHE CHUNKS
# ==========================================================

print("Loading chunks...")

chunk_db = {}

papers = sorted(CHUNK_DIR.glob("*"))

for paper in papers:

    chunk_file = paper / "chunks.json"

    if not chunk_file.exists():
        continue

    with open(chunk_file, encoding="utf8") as f:
        chunks = json.load(f)

    for chunk in chunks:

        key = (
            chunk["paper_id"],
            chunk["chunk_id"]
        )

        chunk_db[key] = chunk

print(f"Loaded {len(chunk_db)} chunks.")

# ==========================================================
# SEARCH
# ==========================================================

def search(query, k=TOP_K):

    embedding = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    scores, ids = index.search(
        embedding,
        k
    )

    results = []

    for score, idx in zip(scores[0], ids[0]):

        if idx < 0:
            continue

        meta = metadata[idx]

        key = (
            meta["paper_id"],
            meta["chunk_id"]
        )

        chunk = chunk_db.get(key)

        if chunk is None:
            continue

        results.append({

            "score": float(score),

            "paper_id": meta["paper_id"],

            "chunk_id": meta["chunk_id"],

            "chunk_type": meta["chunk_type"],

            "section_number":
                chunk.get("section_number"),

            "section_title":
                chunk.get("section_title"),

            "page_start":
                chunk.get("page_start"),

            "page_end":
                chunk.get("page_end"),

            "word_count":
                chunk.get("word_count"),

            "text":
                chunk.get("text", "")

        })

    return results

# ==========================================================
# MAIN
# ==========================================================

while True:

    print()

    query = input("Query : ").strip()

    if query.lower() in ["exit", "quit"]:
        break

    results = search(query)

    print()
    print("=" * 100)

    for i, r in enumerate(results, 1):

        print()

        print(f"[{i}]")

        print(f"Score        : {r['score']:.4f}")

        print(f"Paper        : {r['paper_id']}")

        print(f"Chunk        : {r['chunk_id']}")

        print(f"Type         : {r['chunk_type']}")

        print(f"Section      : {r['section_number']}")

        print(f"Title        : {r['section_title']}")

        print(f"Pages        : {r['page_start']} - {r['page_end']}")

        print(f"Words        : {r['word_count']}")

        print()

        text = r["text"]

        if len(text) > 600:
            text = text[:600] + "..."

        print(text)

        print("-" * 100)