import sys
import os
import requests
import json
import time

sys.path.append(os.getcwd())

from backend.rag.prompts import get_prompt
from backend.rag.retriever import search

query = "compare abstract"
paper_a = "2212.00380v1"
paper_b = "escot"

# Get chunks
chunks_a = search(query=query, paper_id=paper_a, top_k=2)
chunks_b = search(query=query, paper_id=paper_b, top_k=2)

ctx_a = "[SECTION] Abstract\n[CONTENT]\n" + "".join([c["text"] for c in chunks_a])
ctx_b = "[SECTION] Abstract\n[CONTENT]\n" + "".join([c["text"] for c in chunks_b])

prompt = get_prompt(
    mode="compare",
    query=query,
    context_a=ctx_a,
    context_b=ctx_b,
    paper_a="Paper A",
    paper_b="Paper B"
)

payload = {
    "model": "qwen2.5:1.5b",
    "prompt": prompt,
    "stream": True,
    "options": {
        "num_predict": 250,
        "temperature": 0.2,
        "top_p": 0.9
    }
}

print(f"Sending prompt of length {len(prompt)} to Ollama stream...")
t0 = time.time()
response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)

print("Starting generation stream:")
count = 0
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data.get("response", ""), end="", flush=True)
        count += 1
        if count == 1:
            print(f"\n[Time to first token: {time.time() - t0:.2f}s]\n")

print(f"\n\nTotal time: {time.time() - t0:.2f}s")
