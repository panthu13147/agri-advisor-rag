# AgriAdvisor — Full Implementation Spec (End to End)

This is a complete build spec, phase by phase, matching the architecture already 
locked in your PPT (Ingestion -> Chunking/Embedding -> Retrieval -> Generation). 
Nothing here contradicts anything already decided — this just makes it buildable.

**One note before you start, not a rule, just worth deciding on purpose:** you 
have a Practical & Oral Exam component on this project. Whatever builds this 
first draft — you, me turn-by-turn, or an agent — the plan is written clearly 
enough that you can read through it and actually explain every phase afterward. 
That's worth doing regardless of which path you pick.

---

## Project Structure

```
agriadvisor/
├── data/
│   └── raw/
│       ├── icar/          # 4 ICAR contingency plan PDFs
│       ├── imd/           # 4 IMD advisory PDFs
│       └── oni/           # NOAA ONI classification table
├── src/
│   ├── ingest.py          # Phase 1 — load + extract text
│   ├── chunk.py           # Phase 2 — split into chunks
│   ├── embed_store.py     # Phase 3 — embeddings + ChromaDB
│   ├── retrieve.py        # Phase 4 — retrieval + scenario weighting
│   ├── generate.py        # Phase 5 — Ollama generation
│   └── pipeline.py        # Ties phases 3-5 together end to end
├── chroma_db/              # generated — persisted vector store
├── app.py                  # Phase 6 — Streamlit frontend
├── evaluate.py              # Phase 7 — RAG vs. no-RAG baseline comparison
├── requirements.txt
└── README.md
```

---

## Phase 0 — Environment Setup

```
python -m venv venv
venv\Scripts\activate          # (you already know this part)

pip install langchain langchain-community langchain-ollama chromadb 
streamlit pdfplumber python-dotenv
```

Confirm both Ollama models are pulled (you likely already have these from JARVIS):
```
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

---

## Phase 1 — Ingestion (`src/ingest.py`)

Goal: load every PDF, extract raw text, tag it with metadata before anything 
else happens to it.

```python
import pdfplumber
import os

def load_documents(data_dir="data/raw"):
    """Returns a list of dicts: {text, district, doc_type, source_file}"""
    documents = []
    
    for doc_type in ["icar", "imd", "oni"]:
        folder = os.path.join(data_dir, doc_type)
        for filename in os.listdir(folder):
            if not filename.endswith(".pdf"):
                continue
            path = os.path.join(folder, filename)
            with pdfplumber.open(path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            
            # District comes from the filename — name your PDFs 
            # "latur.pdf", "beed.pdf", "yavatmal.pdf", "amravati.pdf"
            district = filename.replace(".pdf", "").lower() if doc_type != "oni" else "all"
            
            documents.append({
                "text": text,
                "district": district,
                "doc_type": doc_type,
                "source_file": filename
            })
    return documents
```

**Checkpoint:** run this alone first, print `len(documents)` and the first 
200 characters of one document. Confirm the PDFs actually extracted readable 
text before moving to Phase 2 — scanned/image-based PDFs sometimes extract as 
empty strings, and you want to catch that now, not after chunking.

---

## Phase 2 — Chunking (`src/chunk.py`)

Goal: split each document into smaller, semantically coherent pieces — same 
concept from the RAG explanation earlier in this project.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_documents(documents):
    """Takes Phase 1 output, returns chunks with metadata preserved."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )
    
    all_chunks = []
    for doc in documents:
        pieces = splitter.split_text(doc["text"])
        for piece in pieces:
            all_chunks.append({
                "text": piece,
                "district": doc["district"],
                "doc_type": doc["doc_type"],
                "source_file": doc["source_file"]
            })
    return all_chunks
```

**Checkpoint:** print how many chunks came from each district. If one district 
has drastically fewer chunks than the others, go back and check that PDF 
extracted properly in Phase 1.

---

## Phase 3 — Embedding + Vector Store (`src/embed_store.py`)

Goal: convert every chunk into a vector, store it in ChromaDB with its metadata 
intact, so it can be filtered and searched later.

```python
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

def build_vectorstore(chunks, persist_dir="chroma_db"):
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    texts = [c["text"] for c in chunks]
    metadatas = [
        {"district": c["district"], "doc_type": c["doc_type"], "source": c["source_file"]}
        for c in chunks
    ]
    
    vectorstore = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=persist_dir
    )
    return vectorstore
```

**This is your Day 1 coding milestone** — run Phases 1-3 together as one 
script, confirm `chroma_db/` folder actually gets created with real content in 
it. That's the "documents in, chunked, embedded, stored" checkpoint from 
before.

---

## Phase 4 — Retrieval with Scenario Weighting (`src/retrieve.py`)

This is your one confirmed architecture gap — the part that doesn't exist 
anywhere else in what's been built so far. Two approaches, do the first one:

**Approach A (do this — simple, defensible, actually implementable in your 
timeframe):** bias the retrieval query itself based on scenario, and filter by 
district using metadata before doing semantic search.

```python
SCENARIO_CONTEXT = {
    "Strong": "severe drought conditions, significant rainfall deficit, delayed monsoon",
    "Moderate": "moderate rainfall deficit, some delay in monsoon onset",
    "Weak": "mild rainfall variability, near-normal conditions",
    "Neutral": "normal monsoon conditions, no significant El Niño influence"
}

def retrieve(vectorstore, district, crop, month, scenario, k=5):
    scenario_bias = SCENARIO_CONTEXT[scenario]
    query = f"{crop} farming in {month} under {scenario_bias} in {district} district"
    
    results = vectorstore.similarity_search(
        query,
        k=k,
        filter={"district": district.lower()}
    )
    return results
```

Why this counts as real scenario-weighting: the query text itself shifts 
based on scenario, which shifts which chunks come back as most semantically 
similar — a "Strong" query pulls chunks discussing severe drought language, a 
"Neutral" query pulls chunks discussing normal-year guidance. This is a 
legitimate, explainable mechanism — be ready to explain exactly this if asked 
in your viva.

**Approach B (future work / stretch goal, mention in your report, don't build 
unless Approach A is done early with time to spare):** pre-tag each chunk 
during ingestion with a severity level based on keyword scanning, then filter 
directly on that tag instead of relying on semantic bias alone.

---

## Phase 5 — Generation (`src/generate.py`)

Goal: take retrieved chunks + user query, generate a Recommendation -> Reason 
-> Source structured answer, grounded only in what was retrieved.

```python
import ollama

SYSTEM_PROMPT = """You are AgriAdvisor, an assistant for KVK officers and 
agricultural extension workers in Maharashtra. You answer ONLY using the 
provided context below. Do not use outside knowledge. 

Structure every answer in exactly this format:

RECOMMENDATION: [the specific actionable advice]
REASON: [why this applies, referencing the El Nino scenario and conditions]
SOURCE: [which document(s) this came from]

If the context does not contain enough information to answer confidently, 
say so explicitly instead of guessing."""

def generate_advisory(query_details, retrieved_chunks):
    context = "\n\n".join(
        f"[Source: {c.metadata['source']}]\n{c.page_content}" 
        for c in retrieved_chunks
    )
    
    user_message = f"""Context:
{context}

Question: A KVK officer in {query_details['district']} needs advice for 
{query_details['crop']} during {query_details['month']}, under a 
{query_details['scenario']} El Nino scenario. What should they advise?"""

    response = ollama.chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    return response["message"]["content"]
```

---

## Phase 6 — Pipeline (`src/pipeline.py`)

Ties Phases 3-5 together into one callable function — this is what both the 
Streamlit app and the evaluation script will import and use.

```python
from src.embed_store import build_vectorstore
from src.retrieve import retrieve
from src.generate import generate_advisory

class AgriAdvisorPipeline:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def get_advisory(self, district, crop, month, scenario):
        chunks = retrieve(self.vectorstore, district, crop, month, scenario)
        query_details = {"district": district, "crop": crop, "month": month, "scenario": scenario}
        result = generate_advisory(query_details, chunks)
        return result, chunks   # return chunks too, for the "view retrieved context" UI feature
```

---

## Phase 7 — Streamlit Frontend (`app.py`)

Matches the dashboard design already agreed — sidebar inputs, structured 
output panel.

```python
import streamlit as st
from src.pipeline import AgriAdvisorPipeline
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

st.title("AgriAdvisor — El Nino-Aware Agricultural Advisory")

@st.cache_resource
def load_pipeline():
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    return AgriAdvisorPipeline(vectorstore)

pipeline = load_pipeline()

with st.sidebar:
    st.header("Query Parameters")
    district = st.selectbox("District", ["Latur", "Beed", "Yavatmal", "Amravati"])
    crop = st.selectbox("Crop", ["Cotton", "Soybean", "Tur", "Jowar"])
    month = st.selectbox("Month / Stage", ["Pre-sowing", "Sowing", "Vegetative", "Flowering", "Harvest"])
    scenario = st.selectbox("El Nino Scenario", ["Strong", "Moderate", "Weak", "Neutral"])
    generate_btn = st.button("Generate Advisory")

if generate_btn:
    with st.spinner("Retrieving and generating advisory..."):
        result, chunks = pipeline.get_advisory(district, crop, month, scenario)
    
    st.subheader(f"Advisory for: {district} — {crop} — {month} — {scenario} El Nino")
    st.write(result)
    
    with st.expander("View retrieved source chunks (transparency)"):
        for c in chunks:
            st.markdown(f"**Source:** {c.metadata['source']}")
            st.text(c.page_content[:300] + "...")
```

---

## Phase 8 — Evaluation Script (`evaluate.py`)

This is what produces your Result Analysis section — the side-by-side proof 
that RAG beats a plain LLM.

```python
import ollama
from src.pipeline import AgriAdvisorPipeline
# ... load pipeline same as app.py

test_cases = [
    {"district": "Latur", "crop": "Soybean", "month": "Sowing", "scenario": "Strong"},
    {"district": "Yavatmal", "crop": "Cotton", "month": "Sowing", "scenario": "Moderate"},
    {"district": "Amravati", "crop": "Tur", "month": "Vegetative", "scenario": "Weak"},
]

for case in test_cases:
    rag_answer, _ = pipeline.get_advisory(**case)
    
    plain_response = ollama.chat(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": 
            f"What agricultural advice would you give for {case['crop']} in "
            f"{case['district']} during {case['month']} under a {case['scenario']} El Nino year?"}]
    )
    baseline_answer = plain_response["message"]["content"]
    
    print(f"=== {case} ===")
    print(f"RAG (grounded):\n{rag_answer}\n")
    print(f"Baseline (no retrieval):\n{baseline_answer}\n")
    print("=" * 60)
```

Save this output — screenshot or copy the printed comparisons directly into 
your Result Analysis slide/section.

---

## Build Order — Do Not Skip Ahead

1. Phase 0 (setup) -> Phase 1 (ingestion) -> **checkpoint:** text actually extracted
2. Phase 2 (chunking) -> **checkpoint:** reasonable chunk counts per district
3. Phase 3 (embedding/store) -> **checkpoint:** `chroma_db/` has real content — **this is Day 1's finish line**
4. Phase 4 (retrieval) -> **checkpoint:** manually run a query, confirm returned chunks actually look relevant to the district/scenario
5. Phase 5 (generation) -> **checkpoint:** confirm output actually follows Recommendation/Reason/Source format
6. Phase 6 (pipeline) -> wires 3-5 together, no new logic, just connecting
7. Phase 7 (Streamlit) -> **this is your demo-ready milestone**
8. Phase 8 (evaluation) -> generates your Result Analysis content

Each checkpoint is a real stopping point — don't move to the next phase until 
the current one's checkpoint actually passes. If you're using an agent to 
build this, the same rule applies: review and understand the output of each 
phase before letting it continue to the next one.
