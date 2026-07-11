import json

with open('graph_po3/2212.00193v2/graph_stage2.json') as f:
    ir = json.load(f)

# Replicate the logic in 5.py
for node in ir["nodes"]:
    node_type = node["type"]
    is_real_section = False # simplified
    
    if node_type == "SectionHeaderItem" and not is_real_section:
        node_type = "Paragraph"
        
    print(f"Adding Node {node['id']} as {node_type}")
    if node['id'] == 1:
        print("^^^ Node 1 added!")
