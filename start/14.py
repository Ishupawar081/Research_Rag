from pathlib import Path
import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

# ==========================================================
# CONFIG
# ==========================================================

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
FAISS_DIR = Path("faiss_index4")
CHUNK_DIR = Path("semantic_chunks_a4")
REGISTRY_FILE = Path("paper_registry2/papers.json")
TOP_K = 5

# ==========================================================
# LOAD MODEL
# ==========================================================

print("=" * 70)
print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Model loaded.")
print()

# ==========================================================
# LOAD FAISS INDEX
# ==========================================================

print("=" * 70)
print("Loading FAISS index...")
index = faiss.read_index(str(FAISS_DIR / "index.faiss"))
print("Vectors :", index.ntotal)
print()

# ==========================================================
# LOAD INDEX METADATA
# ==========================================================

print("=" * 70)
print("Loading index metadata...")
with open(FAISS_DIR / "index_metadata.json", encoding="utf8") as f:
    INDEX_METADATA = json.load(f)
print("Metadata entries :", len(INDEX_METADATA))
print()

# ==========================================================
# LOAD PAPER REGISTRY
# ==========================================================

print("=" * 70)
print("Loading paper registry...")
with open(REGISTRY_FILE, encoding="utf8") as f:
    PAPER_REGISTRY = json.load(f)
print("Registered papers :", len(PAPER_REGISTRY))
print()

# ==========================================================
# BUILD PAPER LOOKUP
# ==========================================================

PAPER_LOOKUP = {}
for paper in PAPER_REGISTRY:
    pid = paper["paper_id"]
    PAPER_LOOKUP[pid] = paper

# ==========================================================
# CHUNK CACHE
# ==========================================================

# Avoid reopening chunks.json repeatedly.
CHUNK_CACHE = {}

# ==========================================================
# LOAD CHUNKS OF ONE PAPER
# ==========================================================

def load_chunks(paper_id):
    if paper_id in CHUNK_CACHE:
        return CHUNK_CACHE[paper_id]

    chunk_file = CHUNK_DIR / paper_id / "chunks.json"

    if not chunk_file.exists():
        return {}

    with open(chunk_file, encoding="utf8") as f:
        chunks = json.load(f)

    lookup = {}
    for chunk in chunks:
        lookup[chunk["chunk_id"]] = chunk

    CHUNK_CACHE[paper_id] = lookup
    return lookup

# ==========================================================
# GET CHUNK
# ==========================================================

def get_chunk(paper_id, chunk_id):
    chunks = load_chunks(paper_id)
    return chunks.get(chunk_id)

# ==========================================================
# EMBED QUERY
# ==========================================================

def embed_query(query):
    embedding = model.encode(
        query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return embedding.astype("float32")

# ==========================================================
# PRINT PAPER INFO
# ==========================================================

def print_paper_summary(paper_id):
    paper = PAPER_LOOKUP.get(paper_id)
    if paper is None:
        print("Paper not found.")
        return

    print("=" * 70)
    print("Paper ID :", paper["paper_id"])
    print("Title    :", paper["title"])
    print("Authors  :", ", ".join(paper.get("authors", [])))
    print("Sections :", paper.get("num_sections"))
    print("Chunks   :", paper.get("num_chunks"))
    print("=" * 70)

# ==========================================================
# SEARCH FAISS
# ==========================================================

def search(query, top_k=5, paper_id=None):
    """
    Semantic search.

    Parameters
    ----------
    query : str
    top_k : int
    paper_id : str | None
        If provided, results are restricted to one paper.
    """
    query_embedding = embed_query(query)
    query_embedding = np.expand_dims(query_embedding, axis=0)

    # Search more than required because filtering may remove some results.
    search_k = min(max(top_k * 10, 50), index.ntotal)

    scores, indices = index.search(query_embedding, search_k)
    results = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        meta = INDEX_METADATA[idx]

        if paper_id is not None and meta["paper_id"] != paper_id:
            continue

        chunk = get_chunk(meta["paper_id"], meta["chunk_id"])

        if chunk is None:
            continue

        results.append({
            "score": float(score),
            "paper_id": meta["paper_id"],
            "paper_title": chunk.get("paper_title", ""),
            "chunk_id": meta["chunk_id"],
            "chunk_type": meta["chunk_type"],
            "section_number": chunk.get("section_number"),
            "section_title": chunk.get("section_title"),
            "page_start": chunk.get("page_start"),
            "page_end": chunk.get("page_end"),
            "word_count": chunk.get("word_count", 0),
            "text": chunk.get("text", "")
        })

        if len(results) >= top_k:
            break

    return results

# ==========================================================
# PRINT RESULTS
# ==========================================================

def print_results(results):
    if len(results) == 0:
        print("\nNo results found.")
        return

    print("\n" + "=" * 100)
    for i, r in enumerate(results, start=1):
        print(f"\n[{i}]")
        print(f"Score        : {r['score']:.4f}")
        print(f"Paper        : {r['paper_id']}")
        print(f"Title        : {r['paper_title']}")
        print(f"Chunk        : {r['chunk_id']}")
        print(f"Type         : {r['chunk_type']}")
        print(f"Section      : {r['section_number']}")
        print(f"Section Title: {r['section_title']}")
        print(f"Pages        : {r['page_start']} - {r['page_end']}")
        print(f"Words        : {r['word_count']}\n")
        
        preview = r["text"][:900]
        print(preview)
        
        if len(r["text"]) > 900:
            print("...")
            
        print("-" * 100)

# ==========================================================
# PAPER SEARCH
# ==========================================================

def normalize(text):
    return text.lower().replace("-", " ").replace("_", " ").strip()

def find_paper(query):
    q = normalize(query)

    # Exact paper id
    for p in PAPER_REGISTRY:
        if normalize(p["paper_id"]) == q:
            return p

    # Exact title
    for p in PAPER_REGISTRY:
        if normalize(p["title"]) == q:
            return p

    # Alias
    for p in PAPER_REGISTRY:
        for alias in p.get("aliases", []):
            if normalize(alias) == q:
                return p

    # Partial title
    for p in PAPER_REGISTRY:
        if q in normalize(p["title"]):
            return p

    return None

# ==========================================================
# LIST PAPERS
# ==========================================================

def list_papers():
    print("\n" + "=" * 80)
    for i, p in enumerate(PAPER_REGISTRY, start=1):
        print(f"{i:2d}. {p['paper_id']} | {p['title']}")
    print("=" * 80)

# ==========================================================
# CONVERSATION STATE
# ==========================================================

STATE = {
    "selected_paper": None
}

# ==========================================================
# SELECT PAPER
# ==========================================================

def select_paper(query):
    paper = find_paper(query)
    if paper is None:
        print("\nPaper not found.")
        return

    STATE["selected_paper"] = paper["paper_id"]

    print("\n" + "=" * 70)
    print("Selected Paper\n")
    print("Paper ID :", paper["paper_id"])
    print("Title    :", paper["title"])
    print("Authors  :", ", ".join(paper.get("authors", [])))
    print("=" * 70)

# ==========================================================
# CLEAR
# ==========================================================

def clear_selection():
    STATE["selected_paper"] = None
    print("\nPaper selection cleared.")

# ==========================================================
# DEMO
# ==========================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Retriever initialization successful.\n")
    print("Embedding Dimension :", model.get_embedding_dimension())
    print("FAISS Vectors       :", index.ntotal)
    print("Registered Papers   :", len(PAPER_REGISTRY))
    print("\nReady for retrieval.")

    while True:
        print()
        if STATE["selected_paper"]:
            print(f"[Selected Paper] {STATE['selected_paper']}")

        cmd = input("> ").strip()

        if cmd.lower() in {"quit", "exit", "q"}:
            break

        if cmd.lower() == "papers":
            list_papers()
            continue

        if cmd.lower().startswith("select "):
            select_paper(cmd[7:])
            continue

        if cmd.lower() == "clear":
            clear_selection()
            continue

        if cmd.lower() == "info":
            pid = STATE["selected_paper"]
            if pid:
                print_paper_summary(pid)
            else:
                print("No paper selected.")
            continue

        if not cmd:
            continue

        # Search runs inside the loop now
        results = search(
            cmd,
            top_k=5,
            paper_id=STATE["selected_paper"]
        )

        print_results(results)