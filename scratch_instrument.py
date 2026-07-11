import os
import re

def instrument_file(file_path, replacements):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"Warning: Could not find '{old}' in {file_path}")
            
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


# 1. retriever.py missed chunks
instrument_file("backend/rag/retriever.py", [
    (
'''def _fetch_candidates(query: str, search_size: int, paper_id: str | None = None):
    """
    Core FAISS search and result formatting.
    Yields retrieved chunks one by one in similarity order.
    """''',
'''def _fetch_candidates(query: str, search_size: int, paper_id: str | None = None):
    """
    Core FAISS search and result formatting.
    Yields retrieved chunks one by one in similarity order.
    """
    print("=================================================", flush=True)
    print("ENTER _fetch_candidates", flush=True)
    print("=================================================", flush=True)
    print("Before embedding query", flush=True)'''
    ),
    (
'''    query_embedding = embed_query(query)''',
'''    query_embedding = embed_query(query)
    print("After embedding query", flush=True)'''
    ),
    (
'''def search(
    query: str,
    top_k: int = 5,
    paper_id: str | None = None
):
    """
    Existing search strategy. Returns top_k nearest chunks.
    """''',
'''def search(
    query: str,
    top_k: int = 5,
    paper_id: str | None = None
):
    """
    Existing search strategy. Returns top_k nearest chunks.
    """
    print("=================================================", flush=True)
    print("ENTER search", flush=True)
    print("=================================================", flush=True)
    import time
    start = time.perf_counter()'''
    ),
    (
'''def search_diverse(
    query: str,
    top_k: int = 10,
    max_chunks_per_paper: int = 2
):
    """
    Semantic search ensuring diversity across multiple papers.
    """''',
'''def search_diverse(
    query: str,
    top_k: int = 10,
    max_chunks_per_paper: int = 2
):
    """
    Semantic search ensuring diversity across multiple papers.
    """
    print("=================================================", flush=True)
    print("ENTER search_diverse", flush=True)
    print("=================================================", flush=True)
    import time
    start = time.perf_counter()'''
    ),
])

# 2. context_builder.py
instrument_file("backend/rag/context_builder.py", [
    (
'''def prepare_context(query: str, retrieved_chunks: list):
    """
    Formats the context efficiently without duplication.
    """''',
'''def prepare_context(query: str, retrieved_chunks: list):
    """
    Formats the context efficiently without duplication.
    """
    print("=================================================", flush=True)
    print("ENTER prepare_context", flush=True)
    print("=================================================", flush=True)
    import time
    start = time.perf_counter()
    print(f"Number of chunks received: {len(retrieved_chunks)}", flush=True)'''
    ),
    (
'''    deduped = preprocess_results(retrieved_chunks)''',
'''    deduped = preprocess_results(retrieved_chunks)
    print(f"Number after duplicate removal: {len(deduped)}", flush=True)'''
    ),
    (
'''    # Trimming is handled per-paper in build_context, but overall chunks:''',
'''    # Trimming is handled per-paper in build_context, but overall chunks:
    # Actually just print later'''
    ),
    (
'''    return {
        "context": context,
        "sources": sources,
        "chunks": chunks
    }''',
'''    print(f"Number after trimming: {len(chunks)}", flush=True)
    print(f"Final context length: {len(context)}", flush=True)
    end = time.perf_counter()
    print(f"Function: prepare_context", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print(f"retrieved chunk count: {len(retrieved_chunks)}", flush=True)
    print(f"context length: {len(context)}", flush=True)
    print("=================================================", flush=True)
    print("EXIT prepare_context", flush=True)
    print("=================================================", flush=True)
    return {
        "context": context,
        "sources": sources,
        "chunks": chunks
    }'''
    ),
    (
'''def preprocess_results(retrieved_chunks: list):''',
'''def preprocess_results(retrieved_chunks: list):
    print("=================================================", flush=True)
    print("ENTER preprocess_results", flush=True)
    print("=================================================", flush=True)'''
    ),
    (
'''    return list(seen.values())''',
'''    print("=================================================", flush=True)
    print("EXIT preprocess_results", flush=True)
    print("=================================================", flush=True)
    return list(seen.values())'''
    ),
    (
'''def build_context(deduped_chunks: list):''',
'''def build_context(deduped_chunks: list):
    print("=================================================", flush=True)
    print("ENTER build_context", flush=True)
    print("=================================================", flush=True)'''
    ),
    (
'''    return final_context.strip(), sources, final_chunks''',
'''    print("=================================================", flush=True)
    print("EXIT build_context", flush=True)
    print("=================================================", flush=True)
    return final_context.strip(), sources, final_chunks'''
    )
])

# 3. prompts.py
instrument_file("backend/rag/prompts.py", [
    (
'''def get_prompt(mode: str, query: str, **kwargs):
    """
    Returns the appropriate system prompt based on the chat mode.
    """''',
'''def get_prompt(mode: str, query: str, **kwargs):
    """
    Returns the appropriate system prompt based on the chat mode.
    """
    print("=================================================", flush=True)
    print("ENTER get_prompt", flush=True)
    print("=================================================", flush=True)
    import time
    start = time.perf_counter()'''
    ),
    (
'''    return f"{system_prompt}\\n{user_prompt}"''',
'''    prompt = f"{system_prompt}\\n{user_prompt}"
    end = time.perf_counter()
    print("Function: build_prompt (get_prompt)", flush=True)
    print(f"prompt length: {len(prompt)}", flush=True)
    print(f"Execution time: {end - start:.4f}s", flush=True)
    print("=================================================", flush=True)
    print("EXIT get_prompt", flush=True)
    print("=================================================", flush=True)
    return prompt'''
    )
])

# 4. loader.py
instrument_file("backend/rag/loader.py", [
    (
'''def load_chunks(self):''',
'''def load_chunks(self):
        print("=================================================", flush=True)
        print("ENTER load_chunks", flush=True)
        print("=================================================", flush=True)'''
    ),
    (
'''        self.is_loaded = True''',
'''        self.is_loaded = True
        print("=================================================", flush=True)
        print("EXIT load_chunks", flush=True)
        print("=================================================", flush=True)'''
    ),
    (
'''def get_chunk(self, paper_id: str, chunk_id: str):''',
'''def get_chunk(self, paper_id: str, chunk_id: str):
        print("=================================================", flush=True)
        print("ENTER get_chunk", flush=True)
        print("=================================================", flush=True)'''
    ),
    (
'''        return paper_chunks.get(chunk_id)''',
'''        chunk = paper_chunks.get(chunk_id)
        print("=================================================", flush=True)
        print("EXIT get_chunk", flush=True)
        print("=================================================", flush=True)
        return chunk'''
    )
])

# 5. llm.py
instrument_file("backend/rag/llm.py", [
    (
'''def generate(prompt: str, model: str = "llama3"):''',
'''def generate(prompt: str, model: str = "llama3"):
    print("=================================================", flush=True)
    print("ENTER generate", flush=True)
    print("=================================================", flush=True)
    import time
    start = time.perf_counter()
    
    print("Before sending to Ollama", flush=True)
    print(f"Model: {model}", flush=True)
    print(f"Prompt length: {len(prompt)}", flush=True)
    print(f"Approximate token count: {len(prompt.split())}", flush=True)
    print(f"First 300 characters: {prompt[:300]}", flush=True)
    print(f"Last 300 characters: {prompt[-300:]}", flush=True)
'''
    ),
    (
'''        response = requests.post(
            OLLAMA_URL,
            json=payload,
            headers=headers
        )''',
'''        response = requests.post(
            OLLAMA_URL,
            json=payload,
            headers=headers
        )
        print("After response:", flush=True)
        print(f"HTTP status: {response.status_code}", flush=True)
        end = time.perf_counter()
        print(f"Generation time: {end - start:.4f}s", flush=True)
'''
    ),
    (
'''        if response.status_code != 200:''',
'''        if response.status_code != 200:
            print(f"HTTP body: {response.text}", flush=True)
            print(f"HTTP headers: {response.headers}", flush=True)'''
    ),
    (
'''        return {
            "success": True,
            "answer": result["response"]
        }''',
'''        ans = result["response"]
        print(f"Response length: {len(ans)}", flush=True)
        print(f"Function: generate", flush=True)
        print(f"Execution time: {end - start:.4f}s", flush=True)
        print(f"prompt length: {len(prompt)}", flush=True)
        print(f"response length: {len(ans)}", flush=True)
        print("=================================================", flush=True)
        print("EXIT generate", flush=True)
        print("=================================================", flush=True)
        return {
            "success": True,
            "answer": ans
        }'''
    ),
    (
'''    except Exception as e:
        return {
            "success": False,
            "error": f"LLM connection failed: {str(e)}"
        }''',
'''    except Exception as e:
        import traceback
        end = time.perf_counter()
        print(f"Exception type: {type(e)}", flush=True)
        print(f"Exception message: {str(e)}", flush=True)
        print("=================================================", flush=True)
        print("EXIT generate (Exception)", flush=True)
        print("=================================================", flush=True)
        return {
            "success": False,
            "error": f"LLM connection failed: {str(e)}"
        }'''
    )
])

print("Instrumentation complete!")
