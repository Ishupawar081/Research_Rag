import json
import random
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import faiss
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("embeddings4")
OUTPUT_DIR = Path("faiss_index4")

OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "BAAI/bge-base-en-v1.5"
EXPECTED_DIMENSION = 768

# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def validate_embeddings(embeddings: np.ndarray, expected_dim: int):
    """
    Verify embeddings have no NaN, Inf, correct dimension, and are not empty.
    Raises clear exceptions if validation fails.
    """
    if embeddings.size == 0 or embeddings.shape[0] == 0:
        raise ValueError("Embeddings array is empty.")
        
    if embeddings.ndim != 2:
        raise ValueError(f"Expected 2D embeddings array, got {embeddings.ndim}D.")
        
    if embeddings.shape[1] != expected_dim:
        raise ValueError(f"Incorrect embedding dimension: expected {expected_dim}, got {embeddings.shape[1]}")
        
    if np.isnan(embeddings).any():
        raise ValueError("Embeddings contain NaN.")
        
    if np.isinf(embeddings).any():
        raise ValueError("Embeddings contain Inf.")

def verify_normalization(embeddings: np.ndarray, num_samples: int = 10, tol: float = 1e-4):
    """
    Verify that random samples of embeddings have unit norm.
    Prints a warning if any sampled vector deviates significantly.
    """
    n = len(embeddings)
    if n == 0:
        return
        
    samples = random.sample(range(n), min(n, num_samples))
    for idx in samples:
        norm = np.linalg.norm(embeddings[idx])
        if abs(norm - 1.0) > tol:
            print(f"\nWARNING: Vector at index {idx} significantly deviates from unit norm: ||v|| = {norm:.6f}")
            break

# ==========================================================
# BUILD FUNCTION
# ==========================================================

def build_index(input_dir: Path, output_dir: Path):
    print("Loading embeddings and metadata...")
    all_embeddings_list = []
    all_metadata = []
    paper_offsets = {}
    current_offset = 0

    papers = sorted(input_dir.glob("*"))
    for paper in tqdm(papers, desc="Reading papers"):
        emb_file = paper / "embeddings.npy"
        meta_file = paper / "metadata.json"
        if not emb_file.exists() or not meta_file.exists():
            continue

        embeddings = np.load(emb_file)
        with open(meta_file, encoding="utf8") as f:
            metadata = json.load(f)

        count = len(embeddings)
        if count != len(metadata):
            raise ValueError(f"{paper.name}: embeddings ({count}) != metadata ({len(metadata)})")
            
        if count == 0:
            continue

        paper_offsets[paper.name] = {
            "start": current_offset,
            "end": current_offset + count - 1,
            "count": count
        }

        all_embeddings_list.append(embeddings)
        all_metadata.extend(metadata)
        current_offset += count

    print("Merging embeddings...")
    if not all_embeddings_list:
        raise ValueError("No embeddings found to index.")

    all_embeddings = np.vstack(all_embeddings_list).astype("float32")
    print("Validating embeddings...")
    validate_embeddings(all_embeddings, EXPECTED_DIMENSION)
    verify_normalization(all_embeddings)

    for i in range(len(all_metadata)):
        new_meta = {"vector_id": i}
        new_meta.update(all_metadata[i])
        all_metadata[i] = new_meta

    dimension = all_embeddings.shape[1]

    paper_counts = [v["count"] for v in paper_offsets.values()]
    total_papers = len(paper_offsets)
    total_vectors = len(all_embeddings)
    avg_chunks = sum(paper_counts) / total_papers if total_papers > 0 else 0
    max_chunks = max(paper_counts) if paper_counts else 0
    min_chunks = min(paper_counts) if paper_counts else 0

    largest_paper = max(paper_offsets.keys(), key=lambda k: paper_offsets[k]["count"]) if paper_offsets else "N/A"
    smallest_paper = min(paper_offsets.keys(), key=lambda k: paper_offsets[k]["count"]) if paper_offsets else "N/A"

    print("\n--- Statistics ---")
    print(f"Total papers              : {total_papers}")
    print(f"Total vectors             : {total_vectors}")
    print(f"Embedding dimension       : {dimension}")
    print(f"Average chunks per paper  : {avg_chunks:.2f}")
    print(f"Maximum chunks in a paper : {max_chunks}")
    print(f"Minimum chunks in a paper : {min_chunks}")
    print(f"Largest paper             : {largest_paper}")
    print(f"Smallest paper            : {smallest_paper}")
    print("------------------\n")

    print("Building FAISS index...")
    index = faiss.IndexFlatIP(dimension)
    index.add(all_embeddings)

    print("Saving outputs...")
    output_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(output_dir / "index.faiss"))

    with open(output_dir / "index_metadata.json", "w", encoding="utf8") as f:
        json.dump(all_metadata, f, indent=4, ensure_ascii=False)

    index_info = {
        "embedding_model": MODEL_NAME,
        "dimension": dimension,
        "num_vectors": total_vectors,
        "normalized": True,
        "index_type": "IndexFlatIP",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    with open(output_dir / "index_info.json", "w", encoding="utf8") as f:
        json.dump(index_info, f, indent=4, ensure_ascii=False)

    with open(output_dir / "paper_offsets.json", "w", encoding="utf8") as f:
        json.dump(paper_offsets, f, indent=4, ensure_ascii=False)

    print("\nIndex saved.")
    print(f"Vectors in index: {index.ntotal}")
    return output_dir / "index.faiss"

if __name__ == "__main__":
    build_index(INPUT_DIR, OUTPUT_DIR)
    print("Done.")