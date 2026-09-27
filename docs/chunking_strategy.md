# Chunking Strategy & Segmentation Rules

This document outlines the chunking strategies evaluated and selected for parsing agricultural contingency documents and weather advisories.

---

## 🎯 Chunking Strategy Breakdown

| Strategy Type | Target Content | Chunk Size (Tokens/Chars) | Overlap | Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Table-Aware Section Chunking** | ICAR Contingency Tables (Sec 2.1 - 2.3) | ~500 - 800 chars | 100 chars | Preserves complete condition ──► crop advice ──► agronomic measure rows without splitting advice mid-table. |
| **Semantic Paragraph Chunking** | District Profiles & Climate Background | ~300 - 500 chars | 50 chars | Captures complete background narratives regarding soil depth, rainfall patterns, and irrigation infrastructure. |
| **Bullet-Level Advisory Chunking** | IMD Weekly Agromet Bulletins | ~200 - 400 chars | 0 chars | Weekly crop alerts are self-contained bullet points (e.g. "Cotton: Postpone irrigation due to forecasted heavy rainfall"). |

---

## 🛑 Anti-Patterns Avoided

1. **Blind Character-Count Chunking**: Splitting chunks strictly every 500 characters breaks table rows, severing a crop recommendation from its corresponding delay condition.
2. **Loss of Table Headers**: Ingesting table cells without header context (e.g. associating "Pigeonpea 6:1" with "Delayed Sowing by 4 Weeks") renders vector search ineffective.
