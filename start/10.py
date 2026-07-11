from pathlib import Path
import json
import faiss
import numpy as np

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

        info = metadata[idx].copy()

        info["score"] = float(score)

        results.append(info)

    return results

# ==========================================================
# INTERACTIVE LOOP
# ==========================================================

while True:

    print()

    query = input("Query : ").strip()

    if query.lower() in ["exit", "quit"]:
        break

    results = search(query)

    print()

    print("=" * 80)

    for i, r in enumerate(results, 1):

        print()

        print(f"{i}. Score : {r['score']:.4f}")

        print("Paper :", r["paper_id"])

        print("Chunk :", r["chunk_id"])

        print("Section :", r.get("section_title"))