import sys
import os

sys.path.append(os.getcwd())

from backend.rag.retriever import search
from backend.rag.context_builder import prepare_context

query = "who are the authors"
results = search(query, top_k=5, paper_id="2212.00187v1")
print("Search results count:", len(results))
prepare_context(query, results)

print("------------------------------------------")

query = "give abstract"
results = search(query, top_k=5, paper_id="2212.00187v1")
print("Search results count:", len(results))
prepare_context(query, results)

