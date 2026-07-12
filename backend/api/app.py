from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.api.routes import router

app = FastAPI(
    title="Research Paper Intelligence System",
    description="RAG Backend",
    version="1.0"
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
         FRONTEND_URL,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)