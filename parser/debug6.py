import json

with open("graph_3/2212.00187v1/graph.json") as f:
    graph=json.load(f)

for node in graph["nodes"]:

    if node["type"]=="Section":

        print(node)

        break