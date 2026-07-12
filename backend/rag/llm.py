import json
import requests
import time
import os

# ==========================================================
# CONFIG
# ==========================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

DEFAULT_MODEL = "qwen2.5:1.5b"

DEFAULT_TEMPERATURE = 0.2

DEFAULT_TOP_P = 0.9

DEFAULT_MAX_TOKENS = 1024


# ==========================================================
# GENERATE
# ==========================================================

def generate(
    prompt: str,
    model=DEFAULT_MODEL,
    temperature=DEFAULT_TEMPERATURE,
    top_p=DEFAULT_TOP_P,
    max_tokens=DEFAULT_MAX_TOKENS,
    is_comparison=False,
    is_intermediate=False
):
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

    # Determine num_predict. For comparisons or general queries, cap it to prevent infinite loops.
    if is_intermediate:
        num_predict = 500
        req_timeout = (5.0, 120.0)
    elif is_comparison:
        num_predict = 2000
        req_timeout = (5.0, 900.0)
    else:
        num_predict = min(max_tokens, 500)
        req_timeout = (5.0, 300.0)

    options = {
        "temperature": temperature,
        "top_p": top_p,
        "num_predict": num_predict
    }

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": options
    }

    print(f"--- Ollama Request Debug ---", flush=True)
    print(f"Model Name: {model}", flush=True)
    print(f"Prompt Length: {len(prompt)} chars", flush=True)
    print(f"num_predict: {num_predict}", flush=True)
    print(f"timeout limit: 120.0s", flush=True)
    print(f"Generation Options: {options}", flush=True)
    print(f"----------------------------", flush=True)

    last_error = "Unknown error"

    for attempt in range(2):
        try:
            t_send = time.time()
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                timeout=req_timeout
            )
            t_recv = time.time()
            print("After response:", flush=True)
            print(f"HTTP status: {response.status_code}", flush=True)
            end = time.perf_counter()
            print(f"Time to send request & receive response (stream=False): {t_recv - t_send:.4f}s", flush=True)
            print(f"Total Generation time limit perceived: {end - start:.4f}s", flush=True)

            if response.status_code != 200:
                print(f"HTTP body: {response.text}", flush=True)
                print(f"HTTP headers: {response.headers}", flush=True)

            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise ValueError("Failed to parse JSON response from Ollama.")

            if not isinstance(data, dict) or "response" not in data:
                raise ValueError("Invalid response format from Ollama.")

            ans = data["response"]
            print(f"Response length: {len(ans)}", flush=True)
            
            # Additional required logs
            total_duration_s = data.get("total_duration", 0) / 1e9
            load_duration_s = data.get("load_duration", 0) / 1e9
            prompt_eval_duration_s = data.get("prompt_eval_duration", 0) / 1e9
            eval_duration_s = data.get("eval_duration", 0) / 1e9
            prompt_tokens = data.get("prompt_eval_count", 0)
            gen_tokens = data.get("eval_count", 0)
            
            print(f"Ollama load_duration: {load_duration_s:.4f}s", flush=True)
            print(f"Ollama prompt_eval_duration (Time to First Token): {prompt_eval_duration_s:.4f}s", flush=True)
            print(f"Ollama eval_duration (Generation time): {eval_duration_s:.4f}s", flush=True)
            print(f"Ollama total_duration: {total_duration_s:.4f}s", flush=True)
            print(f"Tokens generated: {gen_tokens} / {num_predict} limit", flush=True)
            
            if eval_duration_s > 0:
                print(f"Generation speed: {gen_tokens / eval_duration_s:.2f} tokens/s", flush=True)

            print("=================================================", flush=True)
            print("EXIT generate", flush=True)
            print("=================================================", flush=True)

            return {
                "success": True,
                "answer": ans,
                "model": data.get("model", model),
                "generation_time": total_duration_s,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": gen_tokens
                }
            }

        except requests.exceptions.ConnectionError as e:
            last_error = "Ollama is unavailable. Please ensure the Ollama service is running."
            print(f"Exception type: {type(e)}", flush=True)
            print(f"Exception message: {str(e)}", flush=True)
        except requests.exceptions.Timeout as e:
            last_error = "Request to Ollama timed out."
            print(f"Exception type: {type(e)}", flush=True)
            print(f"Exception message: {str(e)}", flush=True)
        except Exception as e:
            last_error = str(e)
            print(f"Exception type: {type(e)}", flush=True)
            print(f"Exception message: {str(e)}", flush=True)

    print("=================================================", flush=True)
    print("EXIT generate (Failure)", flush=True)
    print("=================================================", flush=True)

    return {
        "success": False,
        "answer": "",
        "error": last_error
    }


# ==========================================================
# STREAMING
# ==========================================================

def generate_stream(
    prompt: str,
    model=DEFAULT_MODEL
):

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    try:

        t0 = time.time()
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            stream=True,
            timeout=(5.0, 600.0)
        )
        print("POST finished in", time.time() - t0)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        yield "Error: Ollama is unavailable. Please ensure the Ollama service is running."
        return
    except requests.exceptions.Timeout:
        yield "Error: Request to Ollama timed out."
        return
    except Exception as e:
        yield f"Error: {str(e)}"
        return

    for line in response.iter_lines():
        if not line:
            continue

        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        if isinstance(data, dict) and "response" in data:
            yield data["response"]


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    test_prompt = """
SYSTEM

You are a helpful assistant.

QUESTION

Explain the variation field.

CONTEXT

MixVoxels proposes a variation field for identifying dynamic voxels.
The variation field is trained using pixel-level temporal variance.
Section 3.3 introduces the complete formulation.
Training takes less than 30 seconds.
"""

    result = generate(prompt=test_prompt)

    print()
    print("=" * 80)
    print(result["answer"])