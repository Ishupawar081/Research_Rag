from typing import Optional

from pydantic import BaseModel


# ==========================================================
# REQUEST
# ==========================================================

class ChatRequest(BaseModel):

    mode: str

    query: str

    paper: Optional[str] = None

    paper_a: Optional[str] = None

    paper_b: Optional[str] = None

    top_k: int = 8


# ==========================================================
# RESPONSE
# ==========================================================

class ChatResponse(BaseModel):

    success: bool

    mode: str

    query: str | None = None

    answer: str | None = None

    error: str | None = None

    sources: list = []

    papers: list = []

    retrieval_time: float | None = None