# Evaluation Iteration 001
**Date:** 2026-07-10 02:13:05

## Overall Metrics
- **retrieval_precision:** 82.86
- **retrieval_recall:** 85.71
- **faithfulness:** 0.00
- **groundedness:** 0.00
- **hallucination:** 100.00
- **formatting:** 0.00
- **latency:** 36.82
- **pass_rate:** 0.00

## Per Paper
### 2212.00380v1
- **avg_retrieval:** 82.85714285714286
- **avg_faithfulness:** 0.0
- **avg_latency:** 36.823849133082796

## Per Question Failures
### Question: Who are the authors? (Paper: 2212.00380v1)
- **Intent:** METADATA
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: What are the affiliations? (Paper: 2212.00380v1)
- **Intent:** METADATA
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Give abstract (Paper: 2212.00380v1)
- **Intent:** ABSTRACT
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Explain introduction (Paper: 2212.00380v1)
- **Intent:** INTRODUCTION
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Explain methodology (Paper: 2212.00380v1)
- **Intent:** METHOD
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: What are the experimental results? (Paper: 2212.00380v1)
- **Intent:** RESULTS
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Summarize paper (Paper: 2212.00380v1)
- **Intent:** SUMMARY
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: What are the limitations and future work? (Paper: 2212.00380v1)
- **Intent:** CONCLUSION
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Give references (Paper: 2212.00380v1)
- **Intent:** REFERENCES
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: What does Fig. 1. Example of t... illustrate? (Paper: 2212.00380v1)
- **Intent:** GENERAL
- **Category:** Wrong section
- **Root Cause:** Retriever failed to filter sections or match alias
- **Suggested Fix:** Add/modify section aliases
- **Target Module:** backend/rag/retriever.py
- **Answer:** ...

### Question: What does The concept of trans... illustrate? (Paper: 2212.00380v1)
- **Intent:** GENERAL
- **Category:** Wrong section
- **Root Cause:** Retriever failed to filter sections or match alias
- **Suggested Fix:** Add/modify section aliases
- **Target Module:** backend/rag/retriever.py
- **Answer:** ...

### Question: Explain U-Nets are fully-con... (Paper: 2212.00380v1)
- **Intent:** GENERAL
- **Category:** Hallucination
- **Root Cause:** LLM ignored context bounds
- **Suggested Fix:** Strengthen system prompt bounds
- **Target Module:** backend/rag/prompts.py
- **Answer:** ...

### Question: Explain Fig. 1. Audio-Condit... (Paper: 2212.00380v1)
- **Intent:** GENERAL
- **Category:** Wrong chunk
- **Root Cause:** Semantic search pulled irrelevant chunks
- **Suggested Fix:** Improve intent routing or semantic filtering
- **Target Module:** backend/rag/retriever.py
- **Answer:** ...

### Question: Explain with tp the number o... (Paper: 2212.00380v1)
- **Intent:** GENERAL
- **Category:** Wrong chunk
- **Root Cause:** Semantic search pulled irrelevant chunks
- **Suggested Fix:** Improve intent routing or semantic filtering
- **Target Module:** backend/rag/retriever.py
- **Answer:** ...

