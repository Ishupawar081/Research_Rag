from pathlib import Path
import json
import threading

import faiss
from sentence_transformers import SentenceTransformer

from backend.config.settings import EMBEDDING_MODEL
from backend.pipeline.pipeline_manager import DATA_DIR

# ==========================================================
# Resource Loader
# ==========================================================

class ResourceLoader:
    """
    Singleton-style loader.

    Loads everything only once.

    Resources loaded:

        - SentenceTransformer
        - FAISS index
        - Index metadata
        - Paper registry

    Chunk files are cached on demand.
    """

    def __init__(self):
        self._model = None
        self._indices = {}
        self._metadata = {}
        self._registries = {}
        self._paper_lookups = {}
        self._chunk_caches = {}
        self._lock = threading.Lock()

        self._lock = threading.Lock()

    # ======================================================
    # MODEL
    # ======================================================

    @property
    def model(self):

        if self._model is None:

            with self._lock:

                if self._model is None:

                    print("Loading embedding model...")

                    self._model = SentenceTransformer(
                        EMBEDDING_MODEL
                    )

                    print("Embedding model loaded.")

        return self._model

    # ======================================================
    # FAISS
    # ======================================================

    def get_index(self, user_id: str):
        if user_id not in self._indices:
            with self._lock:
                if user_id not in self._indices:
                    index_file = DATA_DIR / user_id / "faiss" / "index.faiss"
                    if index_file.exists():
                        self._indices[user_id] = faiss.read_index(str(index_file))
                    else:
                        # Return empty index if not exists
                        d = self.model.get_sentence_embedding_dimension()
                        self._indices[user_id] = faiss.IndexFlatL2(d)
        return self._indices.get(user_id)

    # ======================================================
    # INDEX METADATA
    # ======================================================

    def get_metadata(self, user_id: str):
        if user_id not in self._metadata:
            with self._lock:
                if user_id not in self._metadata:
                    meta_file = DATA_DIR / user_id / "faiss" / "index_metadata.json"
                    if meta_file.exists():
                        with open(meta_file, encoding="utf8") as f:
                            self._metadata[user_id] = json.load(f)
                    else:
                        self._metadata[user_id] = []
        return self._metadata.get(user_id)

    # ======================================================
    # PAPER REGISTRY
    # ======================================================

    def get_registry(self, user_id: str):
        if user_id not in self._registries:
            with self._lock:
                if user_id not in self._registries:
                    reg_file = DATA_DIR / user_id / "registry" / "papers.json"
                    if reg_file.exists():
                        with open(reg_file, encoding="utf8") as f:
                            self._registries[user_id] = json.load(f)
                    else:
                        self._registries[user_id] = []
                    
                    self._paper_lookups[user_id] = {
                        p["paper_id"]: p
                        for p in self._registries[user_id]
                    }
        return self._registries.get(user_id)

    # ======================================================
    # PAPER LOOKUP
    # ======================================================

    def get_paper_lookup(self, user_id: str):
        self.get_registry(user_id)
        return self._paper_lookups.get(user_id, {})

    # ======================================================
    # LOAD CHUNKS
    # ======================================================

    def load_chunks(self, user_id: str, paper_id: str):
        if user_id not in self._chunk_caches:
            self._chunk_caches[user_id] = {}
            
        if paper_id in self._chunk_caches[user_id]:
            return self._chunk_caches[user_id][paper_id]

        chunk_file = DATA_DIR / user_id / "semantic_chunks" / paper_id / "chunks.json"

        if not chunk_file.exists():
            return {}

        with open(chunk_file, encoding="utf8") as f:
            chunks = json.load(f)

        lookup = {c["chunk_id"]: c for c in chunks}
        self._chunk_caches[user_id][paper_id] = lookup
        return lookup

    # ======================================================
    # GET CHUNK
    # ======================================================

    def get_chunk(self, user_id: str, paper_id: str, chunk_id: str):
        chunks = self.load_chunks(user_id, paper_id)
        return chunks.get(chunk_id)

    # ======================================================
    # CLEAR CACHE
    # ======================================================

    def clear_cache(self, user_id: str):
        with self._lock:
            self._indices.pop(user_id, None)
            self._metadata.pop(user_id, None)
            self._registries.pop(user_id, None)
            self._paper_lookups.pop(user_id, None)
            self._chunk_caches.pop(user_id, None)

    # ======================================================
    # INFO
    # ======================================================

    def info(self):

        print()

        print("=" * 60)

        print("Embedding Model")

        print(
            self.model.get_embedding_dimension()
        )

        print()

        print("Vectors")

        print(
            self.index.ntotal
        )

        print()

        print("Registry")

        print(
            len(self.registry)
        )

        print("=" * 60)


# ==========================================================
# Global Singleton
# ==========================================================

resources = ResourceLoader()