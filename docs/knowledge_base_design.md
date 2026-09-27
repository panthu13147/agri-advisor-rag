# Knowledge Base Design & Data Schema

This document details the knowledge representation, document anatomy, and metadata tagging rules for the AgroMind Knowledge Base.

---

## 📋 Document Anatomy Analysis (ICAR Contingency PDFs)

ICAR District Contingency Plans contain structured tabular data and contextual prose:

1. **Header Metadata**: State, Agro-Climatic Zone, District Name, Average Annual Rainfall, Soil Types.
2. **Rainfed Cropping Contingencies (Section 2.1)**:
   - Delay by 2 weeks (Late June / Early July)
   - Delay by 4 weeks (July mid/end)
   - Delay by 6-8 weeks (August onset)
3. **Agronomic Measures**: Crop/Cropping system substitution, sowing density adjustments, inter-cropping choices, soil moisture conservation, fertilizer management.
4. **Mid-Season Drought / Dry Spells (Section 2.2)**:
   - Early stage (Vegetative)
   - Mid stage (Flowering)
   - Late stage (Fruiting/Maturity)

---

## 🏷️ Metadata Schema (`chunks/*.json`)

Every chunk stored in the Knowledge Base is bound to the following JSON metadata structure:

```json
{
  "chunk_id": "ICAR_BEED_0042",
  "source_file": "ICAR_Contingency_100_Districts_Peninsular_India.pdf",
  "authority": "ICAR-CRIDA",
  "state": "Maharashtra",
  "region": "Marathwada",
  "district": "Beed",
  "soil_type": "Medium Deep Black Soil",
  "crop": "Cotton",
  "season": "Kharif",
  "contingency_type": "Delayed Sowing (2-4 Weeks)",
  "section": "2.1.1 Rainfed Situation",
  "text": "For delayed sowing by 2-4 weeks (July 1st week), substitute long-duration cotton varieties with short-duration hybrids or intercrop with Pigeonpea (6:1 ratio)..."
}
```
