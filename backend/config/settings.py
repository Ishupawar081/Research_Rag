from pathlib import Path

# ==========================================================
# PROJECT ROOT
# ==========================================================

ROOT = Path(__file__).resolve().parents[1]

# ==========================================================
# DATA
# ==========================================================

DATA_DIR = ROOT / "data"

SEMANTIC_CHUNKS = DATA_DIR / "semantic_chunks"

EMBEDDINGS = DATA_DIR / "embeddings"

FAISS_DIR = DATA_DIR / "faiss"

REGISTRY = DATA_DIR / "registry"

# ==========================================================
# FILES
# ==========================================================

INDEX_FILE = FAISS_DIR / "index.faiss"

INDEX_METADATA = FAISS_DIR / "index_metadata.json"

PAPER_REGISTRY = REGISTRY / "papers.json"

# ==========================================================
# MODEL
# ==========================================================

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

TOP_K = 5