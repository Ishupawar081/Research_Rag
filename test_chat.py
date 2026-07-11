from backend.rag.chat import single_paper_chat
import traceback

try:
    res = single_paper_chat(
        query="what is attention?",
        paper="attention-is-all-you-need-Paper",
        top_k=5,
        user_id="4c559521-dbef-4b40-a23f-e2f68c307ff8"
    )
    print("SUCCESS", res)
except Exception as e:
    print("ERROR:")
    traceback.print_exc()

