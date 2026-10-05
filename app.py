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
    # num_predict=2048 is critical here because Marathi script consumes 
    # significantly more tokens than English, causing early truncation.
    return OllamaLLM(model="llama3.1:8b", temperature=0.3, num_predict=2048)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2674/2674486.png", width=100)
    
    # Define language FIRST before using it for translations
    language = st.radio("🌐 Language / भाषा", ["English", "Marathi (मराठी)"])
    
    st.title("Settings & Status" if language == "English" else "सेटिंग्ज आणि स्थिती")
    st.markdown("---")

    st.subheader("🖥️ System Status" if language == "English" else "🖥️ प्रणालीची स्थिती")
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
    st.caption("Data Sources: ICAR Contingency Plans, IMD Bulletins, NOAA ONI Index" if language == "English" else "डेटा स्रोत: ICAR आकस्मिक योजना, IMD बुलेटिन, NOAA ONI इंडेक्स")

# Dictionary for translations
t = {
    "config_title": "### 📋 Configure Advisory Parameters" if language == "English" else "### 📋 सल्लागार मापदंड कॉन्फिगर करा",
    "district": "📍 District" if language == "English" else "📍 जिल्हा",
    "crop": "🌱 Crop" if language == "English" else "🌱 पीक",
    "stage": "📅 Sowing Stage" if language == "English" else "📅 पेरणीचा टप्पा",
    "enso": "🌊 El Niño Scenario" if language == "English" else "🌊 एल निनो परिस्थिती",
    "btn": "🚀 Generate Precision Advisory & Accuracy Comparison" if language == "English" else "🚀 अचूक कृषी सल्ला आणि अचूकता तुलना व्युत्पन्न करा",
    "gen_msg": "🔍 Generating: Standard LLM vs. AgriAdvisor RAG..." if language == "English" else "🔍 व्युत्पन्न करत आहे: मानक AI विरुद्ध कृषी-सल्लागार RAG...",
    "success": "✅ Generation & Comparison complete in" if language == "English" else "✅ निर्मिती आणि तुलना पूर्ण झाली वेळ:",
    "target": "**Target:**" if language == "English" else "**लक्ष्य:**",
    "tab1": "🟢 AFTER RAG (AgriAdvisor)" if language == "English" else "🟢 RAG नंतर (AgriAdvisor)",
    "tab2": "🔴 BEFORE RAG (Standard AI)" if language == "English" else "🔴 RAG पूर्वी (मानक AI)",
    "tab3": "🔎 Retrieved Evidence" if language == "English" else "🔎 प्राप्त केलेले पुरावे",
    "tab4": "📊 System Accuracy" if language == "English" else "📊 प्रणाली अचूकता",
    "tab1_h": "#### ✅ Grounded & Parameter-Wise Advisory" if language == "English" else "#### ✅ सविस्तर आणि मापदंडानुसार कृषी सल्ला",
    "tab2_h": "#### ⚠️ Standard LLM (No Knowledge Base)" if language == "English" else "#### ⚠️ मानक AI (कोणताही डेटाबेस नाही)",
    "tab2_w": "Notice how the standard AI lacks specific district data, invents statistics, or misses official ICAR/IMD guidelines without RAG." if language == "English" else "लक्षात घ्या की मानक AI कडे विशिष्ट जिल्ह्याचा डेटा कसा नाही, आकडेवारीचा शोध लावते किंवा RAG शिवाय अधिकृत ICAR/IMD मार्गदर्शक तत्त्वे गमावते.",
    "tab3_h": "#### 📚 Official Source Chunks Used by RAG" if language == "English" else "#### 📚 RAG द्वारे वापरलेले अधिकृत स्रोत",
}

# Dictionary for option translations
district_map = {"Latur": "लातूर", "Beed": "बीड", "Yavatmal": "यवतमाळ", "Amravati": "अमरावती"}
crop_map = {"Cotton": "कापूस", "Soybean": "सोयाबीन", "Tur": "तूर", "Jowar": "ज्वारी"}
stage_map = {"Pre-sowing": "पेरणीपूर्व", "Sowing": "पेरणी", "Vegetative": "वाढीचा टप्पा", "Flowering": "फुलोरा", "Harvest": "काढणी"}
scenario_map = {"Strong": "तीव्र (Strong)", "Moderate": "मध्यम (Moderate)", "Weak": "सौम्य (Weak)", "Neutral": "तटस्थ (Neutral)"}

def translate_opt(val, mapping):
    return mapping.get(val, val) if language == "Marathi (मराठी)" else val

# --- MAIN UI: Query Parameters ---
st.markdown(t["config_title"])
col1, col2, col3, col4 = st.columns(4)

with col1:
    district = st.selectbox(t["district"], ["Latur", "Beed", "Yavatmal", "Amravati"], format_func=lambda x: translate_opt(x, district_map))
with col2:
    crop = st.selectbox(t["crop"], ["Cotton", "Soybean", "Tur", "Jowar"], format_func=lambda x: translate_opt(x, crop_map))
with col3:
    month = st.selectbox(t["stage"], ["Pre-sowing", "Sowing", "Vegetative", "Flowering", "Harvest"], format_func=lambda x: translate_opt(x, stage_map))
with col4:
    scenario = st.selectbox(t["enso"], ["Strong", "Moderate", "Weak", "Neutral"], format_func=lambda x: translate_opt(x, scenario_map))

st.write("")
generate_btn = st.button(t["btn"], use_container_width=True, type="primary")
st.markdown("---")

# Language instruction
lang_instruction = "MARATHI (मराठी). Provide the output exclusively in Marathi script." if "Marathi" in language else "ENGLISH."

# --- STRUCTURED RAG PROMPT ---
if "Marathi" in language:
    rag_template = """तुम्ही एक तज्ज्ञ मुख्य कृषी विस्तार अधिकारी आहात जे शेतकऱ्यांना सल्ला देतात.
तुम्ही तुमचे संपूर्ण उत्तर खालील भाषेत देणे आवश्यक आहे: {lang}

ICAR, IMD आणि NOAA कडील प्रदान केलेल्या संदर्भाचा वापर करून, एक सविस्तर कृषी सल्ला तयार करा.
तुमचे उत्तर काटेकोरपणे खालील ४ विभागांमध्ये असावे:

## 📍 जिल्ह्याचे विश्लेषण: {district}
(ICAR आकस्मिक योजनेत या जिल्ह्याबद्दल काय म्हटले आहे? मातीचा प्रकार, दुष्काळाचा इतिहास, इत्यादी.)

## 🌱 पिकाविषयी मार्गदर्शन: {crop}
(कोणत्या जातीची शिफारस केली आहे? पेरणीची वेळ, बियाण्याचे प्रमाण, खतांची मात्रा काय असावी?)

## 📅 टप्प्यानुसार कृती: {stage}
(या विशिष्ट पीक वाढीच्या टप्प्यावर कोणत्या कृती कराव्यात? सिंचन, पोषक तत्वे, तण नियंत्रण.)

## 🌊 अल निनो (El Niño) प्रभाव: {scenario} अल निनो
(ONI डेटा काय दर्शवतो? {scenario} अल निनोचा महाराष्ट्रातील पावसावर कसा परिणाम होतो? ICAR ने कोणते उपाय सुचवले आहेत?)

जर संदर्भात माहिती नसेल तर स्पष्ट सांगा की माहिती उपलब्ध नाही. खोटी आकडेवारी देऊ नका.

संदर्भ डेटाबेस:
{context}

सविस्तर कृषी सल्ला:
"""
else:
    rag_template = """You are an expert Chief Agricultural Extension Officer advising farmers.
You MUST write the entire response in this language: {lang}

Using the provided context from ICAR, IMD, and NOAA, generate a DETAILED advisory.
Structure your response STRICTLY in the following 4 parameter-wise sections.

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
if "Marathi" in language:
    baseline_template = """तुम्ही एक AI सहाय्यक आहात. खालील कृषी प्रश्नाचे उत्तर द्या.
तुम्ही तुमचे संपूर्ण उत्तर खालील भाषेत देणे आवश्यक आहे: {lang}

तुमचे उत्तर खालील ४ विभागांमध्ये असावे:
## 📍 जिल्ह्याचे विश्लेषण: {district}
## 🌱 पिकाविषयी मार्गदर्शन: {crop}
## 📅 टप्प्यानुसार कृती: {stage}
## 🌊 अल निनो (El Niño) प्रभाव: {scenario} अल निनो

प्रश्न: {scenario} अल निनो परिस्थितीत, {district} जिल्ह्यात {stage} टप्प्यावर {crop} पिकासाठी काय कृषी सल्ला आहे?

उत्तर:
"""
else:
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

    with st.spinner(t["gen_msg"]):
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
            st.success(f"{t['success']} {elapsed_time:.1f}s")
            st.markdown(f"{t['target']} `{district}` | `{crop}` | `{month}` | `{scenario} El Niño`")

            # --- TABS ---
            tab1, tab2, tab3, tab4 = st.tabs([t["tab1"], t["tab2"], t["tab3"], t["tab4"]])

            with tab1:
                st.markdown(t["tab1_h"])
                st.markdown(rag_result)

            with tab2:
                st.markdown(t["tab2_h"])
                st.warning(t["tab2_w"])
                st.markdown(baseline_result)

            with tab3:
                st.markdown(t["tab3_h"])
                for i, doc in enumerate(retrieved_docs):
                    src = doc.metadata.get("source_file", "Unknown")
                    doc_type = doc.metadata.get("doc_type", "")
                    label = f"Source {i+1}: {src}"
                    if doc_type:
                        label += f" [{doc_type}]"
                    with st.expander(label):
                        st.code(doc.page_content, language=None)
                        
            with tab4:
                st.markdown(f"#### 📊 {'Accuracy Metrics (Before vs After RAG)' if language == 'English' else 'अचूकता मेट्रिक्स (RAG पूर्वी वि. नंतर)'}")
                results_file = BASE_DIR / 'evaluation' / 'accuracy_results.json'
                if results_file.exists():
                    with open(results_file, 'r', encoding='utf-8') as f:
                        acc_data = json.load(f)
                    summary = acc_data.get("summary", {})
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Baseline Specific Detail Recall" if language == "English" else "मानक AI तपशील", f"{summary.get('avg_baseline_specific_recall_pct', 0)}%")
                    c2.metric("AgriAdvisor Specific Detail Recall" if language == "English" else "AgriAdvisor अचूक तपशील", f"{summary.get('avg_rag_specific_recall_pct', 0)}%", delta=f"{summary.get('improvement_pct', 0)}%")
                    c3.metric("Hallucinations Prevented" if language == "English" else "प्रतिबंधित खोटे दावे", f"{summary.get('total_baseline_hallucinations', 0) - summary.get('total_rag_hallucinations', 0)}")
                    
                    info_text = "Metrics are calculated dynamically against the real Marathwada Kharif 2023 El Niño drought dataset. 'Specific Detail Recall' measures how often the model correctly states exact ICAR varieties, fertilizer doses, and techniques. 'Hallucinations' measures how often the model invents fake brand names or generic non-regional advice." if language == "English" else "मराठवाडा खरीप २०२३ च्या वास्तविक दुष्काळ डेटासेटवर अचूकता मोजली जाते. मॉडेलने ICAR मधील खऱ्या जाती आणि खते किती अचूक सांगितली हे 'अचूक तपशील' दर्शवते, आणि 'खोटे दावे' (Hallucinations) मॉडेलने स्वतः तयार केलेली खोटी माहिती दर्शवते."
                    st.info(info_text)

                    st.markdown("---")
                    st.markdown(f"#### 🧩 {'Confusion Matrix (Generative RAG Adaptation)' if language == 'English' else 'कन्फ्युजन मॅट्रिक्स (अचूकता तक्ता)'}")
                    
                    cm_rag = summary.get("confusion_matrix_rag", {"TP": 0, "FP": 0, "FN": 0, "TN": 0})
                    cm_baseline = summary.get("confusion_matrix_baseline", {"TP": 0, "FP": 0, "FN": 0, "TN": 0})
                    
                    colA, colB = st.columns(2)
                    with colA:
                        st.markdown("**🟢 AgriAdvisor (With Context)**" if language == "English" else "**🟢 AgriAdvisor (डेटाबेससह)**")
                        st.markdown(f"""
                        <table style="width:100%; text-align:center; border:1px solid white;">
                            <tr>
                                <th></th>
                                <th>{'Relevant (Ground Truth)' if language == 'English' else 'संबंधित (सत्य माहिती)'}</th>
                                <th>{'Irrelevant (Hallucinations)' if language == 'English' else 'असंबंधित (खोटी माहिती)'}</th>
                            </tr>
                            <tr>
                                <th>{'Model Mentions' if language == 'English' else 'मॉडेलने सांगितले'}</th>
                                <td style="background-color:#065F46; color:white;"><b>{'True Positives (TP)' if language == 'English' else 'अचूक (TP)'}</b><br>{cm_rag['TP']}</td>
                                <td style="background-color:#991B1B; color:white;"><b>{'False Positives (FP)' if language == 'English' else 'चुकीचे (FP)'}</b><br>{cm_rag['FP']}</td>
                            </tr>
                            <tr>
                                <th>{'Model Omits' if language == 'English' else 'मॉडेल विसरले'}</th>
                                <td style="background-color:#92400E; color:white;"><b>{'False Negatives (FN)' if language == 'English' else 'गहाळ (FN)'}</b><br>{cm_rag['FN']}</td>
                                <td style="background-color:#1E3A8A; color:white;"><b>{'True Negatives (TN)' if language == 'English' else 'योग्य वगळलेले (TN)'}</b><br>{cm_rag['TN']}</td>
                            </tr>
                        </table>
                        """, unsafe_allow_html=True)
                        
                    with colB:
                        st.markdown("**🔴 Baseline (No Context)**" if language == "English" else "**🔴 मानक AI (डेटाबेसशिवाय)**")
                        st.markdown(f"""
                        <table style="width:100%; text-align:center; border:1px solid white; opacity: 0.7;">
                            <tr>
                                <th></th>
                                <th>{'Relevant (Ground Truth)' if language == 'English' else 'संबंधित (सत्य माहिती)'}</th>
                                <th>{'Irrelevant (Hallucinations)' if language == 'English' else 'असंबंधित (खोटी माहिती)'}</th>
                            </tr>
                            <tr>
                                <th>{'Model Mentions' if language == 'English' else 'मॉडेलने सांगितले'}</th>
                                <td style="background-color:#065F46; color:white;"><b>TP</b><br>{cm_baseline['TP']}</td>
                                <td style="background-color:#991B1B; color:white;"><b>FP</b><br>{cm_baseline['FP']}</td>
                            </tr>
                            <tr>
                                <th>{'Model Omits' if language == 'English' else 'मॉडेल विसरले'}</th>
                                <td style="background-color:#92400E; color:white;"><b>FN</b><br>{cm_baseline['FN']}</td>
                                <td style="background-color:#1E3A8A; color:white;"><b>TN</b><br>{cm_baseline['TN']}</td>
                            </tr>
                        </table>
                        """, unsafe_allow_html=True)

                else:
                    st.info("System evaluation is currently running..." if language == "English" else "प्रणालीचे मूल्यांकन सध्या चालू आहे...")

        except Exception as e:
            st.error(f"An error occurred during generation: {e}")
