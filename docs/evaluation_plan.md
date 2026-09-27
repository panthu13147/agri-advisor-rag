# RAG Evaluation Plan

This document outlines the evaluation framework, ground-truth benchmark datasets, and quantitative metrics used to validate the AgroMind RAG pipeline.

---

## 📈 Key Evaluation Metrics

1. **Retrieval Precision & Recall@K**:
   - Are the top 3 retrieved chunks containing the ground-truth ICAR contingency advice for the queried district & crop condition?
2. **Faithfulness (Hallucination Rate)**:
   - Does the generated advice strictly follow the retrieved ICAR/IMD context without inventing non-recommended pesticide dosages or unapproved crop varieties?
3. **Answer Relevance**:
   - Does the synthesized output directly answer the farmer's query in clear, actionable regional phrasing?

---

## 🧪 Benchmark Test Set (`tests/ground_truth_eval.json`)

A curated set of 20 realistic farmer query scenarios across Beed, Latur, Yavatmal, and Amravati with verified expert ground-truth recommendations from ICAR PDFs.
