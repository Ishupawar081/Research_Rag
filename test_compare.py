import sys
import os
import json
from backend.rag.chat import compare_papers
user_id = "4c559521-dbef-4b40-a23f-e2f68c307ff8"

users_dir = "backend/data/"
papers_path = os.path.join(users_dir, user_id, "registry/papers.json")
with open(papers_path) as f:
    registry = json.load(f)

if len(registry) >= 2:
    p1 = registry[0]["paper_id"]
    p2 = registry[1]["paper_id"]
    print("Testing Compare methodology...")
    res = compare_papers("Compare methodology", p1, p2, top_k=6, user_id=user_id)
    
    print(f"Compare papers success: {res.get('success')}")
    print("\n\nPROMPT EXTRACT:")
    if res.get('success'):
        print(res.get('answer'))
        # Can't easily print prompt from here, but I can print context length
        print("Context Length:", res.get("context_length"))
