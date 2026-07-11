from rag.loader import resources

resources.info()

paper = resources.registry[0]

print()

print("First Paper")

print(paper["title"])

chunk = resources.get_chunk(

    paper["paper_id"],

    "metadata"

)

print()

print(chunk["paper_title"])