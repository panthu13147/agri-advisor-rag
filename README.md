# 🌾 AgriAdvisor: El Niño-Aware Agricultural Advisory System

An offline, domain-specific Retrieval-Augmented Generation (RAG) system for agricultural contingency crop planning in Maharashtra (Marathwada & Vidarbha regions), powered by local LLMs via Ollama.

---

## 🎯 Target Scope
- **Districts:** Latur, Beed (Marathwada) | Yavatmal, Amravati (Vidarbha)
- **Key Crops:** Cotton, Soybean, Tur (Pigeonpea), Jowar
- **Data Sources:** ICAR District Contingency Plans, IMD Agro-advisories, NOAA Oceanic Niño Index (ONI).

---

## 🚀 Quick Start Guide (How to Run on Any Machine)

Follow these simple steps to run this project on your system:

### 1. Prerequisites
- **Python 3.10+** installed ([Download Python](https://www.python.org/downloads/))
- **Git** installed ([Download Git](https://git-scm.com/))
- **Ollama** installed ([Download Ollama](https://ollama.com/))

### 2. Pull Required AI Models
Open your terminal / command prompt and run:
```bash
# Pull the embedding model (used for vector search)
ollama pull nomic-embed-text:v1.5

# Pull the local LLM
ollama pull llama3.1:8b

# Ensure Ollama server is running
ollama serve
```

### 3. Clone the Repository
```bash
git clone https://github.com/panthu13147/agri-advisor-rag.git
cd agri-advisor-rag
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Launch the Dashboard
```bash
streamlit run app.py
```
The app will automatically open in your default browser at:
👉 **`http://localhost:8501`**

> **Note:** The pre-indexed vector database (`chroma_db/`) containing 3,556 domain chunks is included in the repo, so you do **not** need to re-index the raw PDFs to start using the app.

---

## 🌟 Key Features
- **Bilingual Interface:** Instant seamless switching between English and Marathi (मराठी) across all UI elements and LLM responses.
- **A/B Testing Comparison:** Side-by-side view comparing raw LLM baseline output vs. grounded RAG output.
- **Retrieved Evidence Inspector:** Full traceability showing exact ICAR chunks, sources, and similarity scores.
- **Real-Time Accuracy & Confusion Matrix:** Live evaluation calculating True Positives, Hallucination Prevention, and Specific Detail Recall.

---

## 🏗️ Tech Stack
- **Frontend / UI:** Streamlit
- **LLM Engine:** Llama 3.1 8B (via Ollama)
- **Embedding Model:** `nomic-embed-text:v1.5` (768 dimensions)
- **Vector Database:** ChromaDB (Persistent SQLite + HNSW Index)
- **RAG Framework:** LangChain Core / LangChain Community
