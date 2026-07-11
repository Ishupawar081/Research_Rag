import requests
import json
import time

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

MODEL = "qwen2.5:1.5b"      # Change if using another model


def test_llm():

    payload = {
        "model": MODEL,
        "prompt": "Say hello in one sentence.",
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 50
        }
    }

    print("=" * 80)
    print("Testing Ollama")
    print("=" * 80)
    print("Model:", MODEL)
    print()

    start = time.time()

    try:

        print("Sending request...")

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=(10, 120)
        )

        print("HTTP Status:", response.status_code)

        response.raise_for_status()

        data = response.json()

        end = time.time()

        print()
        print("=" * 80)
        print("SUCCESS")
        print("=" * 80)
        print("Time:", round(end - start, 2), "seconds")
        print()

        print("Response:")
        print("-" * 80)
        print(data.get("response", "No response"))
        print("-" * 80)

        print()
        print("Model:", data.get("model"))
        print("Prompt Tokens:", data.get("prompt_eval_count"))
        print("Generated Tokens:", data.get("eval_count"))

    except Exception as e:

        end = time.time()

        print()
        print("=" * 80)
        print("FAILED")
        print("=" * 80)
        print("Elapsed:", round(end - start, 2), "seconds")
        print()
        print(type(e).__name__)
        print(e)


if __name__ == "__main__":
    test_llm()