import sys
import os

sys.path.append(os.getcwd())

from backend.rag.retriever import search
from backend.rag.context_builder import prepare_context

print("==========================================")
print("TEST 1: Metadata")
print("==========================================")
query = "who are the authors"
results = search(query, top_k=5, paper_id="2212.00187v1")
prepare_context(query, results)

print("==========================================")
print("TEST 2: Summary")
print("==========================================")
query = "summarize paper"
results = search(query, top_k=5, paper_id="2212.00187v1")
prepare_context(query, results)

print("==========================================")
print("TEST 3: Method (with fallback check)")
print("==========================================")
query = "explain methodology"
results = search(query, top_k=5, paper_id="2212.00187v1")
prepare_context(query, results)

