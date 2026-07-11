def detect_query_intent(query: str):
    q = query.lower()
    
    if any(k in q for k in ["author", "authors", "email", "emails", "affiliation", "affiliations", "title", "journal", "conference", "doi", "arxiv", "keywords", "publication"]):
        return "METADATA"
        
    if any(k in q for k in ["summary", "summarize", "main idea", "key contributions", "compare contributions"]):
        return "SUMMARY"
        
    SECTION_ALIASES = {
        "ABSTRACT": ["abstract"],
        "INTRODUCTION": ["introduction", "background", "overview", "motivation", "preliminaries"],
        "METHOD": ["method", "methods", "methodology", "approach", "framework", "architecture", "pipeline", "design", "implementation"],
        "RESULTS": ["results", "experiments", "evaluation", "analysis", "performance"],
        "CONCLUSION": ["conclusion", "discussion", "future work", "limitations"],
        "REFERENCES": ["references", "bibliography"],
        "DATASET": ["dataset", "datasets", "data", "experimental setup"]
    }
    
    for intent, aliases in SECTION_ALIASES.items():
        if any(a in q for a in aliases):
            return intent
            
    return "GENERAL"

for q in ["Summarize collection", "Compare methods", "Common datasets", "Shared limitations"]:
    print(f"{q}: {detect_query_intent(q)}")
