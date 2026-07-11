from backend.rag.loader import resources

for paper in resources.registry:

    print()
    print("Title :", paper["title"])
    print("ID    :", paper["paper_id"])