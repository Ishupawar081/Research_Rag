import re
from difflib import SequenceMatcher

from backend.rag.loader import resources

# ==========================================================
# NORMALIZE
# ==========================================================

def normalize(text):

    if text is None:
        return ""

    text = text.lower()

    text = text.replace("-", " ")

    text = text.replace("_", " ")

    text = re.sub(r"[^a-z0-9 ]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==========================================================
# STRING SIMILARITY
# ==========================================================

def similarity(a, b):

    return SequenceMatcher(

        None,

        normalize(a),

        normalize(b)

    ).ratio()


# ==========================================================
# FIND BY PAPER ID
# ==========================================================

def find_by_id(query, user_id):
    query = normalize(query)
    matches = []
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        pid = normalize(paper["paper_id"])
        if query == pid:
            return [paper]
        if pid.startswith(query):
            matches.append(paper)
    return matches


# ==========================================================
# FIND BY TITLE
# ==========================================================

def find_by_title(query, user_id):
    query = normalize(query)
    best_matches = []
    best_score = 0
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        title = normalize(paper["title"])
        score = similarity(query, title)
        if query in title:
            score += 0.25
        if score > best_score:
            best_score = score
            best_matches = [paper]
        elif score == best_score and score > 0:
            best_matches.append(paper)
    if best_score < 0.45:
        return []
    return best_matches


# ==========================================================
# FIND BY ALIAS
# ==========================================================

def find_by_alias(query, user_id):
    query = normalize(query)
    matches = []
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        for alias in paper.get("aliases", []):
            if normalize(alias) == query:
                matches.append(paper)
    return matches


# ==========================================================
# FIND BY AUTHOR
# ==========================================================

def find_by_author(query, user_id):
    query = normalize(query)
    matches = []
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        authors = paper.get("authors", [])
        for author in authors:
            if query in normalize(author):
                matches.append(paper)
                break
    return matches


# ==========================================================
# FIND BY KEYWORD
# ==========================================================

def find_by_keyword(query, user_id):
    query = normalize(query)
    matches = []
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        kws = paper.get("keywords", [])
        for kw in kws:
            if query in normalize(kw):
                matches.append(paper)
                break
    return matches


# ==========================================================
# MAIN RESOLVER
# ==========================================================

def resolve_paper(query, user_id):
    strategies = [
        ("id", find_by_id),
        ("alias", find_by_alias),
        ("title", find_by_title),
        ("author", find_by_author),
        ("keyword", find_by_keyword)
    ]
    for name, strategy_func in strategies:
        matches = strategy_func(query, user_id)
        if matches:
            if len(matches) == 1:
                return matches[0]
            return {
                "is_ambiguous": True,
                "strategy": name,
                "matches": matches
            }
    return None


# ==========================================================
# SEARCH PAPERS
# ==========================================================

def search_papers(query, user_id):
    query = normalize(query)
    results = []
    registry = resources.get_registry(user_id) or []
    for paper in registry:
        score = similarity(query, paper["title"])
        if query in normalize(paper["title"]):
            score += 0.3
        for author in paper.get("authors", []):
            if query in normalize(author):
                score += 0.5
        for kw in paper.get("keywords", []):
            if query in normalize(kw):
                score += 0.4
        if score > 0.35:
            results.append((score, paper))
    results.sort(reverse=True, key=lambda x: x[0])
    return [p for _, p in results]