# AgroMind RAG: Maharashtra Agricultural Advisory System

A domain-specific Retrieval-Augmented Generation (RAG) system for agricultural contingency crop planning in Maharashtra (Marathwada & Vidarbha regions).

## Representative Scope

- **Marathwada**: Beed, Latur (VNMKV Parbhani)
- **Vidarbha**: Yavatmal, Amravati (PDKV Akola)

## Repository Structure

```
PBL_complete/
├── knowledge_base/        # Multi-stage data pipeline (raw_pdfs, metadata, chunks, vector_db)
├── backend/               # FastAPI / LangChain RAG pipeline & API handlers
├── frontend/              # Web user interface
├── scripts/               # Ingestion, extraction, chunking, and embedding scripts
├── notebooks/             # Data exploration & chunk strategy prototyping
├── docs/                  # System architecture & design documents
├── report/                # Project report & LaTeX sources
├── presentation/          # Slide deck & presentation materials
└── tests/                 # Unit & integration tests for RAG pipeline
```
