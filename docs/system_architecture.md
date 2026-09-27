# AgroMind RAG - System Architecture

This document describes the high-level system architecture, data processing pipeline, and core engineering modules of the AgroMind Agricultural Advisory RAG System.

---

## 🏗️ End-to-End Pipeline Overview

```text
[Government ICAR PDFs / IMD Advisories]
                  │
                  ▼
         02_extract_text.py      ──► Raw Extracted Text
                  │
                  ▼
          03_clean_text.py       ──► Clean Text (Headers/Footers Stripped)
                  │
                  ▼
             04_chunk.py         ──► Semantic Chunks
                  │
                  ▼
           05_metadata.py        ──► Tagged Chunks (District, Crop, Soil, Delay Window)
                  │
                  ▼
             06_embed.py         ──► Vector Embeddings (Dense Vectors)
                  │
                  ▼
       07_build_vector_db.py     ──► Persistent Vector Database (Chroma/FAISS)
                  │
                  ▼
            08_query.py          ──► Context Retriever (Hybrid Search & Metadata Filter)
                  │
                  ▼
          09_generate.py         ──► LLM Prompt Engineering & Response Synthesis
                  │
                  ▼
             10_app.py           ──► User-Facing Web Application (Streamlit/FastAPI)
```

---

## 🎯 Architectural Principles & Constraints

1. **Strict Metadata Tagging**: Every chunk must be enriched with categorical metadata (`district`, `region`, `crop`, `soil_type`, `contingency_type`, `authority`).
2. **Deterministic Pre-filtering**: Queries for a specific district (e.g. Latur) must filter candidates at the vector database level before semantic similarity scoring.
3. **Decoupled Data Pipeline**: Processing steps (Extraction ──► Cleaning ──► Chunking ──► Embedding ──► Vector Indexing) are strictly isolated into distinct, testable CLI scripts under `scripts/`.
4. **Offline Resilience**: Baseline ICAR contingency rules are pre-embedded and indexed, allowing core agronomic advisory generation even when live APIs are unreachable.
