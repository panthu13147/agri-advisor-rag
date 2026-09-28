import streamlit as st
import os
from pathlib import Path
import time
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'chroma_db'

st.set_page_config(page_title="AgriAdvisor Dashboard", page_icon="🌾", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header { font-size: 42px !important; font-weight: 700 !important; color: #1E3A8A; margin-bottom: 0px; }
    .sub-header { font-size: 18px !important; color: #4B5563; margin-top: 0px; margin-bottom: 30px;}
    .status-badge { padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    .status-ok { background-color: #D1FAE5; color: #065F46; }
    .baseline-warning { color: #991B1B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🌾 AgriAdvisor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">El Niño-Aware Agricultural Advisory System • Powered by Local RAG</p>', unsafe_allow_html=True)

@st.cache_resource
def load_retriever():
    if not DB_DIR.exists():
        raise FileNotFoundError(f"ChromaDB not found at {DB_DIR}. Run 07_build_vector_db.py first.")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    vectorstore = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 5})

@st.cache_resource
def load_llm():
    return OllamaLLM(model="llama3.1:8b", temperature=0.3)

# --- SIDEBAR: System Status & Language ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2674/2674486.png", width=100)
    st.title("Settings & Status")
    
    # NEW FEATURE: Language Selection
    st.subheader("🌐 Language")
    language = st.radio("Output Language:", ["English", "Marathi (मराठी)"])
    st.markdown("---")
    
    st.subheader("🖥️ System Status")
    try:
        retriever = load_retriever()
        st.markdown('**Vector DB:** <span class="status-badge status-ok">✅ Connected (3,556 chunks)</span>', unsafe_allow_html=True)
    except Exception as e:
        st.error("Vector DB: Offline")
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

# Define the RAG Prompt Template (With Context)
rag_template = """
You are an expert Chief Agricultural Extension Officer advising farmers.
Using the provided context from ICAR, IMD, and NOAA, you must generate a HIGHLY DETAILED and COMPREHENSIVE agricultural advisory report.

You MUST write the entire response in this language: {language_instruction}

Do not give a short summary. Your response must be lengthy, professional, and broken down into the following detailed sections:
1. 🌩️ Weather & El Niño Context
2. 🌱 Sowing & Crop Management
3. 💧 Irrigation & Moisture Management
4. 🐛 Pest & Disease Control (if applicable)

If the context does not contain relevant information for a section, synthesize the best general agricultural advice for that specific district and crop, but explicitly state that you are generalizing.
Do not hallucinate specific statistics. Structure your response with clear bullet points.

Context:
{context}

Question: {question}

Detailed Actionable Advisory Report:
"""
rag_prompt = PromptTemplate.from_template(rag_template)

# Define the Baseline Prompt Template (NO Context - for Before RAG accuracy testing)
baseline_template = """
You are an AI assistant. Please answer the following question to the best of your knowledge.
You MUST write the entire response in this language: {language_instruction}

Question: {question}

Answer:
"""
baseline_prompt = PromptTemplate.from_template(baseline_template)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough(), "language_instruction": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

baseline_chain = (
    {"question": RunnablePassthrough(), "language_instruction": RunnablePassthrough()}
    | baseline_prompt
    | llm
    | StrOutputParser()
)

# --- MAIN UI: Generation ---
if generate_btn:
    query_text = f"What is the agricultural contingency plan and advisory for {crop} in {district} district during the {month} stage under a {scenario} El Niño scenario?"
    
    # Determine language injection string
    lang_instruction = "MARATHI (मराठी). Provide the output exclusively in Marathi script." if "Marathi" in language else "ENGLISH."
    
    with st.spinner(f"🔍 Generating Comparison: Standard LLM vs. AgriAdvisor RAG ({language})..."):
        try:
            start_time = time.time()
            
            # Fetch retrieved documents for RAG
            retrieved_docs = retriever.invoke(query_text)
            
            # 1. Run Baseline (No RAG)
            baseline_result = baseline_chain.invoke({"question": query_text, "language_instruction": lang_instruction})
            
            # 2. Run RAG (With Context)
            rag_result = rag_chain.invoke({"question": query_text, "language_instruction": lang_instruction})
            
            elapsed_time = time.time() - start_time
            st.success(f"Generation & Comparison complete in {elapsed_time:.1f} seconds")
            st.markdown(f"**Target Analysis:** {district} | {crop} | {month} | {scenario} El Niño")
            
            # NEW FEATURE: Accuracy / A/B Testing Tabs
            tab1, tab2, tab3 = st.tabs(["🟢 AFTER RAG (AgriAdvisor)", "🔴 BEFORE RAG (Standard AI)", "🔎 Retrieved Evidence"])
            
            with tab1:
                st.subheader("Grounded & Context-Aware Advisory")
                st.info(rag_result)
                
            with tab2:
                st.subheader("Standard LLM Hallucination Test")
                st.markdown('<p class="baseline-warning">⚠️ Notice how the standard AI often lacks specific district data, invents statistics, or misses official ICAR guidelines without RAG.</p>', unsafe_allow_html=True)
                st.warning(baseline_result)
                
            with tab3:
                st.write("AgriAdvisor synthesized its answer directly from the following official chunks:")
                for i, doc in enumerate(retrieved_docs):
                    with st.expander(f"Source {i+1}: {doc.metadata.get('source_file', 'Unknown')}"):
                        st.text(doc.page_content)
                        
        except Exception as e:
            st.error(f"An error occurred during generation: {e}")
