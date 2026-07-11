from rag.retriever import search

results = search(

    "variation field",

    top_k=3

)

for r in results:

    print()

    print("="*60)

    print(r["paper_title"])

    print(r["section_title"])

    print(r["score"])

    print()

    print(r["text"][:500])