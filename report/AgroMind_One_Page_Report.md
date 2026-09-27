# K. J. Somaiya Institute of Technology
### Department of Artificial Intelligence and Data Science
**Project-Based Learning (PBL) – One Page Project Summary**

**Academic Year:** 2026-27 | **Semester:** III (Odd Sem)

---

### 1. PROJECT DATA
**Project Title:** AgroMind: An El Niño-Aware RAG-Based Agricultural Advisory System for Maharashtra  
**Project Domain:** Artificial Intelligence, Natural Language Processing, Climate Resilience  
**Project Guide:** [Guide Name]  
**Team Members:**  
1. Panth Shah (Roll No: ____)  
2. [Team Member 2 Name] (Roll No: ____)  
3. [Team Member 3 Name] (Roll No: ____)  

---

### 2. EXECUTIVE SUMMARY
AgroMind is an advanced Retrieval-Augmented Generation (RAG) system that processes highly technical government agricultural documents (ICAR contingency plans and IMD weather advisories). By dynamically filtering these documents based on district, crop, and El Niño intensity, it synthesizes instant, reliable, and actionable farming advisories for extension workers, preventing severe crop yield losses in rainfed regions like Marathwada and Vidarbha.

---

### 3. PROBLEM STATEMENT
Critical drought-mitigation guidelines from ICAR and IMD are fragmented across hundreds of PDF pages. Extension workers in Maharashtra lack a unified, rapid-query system to instantly extract localized, crop-specific advice during severe El Niño-driven climate events.

---

### 4. KEY OBJECTIVES
1. **Design a Knowledge Base** integrating static ICAR district contingency plans and dynamic IMD agromet advisories.
2. **Develop a Context-Aware Retrieval Pipeline** that filters guidance based on precise input variables: District, Crop, Month, and El Niño Scenario (Strong/Moderate/Weak).
3. **Generate Traceable Advisories** that enforce a 'Recommendation → Reason → Source' format to prevent LLM hallucinations.
4. **Deploy a Prototype Interface** via Streamlit for agricultural analysts and extension officers.

---

### 5. METHODOLOGY & TECH STACK
**Algorithms/Models:** Retrieval-Augmented Generation (RAG), Llama-3 / Mistral (via Ollama), Nomic-Embed-Text  
**Tools & Frameworks:** Python, LangChain, Streamlit, pdfplumber  
**Dataset Used:** ICAR District Agricultural Contingency Plans (Latur, Beed, Yavatmal, Amravati), IMD Agromet Advisory Bulletins, NOAA ONI Classification  
**Hardware/Environment:** Local machine (Multi-core CPU / Mid-tier GPU), Windows OS  

---

### 6. OUTCOMES & DELIVERABLES
**Achieved:** Successfully extracted complex PDF drought contingency tables into semantic markdown. Developed the core retrieval logic and deployed a fully functional Streamlit dashboard where users input district and climate scenarios to receive verified advice.  
**Working Prototype/Model:** AgroMind Streamlit Dashboard  
**Code Repository:** [Insert GitHub/GitLab Link]  
**Key Findings:** The RAG system significantly outperforms traditional LLMs by completely eliminating hallucinations and successfully citing the exact ICAR PDF page and table for its agronomic recommendations.

---

**Project Guide Name and sign:** ___________________________
