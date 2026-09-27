# Data Acquisition Plan - AgroMind RAG

This document formalizes the data sourcing strategy for the AgroMind Agricultural RAG project, separating static agronomic baseline rules from dynamic weather advisories and defining ingestion pipelines for each data format.

---

## 📊 Source Matrix & RAG Priority

| Source Category | Authority | Static / Dynamic | Source Format | Contains Recommendations? | Use in RAG Knowledge Base? | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ICAR Contingency District Plan** | ICAR-CRIDA | **Static** | PDF | ✅ **Yes** (Drought/Delay crop tables) | ✅ **HIGH (Core)** | Baseline agronomic contingency rules, crop alternatives, soil & rainfall suitability. |
| **IMD Agromet Advisory (AAS)** | IMD / AICRPAM | **Dynamic** | HTML / PDF | ✅ **Yes** (Weekly crop-specific advisories) | ✅ **HIGH (Contextual)** | Live weekly crop management, pest alerts, chemical/irrigation guidance based on current weather. |
| **IMD Weather Forecast (ERFS / Daily)** | IMD | **Dynamic** | HTML / Web App | ❌ **No** (Raw numeric weather data) | ⚠️ **SUPPORTING** | Current/forecast temperature, rainfall, humidity fed as prompt context or query filter. |
| **KVK District Advisories** | Krishi Vigyan Kendra | **Dynamic** | HTML / PDF | ✅ **Yes** (Hyperlocal farm advisories) | ✅ **MEDIUM (Optional)** | Localized field-level farming advice. Great if available, but not a blocker. |
| **Research Papers** | Academic / Universities | **Static** | PDF | ❌ **Academic Focus** | ❌ **NO** (Exclude from RAG) | Project report, literature review, problem statement, and presentation citations. |

---

## 🏛️ Static vs Dynamic Knowledge Architecture

```text
                               ┌──────────────────────────────────────────────┐
                               │             AgroMind RAG Engine              │
                               └──────────────────────┬───────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       │                                                             │
                       ▼                                                             ▼
         ┌──────────────────────────┐                                  ┌──────────────────────────┐
         │     Static Knowledge     │                                  │    Dynamic Knowledge     │
         │      (Baseline RAG)      │                                  │   (Contextual RAG/API)   │
         └─────────────┬────────────┘                                  └─────────────┬────────────┘
                       │                                                             │
       ┌───────────────┴───────────────┐                             ┌───────────────┴───────────────┐
       ▼                               ▼                             ▼                               ▼
 ┌───────────┐                   ┌───────────┐                 ┌───────────┐                   ┌───────────┐
 │ICAR District│                 │ICAR Macro │                 │IMD Agromet│                   │IMD Live   │
 │   PDFs    │                 │ 100-Dist  │                 │ Advisories│                   │ Forecast  │
 └───────────┘                   └───────────┘                 └───────────┘                   └───────────┘
```

---

## 🎯 Scope Coverage & Acquisition Target (4 Representative Districts)

### Region 1: Marathwada (VNMKV Parbhani Jurisdiction)
1. **Latur**:
   - `ICAR District Contingency PDF`: ✅ Acquired (`raw_pdfs/ICAR/ICAR_Latur_Contingency.pdf`)
   - `IMD Agromet Advisory (AAS)`: ✅ Acquired (`raw_pdfs/IMD/IMD_AAS_Latur_Current.pdf`)
2. **Beed**:
   - `ICAR District Contingency PDF`: ✅ Acquired (`raw_pdfs/ICAR/ICAR_Beed_Contingency.pdf`)
   - `IMD Agromet Advisory (AAS)`: ✅ Acquired (`raw_pdfs/IMD/IMD_AAS_Beed_Current.pdf`)

### Region 2: Vidarbha (PDKV Akola Jurisdiction)
3. **Yavatmal**:
   - `ICAR District Contingency PDF`: ✅ Acquired (`raw_pdfs/ICAR/ICAR_Yavatmal_Contingency.pdf`)
   - `IMD Agromet Advisory (AAS)`: ✅ Acquired (`raw_pdfs/IMD/IMD_AAS_Yavatmal_Current.pdf`)
4. **Amravati**:
   - `ICAR District Contingency PDF`: ✅ Acquired (`raw_pdfs/ICAR/ICAR_Amravati_Contingency.pdf`)
   - `IMD Agromet Advisory (AAS)`: ✅ Acquired (`raw_pdfs/IMD/IMD_AAS_Amravati_Current.pdf`)

---

## 🛠️ Data Ingestion Strategy

1. **PDF Processing Pipeline (Static Data)**:
   - Tool: `pdfplumber` / `pypdf`
   - Target: ICAR Contingency PDFs
   - Extracted Content: Contingency tables, crop varieties, delayed sowing recommendations, land use, soil profiles.

2. **Web Scraping Pipeline (Dynamic Data)**:
   - Tool: `BeautifulSoup4` / `httpx` / `playwright`
   - Target: IMD Agromet Advisory Bulletins (AAS)
   - Extracted Content: Crop advisory text, weather warnings, weekly farming tips.

---

## ⚖️ The 5-Question Document Evaluation Framework

Before adding any new document to the Knowledge Base, it must be evaluated against these 5 criteria:

| Question | Evaluation Criteria |
| :--- | :--- |
| **1. Is this official?** | Must be from ICAR, IMD, KVK, or Government. |
| **2. Static or Dynamic?** | PDF (Static baseline) or Live Advisory (Dynamic context). |
| **3. Knowledge Base or Report?** | Official guidelines → RAG KB. Academic → Report/Docs. |
| **4. Is it District specific?** | Must map to Latur, Beed, Yavatmal, or Amravati. |
| **5. Does it contain Farmer Recommendations?** | Must contain actionable advice (e.g., "Delay sowing", "Use soybean variety..."). |

**Rule:** If a document scores "YES" on 4 out of 5 questions, it enters the Knowledge Base. Otherwise, it goes to the Archive or Research folder.
