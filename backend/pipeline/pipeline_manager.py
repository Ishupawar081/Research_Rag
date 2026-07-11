import os
import sys
import importlib
import asyncio
from pathlib import Path
from typing import AsyncGenerator
import shutil
import logging

logger = logging.getLogger("upload_pipeline")
logger.setLevel(logging.INFO)

# Set up paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Dynamically import the numbered scripts from start/
stage1 = importlib.import_module("start.1")
stage2 = importlib.import_module("start.2")
stage4 = importlib.import_module("start.4")
stage5 = importlib.import_module("start.5")
stage6 = importlib.import_module("start.6")
stage7 = importlib.import_module("start.7")
stage8 = importlib.import_module("start.8")
stage9 = importlib.import_module("start.9")
stage13 = importlib.import_module("start.13")

# Define Data Directories inside backend/data
DATA_DIR = PROJECT_ROOT / "backend" / "data"

DIR_PRO = DATA_DIR / "pro"
DIR_GRAPH1 = DATA_DIR / "graph_1"
DIR_GRAPH2 = DATA_DIR / "graph_2"
DIR_GRAPH_FINAL = DATA_DIR / "graph_final"
DIR_SEMANTIC = DATA_DIR / "semantic"
DIR_CHUNKS = DATA_DIR / "semantic_chunks"
DIR_EMBEDDINGS = DATA_DIR / "embeddings"
DIR_FAISS = DATA_DIR / "faiss"
DIR_REGISTRY = DATA_DIR / "registry"
DIR_PDFS = DATA_DIR / "pdfs"

def get_user_dirs(user_id: str):
    base = DATA_DIR / user_id
    dirs = {
        "pro": base / "pro",
        "graph1": base / "graph_1",
        "graph2": base / "graph_2",
        "graph_final": base / "graph_final",
        "semantic": base / "semantic",
        "chunks": base / "semantic_chunks",
        "embeddings": base / "embeddings",
        "faiss": base / "faiss",
        "registry": base / "registry",
        "papers": base / "papers"
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs

async def run_pipeline(pdf_path: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Executes the ingestion pipeline on a single PDF file and yields progress updates (SSE strings).
    """
    udirs = get_user_dirs(user_id)
    pdf_path = Path(pdf_path)
    paper_name = pdf_path.stem

    try:
        # 0. Store PDF Permanently
        logger.info(f"Current stage: Initialization (User ID: {user_id})")
        if "temp_uploads" in pdf_path.parts:
            permanent_pdf = udirs["papers"] / pdf_path.name
            shutil.copy2(pdf_path, permanent_pdf)
            pdf_path = permanent_pdf
            logger.info(f"File saved permanently to {pdf_path}")

        yield f"data: {{\"stage\": \"upload\", \"message\": \"Received {pdf_path.name}\", \"progress\": 0}}\n\n"
        await asyncio.sleep(0.5)

        # Stage 1: Convert PDF to IR
        logger.info(f"Current stage: Ingestion (Stage 1)")
        yield f"data: {{\"stage\": \"ingestion\", \"message\": \"Parsing PDF with Docling...\", \"progress\": 10}}\n\n"
        ir_file = await asyncio.to_thread(stage1.process_pdf, pdf_path, udirs["pro"])

        # Stage 2: Initial Graph Resolution
        logger.info(f"Current stage: Graph 1 (Stage 2)")
        yield f"data: {{\"stage\": \"graph_1\", \"message\": \"Resolving document graph references...\", \"progress\": 25}}\n\n"
        paper_pro_dir = udirs["pro"] / paper_name
        await asyncio.to_thread(stage2.process_paper, paper_pro_dir, udirs["graph1"])

        # Stage 3 (start/4.py): Hierarchy Building
        logger.info(f"Current stage: Graph 2 (Stage 3)")
        yield f"data: {{\"stage\": \"graph_2\", \"message\": \"Building section hierarchy...\", \"progress\": 40}}\n\n"
        paper_g1_dir = udirs["graph1"] / paper_name
        await asyncio.to_thread(stage4.process_paper, paper_g1_dir, udirs["graph2"])

        # Stage 4 (start/5.py): Graph Serialization
        logger.info(f"Current stage: Graph Final (Stage 4)")
        yield f"data: {{\"stage\": \"graph_final\", \"message\": \"Serializing final graph...\", \"progress\": 55}}\n\n"
        paper_g2_dir = udirs["graph2"] / paper_name
        await asyncio.to_thread(stage5.process_paper, paper_g2_dir, udirs["graph_final"])

        # Stage 5 (start/6.py): Semantic Representation
        logger.info(f"Current stage: Semantic (Stage 5)")
        yield f"data: {{\"stage\": \"semantic\", \"message\": \"Constructing semantic representation...\", \"progress\": 70}}\n\n"
        paper_gf_dir = udirs["graph_final"] / paper_name
        await asyncio.to_thread(stage6.process_paper, paper_gf_dir, udirs["semantic"])

        # Stage 6 (start/7.py): Chunking
        logger.info(f"Current stage: Semantic Chunks (Stage 6)")
        yield f"data: {{\"stage\": \"semantic_chunks\", \"message\": \"Building retrieval chunks...\", \"progress\": 80}}\n\n"
        paper_sem_dir = udirs["semantic"] / paper_name
        await asyncio.to_thread(stage7.process_paper, paper_sem_dir, udirs["chunks"])

        # Stage 7 (start/8.py): Embedding
        logger.info(f"Current stage: Embeddings (Stage 7)")
        yield f"data: {{\"stage\": \"embeddings\", \"message\": \"Generating vector embeddings...\", \"progress\": 90}}\n\n"
        paper_chk_dir = udirs["chunks"] / paper_name
        await asyncio.to_thread(stage8.process_paper, paper_chk_dir, udirs["embeddings"])

        # Final Aggregation Stages (rebuild FAISS and Registry)
        logger.info(f"Current stage: Indexing (Final Aggregation)")
        yield f"data: {{\"stage\": \"indexing\", \"message\": \"Updating FAISS index and paper registry...\", \"progress\": 95}}\n\n"
        await asyncio.to_thread(stage9.build_index, udirs["embeddings"], udirs["faiss"])
        await asyncio.to_thread(stage13.build_registry, paper_chk_dir, udirs["registry"])

        from backend.rag.loader import resources
        resources.clear_cache(user_id)

        logger.info(f"Pipeline completed successfully for {paper_name}")
        yield f"data: {{\"stage\": \"complete\", \"message\": \"Pipeline completed successfully!\", \"progress\": 100}}\n\n"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Errors occurred in pipeline for user {user_id}:\n{error_details}")
        yield f"data: {{\"stage\": \"error\", \"message\": \"Pipeline failed: {str(e)}\", \"progress\": 0}}\n\n"

    finally:
        # Cleanup temporary uploaded PDF if it exists in temp_uploads
        if "temp_uploads" in pdf_path.parts:
            try:
                if pdf_path.exists():
                    pdf_path.unlink()
            except Exception as cleanup_error:
                print(f"Failed to clean up {pdf_path}: {cleanup_error}")
