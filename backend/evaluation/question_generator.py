import json
import os
import re

def generate_questions(paper_id):
    """
    Generates generic and paper-specific questions for evaluation.
    """
    questions = []
    
    # 1. Comprehensive Generic Questions
    questions.extend([
        {"query": "Who are the authors?", "intent": "METADATA", "type": "Generic_Metadata"},
        {"query": "What are the affiliations?", "intent": "METADATA", "type": "Generic_Metadata"},
        {"query": "Give abstract", "intent": "ABSTRACT", "type": "Generic_Abstract"},
        {"query": "Explain introduction", "intent": "INTRODUCTION", "type": "Generic_Intro"},
        {"query": "What is the motivation for this work?", "intent": "INTRODUCTION", "type": "Generic_Motivation"},
        {"query": "What are the main contributions?", "intent": "INTRODUCTION", "type": "Generic_Contributions"},
        {"query": "Explain methodology", "intent": "METHOD", "type": "Generic_Method"},
        {"query": "Explain the architecture", "intent": "METHOD", "type": "Generic_Architecture"},
        {"query": "Explain the training procedure", "intent": "METHOD", "type": "Generic_Training"},
        {"query": "What dataset was used?", "intent": "METHOD", "type": "Generic_Dataset"},
        {"query": "What are the experimental results?", "intent": "RESULTS", "type": "Generic_Results"},
        {"query": "What were the evaluation metrics?", "intent": "RESULTS", "type": "Generic_Metrics"},
        {"query": "Summarize paper", "intent": "SUMMARY", "type": "Generic_Summary"},
        {"query": "What are the limitations?", "intent": "CONCLUSION", "type": "Generic_Limitations"},
        {"query": "What is the future work?", "intent": "CONCLUSION", "type": "Generic_FutureWork"},
        {"query": "Give references", "intent": "REFERENCES", "type": "Generic_References"}
    ])
    
    # 2. Dynamic Paper-Specific Questions using robust regex
    graph_file = f"backend/data/graph_final/{paper_id}/graph.json"
    if os.path.exists(graph_file):
        with open(graph_file, "r") as f:
            graph = json.load(f)
            
        nodes = graph.get("nodes", [])
        
        formula_count = 0
        figure_count = 0
        table_count = 0
        algo_count = 0
        ablation_count = 0
        
        # Regex patterns
        eq_pattern = re.compile(r'(?:Equation|Eq\.)\s*\(?(\d+[a-zA-Z]*)\)?', re.IGNORECASE)
        fig_pattern = re.compile(r'(?:Figure|Fig\.)\s*(\d+[a-zA-Z]*)', re.IGNORECASE)
        tab_pattern = re.compile(r'Table\s*([IVXLCDM\d]+[a-zA-Z]*)', re.IGNORECASE)
        algo_pattern = re.compile(r'Algorithm\s*(\d+)', re.IGNORECASE)
        
        for n in nodes:
            t = str(n.get("type", ""))
            text = str(n.get("text", ""))
            title = str(n.get("title", ""))
            
            # Equations
            eq_matches = eq_pattern.findall(text)
            for m in eq_matches:
                if formula_count < 2:
                    questions.append({"query": f"Explain Equation {m}", "intent": "GENERAL", "type": "Dynamic_Formula"})
                    formula_count += 1
                    
            # Figures
            fig_matches = fig_pattern.findall(text)
            for m in fig_matches:
                if figure_count < 2:
                    questions.append({"query": f"What does Figure {m} illustrate?", "intent": "GENERAL", "type": "Dynamic_Figure"})
                    figure_count += 1
                    
            # Tables
            tab_matches = tab_pattern.findall(text)
            for m in tab_matches:
                if table_count < 2:
                    questions.append({"query": f"Explain Table {m}", "intent": "GENERAL", "type": "Dynamic_Table"})
                    table_count += 1
                    
            # Algorithms
            algo_matches = algo_pattern.findall(text)
            for m in algo_matches:
                if algo_count < 1:
                    questions.append({"query": f"Explain Algorithm {m}", "intent": "GENERAL", "type": "Dynamic_Algorithm"})
                    algo_count += 1
                    
            # Sections
            if t == "Section":
                if "ablation" in title.lower() and ablation_count < 1:
                    questions.append({"query": "Explain the ablation study", "intent": "GENERAL", "type": "Dynamic_Section"})
                    ablation_count += 1
                elif "appendix" in title.lower():
                    # Just add one appendix question if found
                    if not any(q["type"] == "Dynamic_Appendix" for q in questions):
                        questions.append({"query": "What is discussed in the appendix?", "intent": "GENERAL", "type": "Dynamic_Appendix"})
                
    # Deduplicate questions in case regex found same eq multiple times
    seen = set()
    unique_questions = []
    for q in questions:
        if q["query"] not in seen:
            seen.add(q["query"])
            unique_questions.append(q)
            
    return unique_questions
