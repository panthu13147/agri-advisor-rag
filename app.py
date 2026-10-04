import streamlit as st
import os
import json
from pathlib import Path
import time
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'chroma_db'

st.set_page_config(page_title="AgriAdvisor Dashboard", page_icon="🌾", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 42px !important; font-weight: 700 !important; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 18px !important; color: #4B5563; margin-top: 0px; margin-bottom: 30px;}
    .status-badge { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    .status-ok { background-color: #D1FAE5; color: #065F46; }
    .param-box { background-color: #1E293B; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid; }
    .param-district { border-color: #3B82F6; }
    .param-crop { border-color: #22C55E; }
    .param-stage { border-color: #F59E0B; }
    .param-enso { border-color: #EF4444; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🌾 AgriAdvisor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">El Niño-Aware Agricultural Advisory System • Powered by Local RAG</p>', unsafe_allow_html=True)

@st.cache_resource
def load_vectorstore():
    if not DB_DIR.exists():
        raise FileNotFoundError(f"ChromaDB not found at {DB_DIR}. Run 07_build_vector_db.py first.")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    return Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)

@st.cache_resource
def load_llm():
    return OllamaLLM(model="llama3.1:8b", temperature=0.3)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2674/2674486.png", width=100)
    st.title("Settings & Status")

    st.subheader("🌐 Language")
    language = st.radio("Output Language:", ["English", "Marathi (मराठी)"])
    st.markdown("---")

    st.subheader("🖥️ System Status")
    try:
        vectorstore = load_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        st.markdown('**Vector DB:** <span class="status-badge status-ok">✅ Connected (3,556 chunks)</span>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Vector DB: Offline — {e}")
        st.stop()

    try:
        llm = load_llm()
        st.markdown('**Local LLM:** <span class="status-badge status-ok">✅ Llama 3.1:8b Ready</span>', unsafe_allow_html=True)
    except:
        st.error("Local LLM: Offline")

    st.markdown("---")
    st.caption("Data Sources: ICAR Contingency Plans, IMD Bulletins, NOAA ONI Index")

# --- MAIN UI: Query Parameters ---
st.markdown("### 📋 Configure Advisory Parameters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    district = st.selectbox("📍 District", ["Latur", "Beed", "Yavatmal", "Amravati"])
with col2:
    crop = st.selectbox("🌱 Crop", ["Cotton", "Soybean", "Tur", "Jowar"])
with col3:
    month = st.selectbox("📅 Sowing Stage", ["Pre-sowing", "Sowing", "Vegetative", "Flowering", "Harvest"])
with col4:
    scenario = st.selectbox("🌊 El Niño Scenario", ["Strong", "Moderate", "Weak", "Neutral"])

st.write("")
generate_btn = st.button("🚀 Generate Precision Advisory & Accuracy Comparison", use_container_width=True, type="primary")
st.markdown("---")

# Language instruction
lang_instruction = "MARATHI (मराठी). Provide the output exclusively in Marathi script." if "Marathi" in language else "ENGLISH."

# --- STRUCTURED RAG PROMPT ---
rag_template = """You are an expert Chief Agricultural Extension Officer advising farmers.
You MUST write the entire response in this language: {lang}

Using the provided context from ICAR, IMD, and NOAA, generate a DETAILED advisory.
Structure your response STRICTLY in the following 4 parameter-wise sections.
Each section MUST correspond to one of the user's input parameters and explain what specific insights were derived from the knowledge base for that parameter.

## 📍 District Analysis: {district}
(What does the ICAR contingency plan say specifically about this district? Soil type, agro-climatic zone, historical drought patterns, district-specific recommendations from the knowledge base.)

## 🌱 Crop-Specific Guidance: {crop}
(What varieties are recommended? What are the sowing windows? Seed rate, spacing, fertilizer dose specific to this crop from the retrieved ICAR/IMD data.)

## 📅 Stage-Specific Actions: {stage}
(What actions should be taken at this particular crop stage? Irrigation scheduling, nutrient management, weed control relevant to this growth phase.)

## 🌊 El Niño Impact Assessment: {scenario} El Niño
(What does the ONI data show? How does a {scenario} El Niño historically affect monsoon rainfall in Maharashtra? What contingency measures does ICAR recommend for this scenario?)

If the context does not contain relevant information for a section, explicitly state: "Note: Generalizing beyond retrieved data for this parameter."
Do not hallucinate specific statistics.

Context from Knowledge Base:
{context}

Detailed Parameter-Wise Advisory:
"""
rag_prompt = PromptTemplate.from_template(rag_template)

# --- BASELINE PROMPT (No RAG) ---
baseline_template = """You are an AI assistant. Answer the following agricultural question.
You MUST write the entire response in this language: {lang}

Structure your response in the following 4 sections:
## 📍 District Analysis: {district}
## 🌱 Crop-Specific Guidance: {crop}
## 📅 Stage-Specific Actions: {stage}
## 🌊 El Niño Impact Assessment: {scenario} El Niño

Question: What is the agricultural advisory for {crop} in {district} district during the {stage} stage under a {scenario} El Niño scenario?

Answer:
"""
baseline_prompt = PromptTemplate.from_template(baseline_template)


def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


# --- GENERATION ---
if generate_btn:
    query_text = f"What is the agricultural contingency plan and advisory for {crop} in {district} district during the {month} stage under a {scenario} El Niño scenario?"

    with st.spinner(f"🔍 Generating: Standard LLM vs. AgriAdvisor RAG ({language})..."):
        try:
            start_time = time.time()

            # 1. Retrieve relevant chunks (pass a plain string!)
            retrieved_docs = retriever.invoke(query_text)
            context_str = format_docs(retrieved_docs)

            # 2. Run BASELINE (no context)
            baseline_result = (baseline_prompt | llm | StrOutputParser()).invoke({
                "lang": lang_instruction,
                "district": district,
                "crop": crop,
                "stage": month,
                "scenario": scenario,
            })

            # 3. Run RAG (with context)
            rag_result = (rag_prompt | llm | StrOutputParser()).invoke({
                "lang": lang_instruction,
                "district": district,
                "crop": crop,
                "stage": month,
                "scenario": scenario,
                "context": context_str,
            })

            elapsed_time = time.time() - start_time
            st.success(f"✅ Generation & Comparison complete in {elapsed_time:.1f} seconds")
            st.markdown(f"**Target:** `{district}` | `{crop}` | `{month}` | `{scenario} El Niño`")

            # --- TABS ---
            tab1, tab2, tab3 = st.tabs([
                "🟢 AFTER RAG (AgriAdvisor)",
                "🔴 BEFORE RAG (Standard AI)",
                "🔎 Retrieved Evidence"
            ])

            with tab1:
                st.markdown("#### ✅ Grounded & Parameter-Wise Advisory")
                st.markdown(rag_result)

            with tab2:
                st.markdown("#### ⚠️ Standard LLM (No Knowledge Base)")
                st.warning("Notice how the standard AI lacks specific district data, invents statistics, or misses official ICAR/IMD guidelines without RAG.")
                st.markdown(baseline_result)

            with tab3:
                st.markdown("#### 📚 Official Source Chunks Used by RAG")
                for i, doc in enumerate(retrieved_docs):
                    src = doc.metadata.get("source_file", "Unknown")
                    doc_type = doc.metadata.get("doc_type", "")
                    label = f"Source {i+1}: {src}"
                    if doc_type:
                        label += f" [{doc_type}]"
                    with st.expander(label):
                        st.code(doc.page_content, language=None)

        except Exception as e:
            st.error(f"An error occurred during generation: {e}")
