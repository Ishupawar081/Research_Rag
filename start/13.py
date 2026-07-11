from pathlib import Path
import json
import re
from tqdm import tqdm

# ==========================================================
# CONFIG
# ==========================================================

INPUT_DIR = Path("semantic_chunks_a4")
OUTPUT_DIR = Path("paper_registry2")

OUTPUT_DIR.mkdir(exist_ok=True)

# ==========================================================
# HELPERS
# ==========================================================

def normalize_title(title):

    if not title:
        return ""

    title = title.lower()

    title = re.sub(r"[^a-z0-9 ]+", " ", title)

    title = re.sub(r"\s+", " ", title).strip()

    return title


def build_aliases(title, paper_id):

    aliases = set()

    if title:
        aliases.add(title)
        aliases.add(normalize_title(title))

        words = title.split()

        if len(words) >= 2:
            aliases.add(words[0])
            aliases.add(words[0].lower())

    aliases.add(paper_id)

    if "v" in paper_id:
        aliases.add(paper_id.split("v")[0])

    return sorted(
        x for x in aliases
        if x and len(x.strip()) > 0
    )


# ==========================================================
# BUILD REGISTRY
# ==========================================================

def build_registry(input_dir: Path, output_dir: Path):
    if (input_dir / "chunks.json").exists():
        papers = [input_dir]
    else:
        papers = sorted(input_dir.glob("*"))

    new_entries = []

    for paper in tqdm(papers):
        chunk_file = paper / "chunks.json"
        if not chunk_file.exists():
            continue

        with open(chunk_file, encoding="utf8") as f:
            chunks = json.load(f)

        if not chunks:
            continue

        metadata = next((c for c in chunks if c["chunk_type"] == "metadata"), None)
        if metadata is None:
            continue

        title = metadata.get("title", "")
        paper_id = metadata["paper_id"]

        section_chunks = [c for c in chunks if c["chunk_type"] == "section"]
        section_titles = [c.get("section_title") for c in section_chunks if c.get("section_title")]

        abstract_chunk = None
        introduction_chunk = None
        conclusion_chunk = None
        acknowledgement_chunk = None
        reference_chunks = []
        appendix_chunks = []
        major_sections = {}

        for c in section_chunks:
            cid = c["chunk_id"]
            title_lower = c.get("section_title", "").lower()

            if c.get("is_abstract"):
                abstract_chunk = cid
                major_sections["abstract"] = cid
            if c.get("is_introduction"):
                introduction_chunk = cid
                major_sections["introduction"] = cid
            if "conclusion" in title_lower or "future work" in title_lower:
                conclusion_chunk = cid
                major_sections["conclusion"] = cid
            if c.get("is_acknowledgement"):
                acknowledgement_chunk = cid
                major_sections["acknowledgement"] = cid
            if c.get("is_reference"):
                reference_chunks.append(cid)
            if c.get("is_appendix"):
                appendix_chunks.append(cid)

        if reference_chunks:
            major_sections["references"] = reference_chunks
        if appendix_chunks:
            major_sections["appendix"] = appendix_chunks

        pages = max((c.get("page_end", 0) for c in section_chunks), default=0)
        total_words = sum(c.get("word_count", 0) for c in section_chunks)
        total_figures = sum(c.get("figure_count", 0) for c in section_chunks)
        total_tables = sum(c.get("table_count", 0) for c in section_chunks)
        total_formulas = sum(c.get("formula_count", 0) for c in section_chunks)

        new_entries.append({
            "paper_id": paper_id,
            "title": title,
            "title_normalized": normalize_title(title),
            "aliases": build_aliases(title, paper_id),
            "authors": metadata.get("authors", []),
            "affiliations": metadata.get("affiliations", []),
            "emails": metadata.get("emails", []),
            "keywords": metadata.get("keywords", []),
            "doi": metadata.get("doi"),
            "conference": metadata.get("conference"),
            "year": metadata.get("year"),
            "pages": pages,
            "num_chunks": len(chunks),
            "num_sections": len(section_chunks),
            "total_words": total_words,
            "total_figures": total_figures,
            "total_tables": total_tables,
            "total_formulas": total_formulas,
            "section_titles": section_titles,
            "abstract_chunk": abstract_chunk,
            "introduction_chunk": introduction_chunk,
            "conclusion_chunk": conclusion_chunk,
            "acknowledgement_chunk": acknowledgement_chunk,
            "reference_chunks": reference_chunks,
            "appendix_chunks": appendix_chunks,
            "major_sections": major_sections,
            "chunk_file": str(chunk_file),
            "embedding_file": f"embeddings/{paper_id}/embeddings.npy",
            "has_references": len(reference_chunks) > 0,
            "has_appendix": len(appendix_chunks) > 0,
            "has_acknowledgement": acknowledgement_chunk is not None,
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "papers.json"

    registry = []
    if out_file.exists():
        try:
            with open(out_file, encoding="utf8") as f:
                registry = json.load(f)
        except Exception:
            registry = []

    # Remove existing entries with the same paper_ids as the newly processed ones
    new_paper_ids = {p["paper_id"] for p in new_entries}
    registry = [p for p in registry if p["paper_id"] not in new_paper_ids]

    # Append the new entries
    registry.extend(new_entries)

    # Sort the combined registry
    registry.sort(key=lambda x: x["title_normalized"])

    with open(out_file, "w", encoding="utf8") as f:
        json.dump(registry, f, indent=4, ensure_ascii=False)

    print(f"\n{'=' * 70}\nTotal Papers : {len(registry)}\n")
    for p in registry[:10]:
        print(f"{p['paper_id']} -> {p['title']}")
    print(f"\nRegistry saved to\n{out_file}")
    
    return out_file

if __name__ == "__main__":
    build_registry(INPUT_DIR, OUTPUT_DIR)