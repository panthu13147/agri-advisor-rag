# Literature Review & Research Paper Strategy

This document outlines the strategy for sourcing, evaluating, and selecting academic research papers for the AgroMind RAG project. 

**Core Principle:** Research papers are strictly for the Literature Review, Project Report, Presentation, and Domain Understanding. They do NOT go directly into the Vector DB unless they contain highly specific, actionable agronomic rules.

---

## 1. Primary Sources (Tiered)

| Tier | Source | Purpose |
| :--- | :--- | :--- |
| **Tier 1** | [Google Scholar](https://scholar.google.com) | Primary search engine. Best for broad queries (e.g., "Latur soybean drought"). |
| **Tier 2** | [ResearchGate](https://www.researchgate.net) | Good for finding full PDFs uploaded directly by researchers. |
| **Tier 3** | [Semantic Scholar](https://www.semanticscholar.org) | AI-based search, excellent for filtering duplicates and finding highly cited papers. |
| **Tier 4** | [DOAJ](https://doaj.org) | Open-access journals (guaranteed free PDFs). |
| **Tier 5** | [Crossref](https://www.crossref.org/) | Useful for metadata extraction and citation linking. |

## 2. Agriculture-Specific Institutions (Goldmines)

When searching, prioritize papers and technical bulletins published by:
- **ICAR / NAAS** (National Academy of Agricultural Sciences)
- **CRIDA** (Central Research Institute for Dryland Agriculture) - *Crucial for drought contingency.*
- **ICRISAT** (International Crops Research Institute for the Semi-Arid Tropics) - *World-famous for semi-arid/rainfed crops.*
- **SAUs** (State Agricultural Universities: VNMKV Parbhani, PDKV Akola).

---

## 3. The 3-Phase Selection Pipeline

### Phase 1: Candidate Collection (Target: 50 Papers)
Build a tracking spreadsheet with the following columns:
`Title | Year | Authors | Journal | District | Crop | Drought | Useful? | PDF? | Score`

### Phase 2: Quantitative Scoring (Target: Score out of 10)
Evaluate each of the 50 papers using this scoring matrix:

| Criteria | Score |
| :--- | :--- |
| Relevant District (Latur, Beed, Yavatmal, Amravati) | 2 |
| Relevant Crop (Soybean, Cotton, etc.) | 2 |
| Focus on Drought / Rainfed Agriculture | 2 |
| Contains Actionable Recommendations | 2 |
| Recent Publication (< 5 years) | 2 |
| **Total Maximum Score** | **10** |

### Phase 3: Final Selection (Target: 5-10 Papers)
Select only the top-scoring 5-10 papers for the final literature review and report.

---

## 4. RAG Inclusion Policy (Strict)

If a top-scoring paper is considered for the RAG Knowledge Base, we will **ONLY** extract:
- Actionable recommendations
- Crop recommendations
- Drought strategies
- Pest management protocols
- Scientific recommendations

We will strictly **EXCLUDE**:
- Introductions & Literature reviews
- Complex statistical models & Data tables
- Acknowledgements, Affiliations, Funding details
