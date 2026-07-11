from backend.rag.retriever import search, search_diverse
from backend.rag.chat import compare_papers, collection_chat
from backend.rag.loader import resources
import sys

user_id = "4c559521-dbef-4b40-a23f-e2f68c307ff8"

res = search_diverse("Summarize collection", top_k=10, max_chunks_per_paper=2, user_id=user_id)
print(f"Chunks returned: {len(res)}")
