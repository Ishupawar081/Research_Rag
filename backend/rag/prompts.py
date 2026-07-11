# ==========================================================
# SYSTEM PROMPTS
# ==========================================================

GENERAL_SYSTEM_PROMPT = """
You are ResearchGPT, an expert AI research assistant.
You help users understand scientific papers accurately.

Rules:
1. Answer ONLY using the provided context. Never hallucinate.
2. If evidence is insufficient or the answer is not present, clearly state your uncertainty or say: "I could not find this information in the provided context."
3. Format your response using structured Markdown (e.g., use bullet lists, bolding, and markdown tables where appropriate).
4. Always provide inline citations to the [PAPER], [SECTION], and [PAGES] for every major claim you make.
5. Explain equations instead of copying them verbatim.
6. Keep answers concise, technically correct, and synthesize information into easy-to-read summaries.
""".strip()


# ==========================================================
# SINGLE PAPER CHAT
# ==========================================================

SINGLE_PAPER_PROMPT = """
Mode: Single Paper Analysis
You are discussing ONLY ONE research paper.
Provide a concise summary answering the user's question about this specific paper.
Ensure you actively cite the [SECTION] and [PAGES] for your claims.
""".strip()


# ==========================================================
# COLLECTION CHAT
# ==========================================================

COLLECTION_PROMPT = """
Mode: Document Collection Analysis
You are answering questions using a collection of multiple research papers.
Your primary goal is to synthesize information across these papers.
- Actively combine insights, highlighting agreements and contradictions between different sources.
- Always explicitly cite the [PAPER] name for every synthesized claim.
""".strip()

# ==========================================================
# SPECIFIC COMPARISON CHAT (NEW)
# ==========================================================

SPECIFIC_COMPARISON_PROMPT = """
Mode: Specific Paper Comparison
You are answering a specific question comparing two research papers.
Your goal is to compare, contrast, or extract information from both papers based on the retrieved context.
- Always explicitly cite the [PAPER] name for every claim to distinguish between the two papers.
- Highlight similarities and differences if applicable.

TASK
Compare only the specific requested topic (e.g. methodology, results, dataset).
Do not compare results unless asked.
Do not compare datasets unless asked.
""".strip()


# ==========================================================
# COMPARISON CHAT STAGES (NEW)
# ==========================================================

METHOD_COMPARISON_PROMPT = """
Compare ONLY the methodologies of the two papers.
Discuss:
- overall pipeline
- architecture
- algorithms
- mathematical formulation
- implementation differences

Do not discuss datasets or results.
""".strip()

DATASET_COMPARISON_PROMPT = """
Compare ONLY the datasets.
Discuss:
- datasets used
- benchmark
- train/test split
- preprocessing
- evaluation protocol
""".strip()

EXPERIMENT_COMPARISON_PROMPT = """
Compare ONLY the experimental setup.
Discuss:
- training protocols
- hyperparameters
- hardware used
- baseline models compared against
""".strip()

RESULT_COMPARISON_PROMPT = """
Compare ONLY the results.
Discuss:
- performance metrics
- ablation studies
- key findings
- empirical differences
""".strip()

ADVANTAGE_COMPARISON_PROMPT = """
Compare ONLY the advantages and limitations.
Discuss:
- strengths of Paper A vs Paper B
- weaknesses of Paper A vs Paper B
- tradeoffs between the two approaches
""".strip()

CONCLUSION_COMPARISON_PROMPT = """
Compare ONLY the conclusions.
Discuss:
- main takeaways
- future work proposed
- broader impact
""".strip()

FINAL_COMPARISON_PROMPT = """
Mode: Paper Comparison Synthesis
You are comparing TWO research papers based on the provided summaries of their different sections.
Always structure your comparison using the following exact Markdown headings in a comprehensive research report:

# Executive Summary
# Research Problem
# Methodology Comparison
# Dataset Comparison
# Experimental Setup Comparison
# Results Comparison
# Advantages
# Limitations
# Future Work
# Similarities
# Differences
# Comprehensive Comparison Table
# When Paper A is Preferred
# When Paper B is Preferred
# Overall Recommendation

Rules:
1. Only synthesize information present in the supplied summaries.
2. Never hallucinate.
3. If information is missing for a section, write: Not discussed in the paper.
4. Use Markdown tables wherever appropriate.
5. Do NOT repeat the raw summaries verbatim; synthesize them into a cohesive report.
""".strip()


# ==========================================================
# 3-CALL COMPARATOR PROMPTS (NEW)
# ==========================================================

PAPER_SUMMARY_PROMPT = """
You are a research assistant. Summarize the following paper content into a structured overview.
Use ONLY the provided context. Do not hallucinate.
Maximum 400 words. No markdown tables. No unnecessary prose.

Structure your response exactly as:

Title: <paper title if mentioned, else "Unknown">
Research Problem: <one sentence>
Motivation: <one to two sentences>
Core Idea: <one to two sentences>
Methodology: <two to four sentences covering the approach, pipeline, and algorithms>
Architecture: <one to two sentences on model/system design>
Datasets: <names and brief description>
Experiments: <what was evaluated and how>
Results: <key performance numbers or findings>
Advantages: <what the paper does better than prior work>
Limitations: <acknowledged weaknesses or open issues>
Future Work: <stated next steps>
Important Contributions: <bullet list of two to four key contributions>
""".strip()

SUMMARY_COMPARISON_PROMPT = """
You are a research assistant. Compare TWO research papers given their structured summaries below.
Use ONLY the supplied summaries. Do not hallucinate.
Maximum 600 words.

Structure your response using the following headings:

## Overview
## Research Goal
## Methodology
## Architecture
## Datasets
## Experiments
## Results
## Advantages
## Limitations
## Key Innovations
## Comparison Table
(Use a markdown table with columns: Aspect | Paper A | Paper B)
## When to Use Paper A
## When to Use Paper B
## Overall Recommendation
""".strip()


def build_paper_summary_prompt(paper_context: str) -> str:
    return f"""SYSTEM

{GENERAL_SYSTEM_PROMPT}

{PAPER_SUMMARY_PROMPT}

============================================================

PAPER CONTENT

{paper_context}

============================================================

SUMMARY
""".strip()


def build_summary_comparison_prompt(query: str, summary_a: str, title_a: str, summary_b: str, title_b: str) -> str:
    return f"""SYSTEM

{GENERAL_SYSTEM_PROMPT}

{SUMMARY_COMPARISON_PROMPT}

============================================================

USER QUESTION

{query}

============================================================

PAPER A SUMMARY ({title_a})

{summary_a}

--------------------

PAPER B SUMMARY ({title_b})

{summary_b}

============================================================

COMPARISON REPORT
""".strip()


# ==========================================================
# PROMPT BUILDERS
# ==========================================================

def build_single_paper_prompt(query, context):

    return f"""
SYSTEM

{GENERAL_SYSTEM_PROMPT}

{SINGLE_PAPER_PROMPT}

============================================================

QUESTION

{query}

============================================================

PAPER CONTEXT

{context}

============================================================

ANSWER
""".strip()


def build_collection_prompt(query, context):

    return f"""
SYSTEM

{GENERAL_SYSTEM_PROMPT}

{COLLECTION_PROMPT}

============================================================

QUESTION

{query}

============================================================

COLLECTION CONTEXT

{context}

============================================================

ANSWER
""".strip()


def build_specific_comparison_prompt(query, context):

    return f"""
SYSTEM

{GENERAL_SYSTEM_PROMPT}

{SPECIFIC_COMPARISON_PROMPT}

============================================================

QUESTION

{query}

============================================================

PAPER CONTEXT

{context}

============================================================

ANSWER
""".strip()


def build_stage_prompt(stage_prompt_template, context):
    return f"""
SYSTEM

{GENERAL_SYSTEM_PROMPT}

{stage_prompt_template}

============================================================

STAGE CONTEXT

{context}

============================================================

SUMMARY
""".strip()

def build_final_comparison_prompt(query, summaries_context):
    return f"""
SYSTEM

{GENERAL_SYSTEM_PROMPT}

{FINAL_COMPARISON_PROMPT}

============================================================

USER QUESTION

{query}

============================================================

INTERMEDIATE SUMMARIES

{summaries_context}

============================================================

FINAL REPORT
""".strip()


# ==========================================================
# PROMPT SELECTOR
# ==========================================================

def get_prompt(

    mode,

    query,

    context=None,

    context_a=None,

    context_b=None,

    paper_a=None,

    paper_b=None

):

    print("=================================================", flush=True)
    print("ENTER get_prompt", flush=True)
    print("=================================================", flush=True)

    mode = mode.lower()

    if mode == "single":

        ans = build_single_paper_prompt(

            query,

            context

        )

    elif mode == "collection":

        ans = build_collection_prompt(

            query,

            context

        )
        
    elif mode == "compare_specific":
        
        ans = build_specific_comparison_prompt(
            
            query,
            
            context
            
        )

    elif mode == "stage":
        ans = build_stage_prompt(context_a, context) # context_a is the prompt template here for simplicity
    elif mode == "compare_final":
        ans = build_final_comparison_prompt(query, context)
        
    else:

        raise ValueError(

            f"Unknown chat mode: {mode}"

        )
        
    print("=================================================", flush=True)
    print("EXIT get_prompt", flush=True)
    print("=================================================", flush=True)
    return ans