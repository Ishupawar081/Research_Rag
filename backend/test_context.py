from rag.retriever import search
from rag.context_builder import prepare_context

query = "variation field"

results = search(

    query,

    top_k=10

)

package = prepare_context(

    query,

    results

)

print()

print("=" * 100)

print(package["context"])

print()

print("=" * 100)

print("SOURCES")

print()

for s in package["sources"]:

    print(s)