# Retrieval Strategy & Search Architecture

This document specifies the hybrid retrieval mechanics, metadata filtering, and reranking strategy used in AgroMind.

---

## 🔍 Retrieval Workflow

```text
User Query: "Latur me monsoon 3 hafte late ho gaya hai, Kaptan/Soybean ki jagah konsi fasal lagayein?"
                                    │
                                    ▼
                      1. Metadata Filter Extractor
                      { district: "Latur", crop: ["Soybean", "All"], contingency: "Delayed Sowing" }
                                    │
                                    ▼
                      2. Vector DB Hard Filtering
                      Candidates = DB.query(filter={ district: "Latur" })
                                    │
                                    ▼
                      3. Semantic Similarity Search (Top-K = 10)
                      Rank candidates by cosine similarity of embeddings
                                    │
                                    ▼
                      4. Context Assembly & Prompt Construction
                      Inject top 3 relevant chunks into LLM prompt with citation IDs
```

---

## 🛡️ Fallback & Scope Guarantee

If zero chunks match the exact district metadata (e.g. specific sub-district query), the retriever falls back to **Region-Level Retrieval** (`region: "Marathwada"`), ensuring reliable agronomic advice is always retrieved from similar regional soil/climate profiles.
