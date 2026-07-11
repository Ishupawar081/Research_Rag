from pathlib import Path
import json
import numpy as np
from tqdm import tqdm

from sentence_transformers import SentenceTransformer

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("semantic_chunks_a4")
OUTPUT_DIR = Path("embeddings4")

OUTPUT_DIR.mkdir(exist_ok=True)

MODEL_NAME = "BAAI/bge-base-en-v1.5"

# ==========================================================
# LOAD MODEL
# ==========================================================

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer(MODEL_NAME)
        print("Model loaded.")
    return _model

# ==========================================================
# ENRICHED TEXT BUILDER
# Only used for embedding — never overwrites chunk data.
# ==========================================================

def _section_semantic_description(section_title: str) -> str:
    """
    Generate a rich semantic description for a section title using
    rule-based keyword matching. Ordered from most specific to most general.
    """
    t = section_title.lower().strip()

    # ---- ordered from most-specific to most-generic ----
    rules = [
        # Abstract
        (["abstract"],
         "Document Summary\nThis abstract summarizes the complete paper including the motivation, method, experiments and conclusions."),

        # Acknowledgement / Funding
        (["acknowledgement", "acknowledgment", "funding"],
         "Funding, contributors, collaborators, and institutional support.\n"
         "This section contains acknowledgements and funding information."),

        # References
        (["reference", "bibliography"],
         "Reference Section\nBibliography\nRelated cited works"),

        # Appendix / supplementary
        (["appendix", "supplement", "supplementary", "additional"],
         "This section is an appendix or supplementary material with additional details, proofs, or experiments."),

        # Dataset / data collection / preprocessing
        (["dataset", "data collection", "data preparation", "data",
          "preprocessing", "corpus", "annotation"],
         "This section describes the dataset, data collection, preprocessing steps, and annotation procedures."),

        # Implementation details
        (["implementation"],
         "This section covers implementation details, training setup, hyperparameters, and experimental configuration."),

        # Ablation
        (["ablation"],
         "This section presents ablation studies, analyzing the contribution of individual components."),

        # Experimental setup / training / setup
        (["training", "setup", "configuration",
          "hyperparameter", "training detail", "experimental setup",
          "experimental detail"],
         "This section covers experimental setup, training details, hyperparameters, and configuration."),

        # Numerical / quantitative results
        (["numerical result", "quantitative result", "quantitative evaluat",
          "numerical evaluat", "numerical comparison"],
         "This section presents the numerical results, experiments, quantitative evaluation, performance metrics, benchmarks, and comparisons with baselines."),

        # General results / experiments / evaluation
        (["result", "experiment", "evaluat", "benchmark", "performance",
          "empirical", "analysis", "assessment"],
         "This section presents experimental results, evaluation, performance analysis, and comparisons."),

        # Discussion / Conclusion / future work
        (["discussion", "conclusion", "future work", "limitation",
          "closing remark", "summary"],
         "This section discusses and summarises the paper, main conclusions, contributions, limitations, and directions for future work."),

        # Loss / objective / optimisation
        (["loss", "objective", "optimisation", "optimization",
          "training objective", "cost function"],
         "This section defines the loss functions, training objectives, and optimisation strategy."),

        # Attention / transformer / self-attention
        (["attention", "transformer", "self-attention", "cross-attention"],
         "This section describes attention mechanisms, transformer modules, and self-attention or cross-attention components."),

        # Representation / feature / embedding
        (["representation", "feature", "embedding", "latent", "encoding",
          "descriptor"],
         "This section discusses feature representations, embeddings, latent spaces, and encoding strategies."),

        # Fusion / multi-modal / combination
        (["fusion", "multi-modal", "multimodal", "combination",
          "integration", "joint"],
         "This section covers fusion strategies, multi-modal integration, and combination of different modalities or signals."),

        # Segmentation / detection / recognition / classification
        (["segmentation", "detection", "recognition", "classification",
          "tracking", "localisation", "localization", "identification"],
         "This section addresses the task of segmentation, detection, recognition, or classification and the methods used."),

        # Generation / synthesis
        (["generation", "synthesis", "generative", "rendering", "sampling"],
         "This section presents generative methods, synthesis techniques, and rendering or sampling procedures."),

        # Method / approach / model / framework / architecture
        (["method", "approach", "model", "framework", "architecture",
          "pipeline", "algorithm", "system", "network", "design",
          "proposed", "formulation", "technical", "solution"],
         "This section explains the proposed method, algorithm, architecture, pipeline, model design, and technical solution."),

        # Introduction
        (["introduction", "overview", "motivation", "problem statement",
          "problem formulation"],
         "This section introduces the paper, motivation, problem statement, contributions, and an overview of the approach."),

        # Related work / prior / literature
        (["related work", "prior work", "literature", "background",
          "previous work", "survey", "existing approach"],
         "This section reviews related work, prior methods, literature review, and existing approaches."),
    ]

    for keywords, description in rules:
        if any(kw in t for kw in keywords):
            return description

    # Fallback: generic description based on the raw title
    return f"This section titled '{section_title}' discusses concepts related to {section_title}."


def _build_paper_identity(chunk: dict) -> str:
    """Helper to extract and format paper identity and metadata."""
    parts = []
    title = chunk.get("title") or chunk.get("paper_title") or ""
    if title:
        parts.append(f"Paper Title: {title}")

    authors = chunk.get("authors", [])
    if authors:
        parts.append(f"Authors: {', '.join(authors)}")

    affils = chunk.get("affiliations", [])
    if affils:
        parts.append(f"Affiliations: {', '.join(affils)}")

    emails = chunk.get("emails", [])
    if emails:
        parts.append(f"Emails: {', '.join(emails)}")

    kws = chunk.get("keywords", [])
    if kws:
        parts.append(f"Keywords: {', '.join(kws)}")

    for field in ["conference", "year", "doi"]:
        val = chunk.get(field)
        if val:
            parts.append(f"{field.capitalize()}: {val}")

    if not parts:
        return ""
    return "Paper Identity:\n" + "\n".join(parts)


def _build_section_hierarchy(chunk: dict) -> str:
    """Helper to extract and format section hierarchy information."""
    parts = []
    sec_num = chunk.get("section_number") or ""
    sec_title = chunk.get("section_title") or ""
    sec_path = chunk.get("section_path") or []

    if sec_num:
        parts.append(f"Section Number: {sec_num}")
    if sec_path:
        parts.append(f"Section Depth: {len(sec_path)}")
        parts.append(f"Section Path: {' > '.join(str(p) for p in sec_path)}")
        if len(sec_path) > 0:
            parts.append(f"Major Section: {sec_path[0]}")
    if sec_title:
        parts.append(f"Section Title: {sec_title}")

    if not parts:
        return ""
    return "Section Hierarchy:\n" + "\n".join(parts)


def _build_embed_text(chunk: dict) -> str:
    """
    Build an enriched text representation for the embedding model.

    The returned string is used ONLY as input to model.encode().
    The stored chunk (chunks.json) and metadata.json are never modified.
    """
    chunk_type = chunk.get("chunk_type", "section")
    parts = []

    # 1. Paper Identity
    identity = _build_paper_identity(chunk)
    if identity:
        parts.append(identity)

    if chunk_type == "metadata":
        # 2. Content for metadata chunk
        body = chunk.get("text", "").strip()
        if body:
            parts.append(f"Content:\n{body}")

    else:
        # 2. Section Hierarchy
        hierarchy = _build_section_hierarchy(chunk)
        if hierarchy:
            parts.append(hierarchy)

        # 3. Semantic Context (Description)
        sec_title = chunk.get("section_title") or ""
        if sec_title:
            desc = _section_semantic_description(sec_title)
            parts.append(f"Semantic Context:\n{desc}")

        # 4. Chunk Type
        ctype = chunk.get("chunk_type") or "section"
        parts.append(f"Chunk Type:\n{ctype}")

        # 5. Content
        body = chunk.get("text", "").strip()
        if body:
            parts.append(f"Content:\n{body}")

    return "\n\n".join(parts)


# ==========================================================
# MAIN
# ==========================================================

def process_paper(paper: Path, output_dir: Path):
    chunk_file = paper / "chunks.json"
    if not chunk_file.exists():
        return None

    with open(chunk_file, encoding="utf8") as f:
        chunks = json.load(f)

    texts = []
    metadata = []
    for chunk in chunks:
        texts.append(_build_embed_text(chunk))
        metadata.append({
            "chunk_id": chunk["chunk_id"],
            "paper_id": chunk["paper_id"],
            "chunk_type": chunk["chunk_type"],
            "section_number": chunk.get("section_number"),
            "section_title": chunk.get("section_title")
        })

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=32,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    out_dir = output_dir / paper.name
    out_dir.mkdir(parents=True, exist_ok=True)

    np.save(out_dir / "embeddings.npy", embeddings)

    with open(out_dir / "metadata.json", "w", encoding="utf8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
        
    return out_dir / "embeddings.npy"

if __name__ == "__main__":
    papers = sorted(INPUT_DIR.glob("*"))
    for paper in tqdm(papers):
        process_paper(paper, OUTPUT_DIR)
    print("\nDone.")