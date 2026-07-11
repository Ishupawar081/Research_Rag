import json
import shutil
import os
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

logger = logging.getLogger("upload_pipeline")
logger.setLevel(logging.INFO)

from backend.api.auth import get_current_user

from backend.api.schemas import ChatRequest
from backend.rag.chat import (
    single_paper_chat,
    collection_chat,
    compare_papers
)
from backend.rag.llm import DEFAULT_MODEL as LLM_MODEL
from backend.config.settings import EMBEDDING_MODEL
from backend.pipeline.pipeline_manager import run_pipeline, DIR_REGISTRY

router = APIRouter()


# ==========================================================
# HEALTH
# ==========================================================

@router.get("/health")

def health():

    return {

        "status": "ok"

    }


# ==========================================================
# CHAT
# ==========================================================

@router.post("/chat")
def chat(request: ChatRequest, user = Depends(get_current_user)):
    try:
        mode = request.mode.lower()

        if mode == "single":
            return single_paper_chat(
                query=request.query,
                paper=request.paper,
                top_k=request.top_k,
                user_id=user.id
            )

        if mode == "collection":
            return collection_chat(
                query=request.query,
                top_k=request.top_k,
                user_id=user.id
            )

        if mode == "compare":
            return compare_papers(
                query=request.query,
                paper_a=request.paper_a,
                paper_b=request.paper_b,
                top_k=request.top_k,
                user_id=user.id
            )

        return {
            "success": False,
            "error": "Unknown mode."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Internal Server Error: {str(e)}"
        }

# ==========================================================
# PIPELINE ENDPOINTS
# ==========================================================

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), user = Depends(get_current_user)):
    """
    Receives a PDF, saves it to a temp dir, and streams progress of the ingestion pipeline.
    """
    logger.info(f"Upload received from User ID: {user.id}")
    try:
        if not file.filename.endswith(".pdf"):
            return {"success": False, "error": "Only PDFs are supported."}
            
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File saved temporarily to: {file_path}")
        logger.info(f"Pipeline started for {file.filename}")
        return StreamingResponse(run_pipeline(str(file_path), user_id=user.id), media_type="text/event-stream")
    except Exception as e:
        logger.error(f"Error starting pipeline: {e}")
        return {"success": False, "error": f"Internal Server Error: {str(e)}"}


@router.get("/papers")
def list_papers(user = Depends(get_current_user)):
    """
    Returns the full paper registry.
    """
    try:
        from backend.pipeline.pipeline_manager import DATA_DIR
        registry_file = DATA_DIR / user.id / "registry" / "papers.json"
        if not registry_file.exists():
            return {"papers": []}
            
        with open(registry_file, encoding="utf-8") as f:
            data = json.load(f)
            
        return {"papers": data}
    except json.JSONDecodeError:
        return {"papers": []}
    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}", "success": False, "papers": []}


@router.get("/paper/{paper_id}")
def get_paper(paper_id: str, user = Depends(get_current_user)):
    """
    Returns metadata for a specific paper from the registry.
    """
    try:
        from backend.pipeline.pipeline_manager import DATA_DIR
        registry_file = DATA_DIR / user.id / "registry" / "papers.json"
        if not registry_file.exists():
            return {"error": "Registry not found", "success": False}
            
        with open(registry_file, encoding="utf-8") as f:
            data = json.load(f)
            
        paper = next((p for p in data if p["paper_id"] == paper_id), None)
        if not paper:
            return {"error": "Paper not found", "success": False}
            
        return {"paper": paper, "success": True}
    except json.JSONDecodeError:
        return {"error": "Corrupted registry file", "success": False}
    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}", "success": False}


@router.get("/info")
def get_info():
    """
    Returns the backend configuration, such as models used.
    """
    return {
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL
    }