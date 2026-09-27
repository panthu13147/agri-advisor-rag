import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE_TYPE

# Load the template
ppt_path = r'c:\Users\panth\Documents\projects\PBL complete\AgriAdvisor_Review1 (1).pptx'
prs = Presentation(ppt_path)

def clear_slide(slide):
    """Clears all text boxes and tables from a slide except for backgrounds/images."""
    shapes_to_delete = []
    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.TEXT_BOX or shape.shape_type == MSO_SHAPE_TYPE.TABLE:
            # We want to keep the slide title if it's a specific placeholder, but in this PPT everything is a textbox.
            # So we will just clear the text instead of deleting the shape if it looks like a title.
            pass

def set_title(slide, title_text):
    # Assume the highest text box (lowest top value) is the title
    text_boxes = [s for s in slide.shapes if hasattr(s, 'text') and s.text.strip()]
    if not text_boxes:
        return
    title_box = min(text_boxes, key=lambda s: s.top)
    title_box.text = title_text
    for p in title_box.text_frame.paragraphs:
        p.alignment = PP_ALIGN.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.size = Pt(28)

def clear_all_text(slide):
    for shape in slide.shapes:
        if hasattr(shape, 'text_frame'):
            shape.text_frame.clear()

def add_text_box(slide, text, left, top, width, height, font_size=18, bold=False):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    return txBox

# ----------------- SLIDE 2: CONTENT -----------------
slide2 = prs.slides[1]
clear_all_text(slide2)
set_title(slide2, "CONTENT")
contents = [
    "1. Introduction",
    "2. Literature Survey",
    "3. Objectives",
    "4. Methodology and Architecture",
    "5. Tools, Technologies and Resources",
    "6. Final Outcomes",
    "7. Time Plan",
    "8. References"
]
for i, item in enumerate(contents):
    add_text_box(slide2, item, Inches(1), Inches(1.5 + (i*0.5)), Inches(8), Inches(0.5), font_size=24)

# ----------------- SLIDE 3: INTRODUCTION -----------------
slide3 = prs.slides[2]
clear_all_text(slide3)
set_title(slide3, "INTRODUCTION")
add_text_box(slide3, "Background", Inches(0.5), Inches(1.2), Inches(9), Inches(0.5), font_size=20, bold=True)
add_text_box(slide3, "Domain: Agricultural Advisory and Climate Resilience.\nContext: Rainfed regions (Marathwada/Vidarbha) face severe crop losses during El Niño years. Existing guidelines are fragmented across ICAR and IMD portals.\nObjective: Leverage a local knowledge base to synthesize technical contingency plans into real-time, actionable advisories.", Inches(0.5), Inches(1.6), Inches(9), Inches(1.5), font_size=16)

add_text_box(slide3, "Problem Statement", Inches(0.5), Inches(3.2), Inches(9), Inches(0.5), font_size=20, bold=True)
add_text_box(slide3, "The Crisis: Delayed sowing and flash droughts ruin crop yields, but actionable advice reaches farmers too late or is too generic.\nCurrent System Flaws:\n - Traditional Portals: Require manual searching through 100-page PDFs.\n - Generic AI: Hallucinates farming advice and lacks authoritative grounding.", Inches(0.5), Inches(3.6), Inches(9), Inches(1.5), font_size=16)

add_text_box(slide3, "Motivation", Inches(0.5), Inches(5.2), Inches(9), Inches(0.5), font_size=20, bold=True)
add_text_box(slide3, "Urgency: El Niño events are intensifying. KVK officers need an automated way to query reliable ICAR/IMD rules instantly.\nImpact: A localized, open-source RAG system that translates complex agricultural science into immediate, crop-saving actions.", Inches(0.5), Inches(5.6), Inches(9), Inches(1.0), font_size=16)

# ----------------- SLIDE 4: OBJECTIVES -----------------
slide4 = prs.slides[3]
clear_all_text(slide4)
set_title(slide4, "OBJECTIVES")
add_text_box(slide4, "Primary Objective", Inches(0.5), Inches(1.5), Inches(9), Inches(0.5), font_size=22, bold=True)
add_text_box(slide4, "To design and implement a Retrieval-Augmented Generation (RAG) system that synthesizes verified agricultural guidance into localized, explainable advisories for KVK officers during El Niño years.", Inches(0.5), Inches(2.0), Inches(9), Inches(1.0), font_size=18)

add_text_box(slide4, "Specific Goals", Inches(0.5), Inches(3.5), Inches(9), Inches(0.5), font_size=22, bold=True)
add_text_box(slide4, "• To design a Knowledge Base integrating ICAR contingency plans and IMD advisories for 4 districts.\n\n• To implement a retrieval pipeline that dynamically filters guidance based on El Niño scenario intensity (Strong/Moderate/Weak).\n\n• To evaluate the prototype's output by enforcing a traceable 'Recommendation → Reason → Source' format.", Inches(0.5), Inches(4.0), Inches(9), Inches(2.5), font_size=18)


# ----------------- SLIDE 5: LITERATURE SURVEY -----------------
slide5 = prs.slides[4]
clear_all_text(slide5)
set_title(slide5, "LITERATURE SURVEY")

# Create a 7 column table
rows, cols = 4, 7
left, top, width, height = Inches(0.2), Inches(1.2), Inches(9.6), Inches(4.5)
table_shape = slide5.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

headers = ["Author(s) & Year", "Paper Title", "Method/Technique", "Objective", "Limitations", "Key Findings", "Research Gap"]
for col_idx, header in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.text = header
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(12)

data = [
    ["Kulkarni et al. (2016)", "Marathwada Rainfall Analysis", "Statistical anomaly mapping", "Analyze rainfall variability", "Lacks actionable crop mitigation steps", "Significant decrease in August rainfall", "No operational advisory translation"],
    ["Shinde et al. (2022)", "Spatiotemporal variation in drought", "Remote sensing SPI", "Map drought severity in Vidarbha", "Highly technical, historical focus", "40% of Vidarbha is highly drought-prone", "No forward-looking LLM integration"],
    ["Kumar et al. (2006)", "Indian Monsoon Failure during El Niño", "Climate modeling", "Link ENSO to monsoon failure", "Broad national scope", "Central-Pacific warming heavily impacts India", "Lacks district-level precision"]
]

for row_idx, row_data in enumerate(data):
    for col_idx, cell_data in enumerate(row_data):
        cell = table.cell(row_idx+1, col_idx)
        cell.text = cell_data
        cell.text_frame.paragraphs[0].font.size = Pt(11)

# ----------------- SLIDE 6: METHODOLOGY AND ARCHITECTURE -----------------
slide6 = prs.slides[5]
clear_all_text(slide6)
set_title(slide6, "METHODOLOGY AND ARCHITECTURE")

add_text_box(slide6, "Goal: Develop a highly localized RAG-based advisory system for drought contingency.", Inches(0.5), Inches(1.2), Inches(9), Inches(0.5), font_size=18, bold=True)
add_text_box(slide6, "Approach:", Inches(0.5), Inches(2.0), Inches(9), Inches(0.5), font_size=18, bold=True)

text = """• Ingestion: Processes ICAR District Contingency Plans and IMD Agromet Advisories into raw markdown.
• Preprocessing: Cleans PDF artifacts and semantically chunks tables (e.g., Drought Contingency Tables) so rows/columns remain intact.
• Embedding & Vector DB: Uses open-source embedding models to store chunks in ChromaDB with metadata (District, Crop).
• Retrieval: Filters context dynamically based on user input (District = Latur, Crop = Soybean, Scenario = El Niño).
• Generation (LLM): Synthesizes retrieved chunks into a structured 'Recommendation -> Reason -> Source' output using Ollama."""
add_text_box(slide6, text, Inches(0.5), Inches(2.5), Inches(9), Inches(3.5), font_size=16)

# ----------------- SLIDE 7: TOOLS, TECHNOLOGIES AND RESOURCES -----------------
slide7 = prs.slides[6]
clear_all_text(slide7)
set_title(slide7, "TOOLS, TECHNOLOGIES AND RESOURCES")

add_text_box(slide7, "Hardware Requirements", Inches(0.5), Inches(1.5), Inches(9), Inches(0.5), font_size=18, bold=True)
add_text_box(slide7, "• Processor: Multi-core CPU (or local GPU) for running lightweight LLMs (Ollama).\n• Memory: 8GB–16GB RAM for vector database operations.", Inches(0.5), Inches(1.9), Inches(9), Inches(1.0), font_size=16)

add_text_box(slide7, "Software & Tech Stack", Inches(0.5), Inches(3.2), Inches(9), Inches(0.5), font_size=18, bold=True)
add_text_box(slide7, "• Language: Python\n• Libraries: pdfplumber, LangChain, Pandas\n• Database: ChromaDB (Vector Store)\n• Models: Llama 3 / Mistral (via Ollama) for generation, nomic-embed-text for embeddings.", Inches(0.5), Inches(3.6), Inches(9), Inches(1.5), font_size=16)

add_text_box(slide7, "Datasets", Inches(0.5), Inches(5.3), Inches(9), Inches(0.5), font_size=18, bold=True)
add_text_box(slide7, "• ICAR District Contingency Plans (Latur, Beed, Yavatmal, Amravati)\n• IMD Agromet Advisory Bulletins (AAS)\n• NOAA Oceanic Niño Index (ONI) Reference.", Inches(0.5), Inches(5.7), Inches(9), Inches(1.0), font_size=16)


# ----------------- SLIDE 8: FINAL OUTCOMES -----------------
slide8 = prs.slides[7]
clear_all_text(slide8)
set_title(slide8, "FINAL OUTCOMES")

outcomes = """• Application Architecture: A web-based Streamlit dashboard allowing users to select District, Crop, and Climate Scenario.
• Core Functionality: A decision support system tailored for KVK extension workers.
• Retrieval Accuracy: High-precision semantic search ensuring only relevant ICAR rules are fetched.
• Hallucination Defense: The system refuses to answer out-of-domain questions and cites exact PDF sources for every claim.
• Traceability: 'Recommendation -> Reason -> Source' structure for government-ready reporting."""
add_text_box(slide8, outcomes, Inches(0.5), Inches(2.0), Inches(9), Inches(4.0), font_size=18)

# ----------------- SLIDE 9: TIME PLAN -----------------
slide9 = prs.slides[8]
clear_all_text(slide9)
set_title(slide9, "TIME PLAN")

rows, cols = 7, 7
left, top, width, height = Inches(0.5), Inches(1.5), Inches(9), Inches(3.5)
table_shape = slide9.shapes.add_table(rows, cols, left, top, width, height)
table = table_shape.table

headers = ["Activity", "W1-W2", "W3-W4", "W5-W6", "W7-W8", "W9-W10", "W11-W14"]
for col_idx, header in enumerate(headers):
    table.cell(0, col_idx).text = header
    table.cell(0, col_idx).text_frame.paragraphs[0].font.bold = True
    table.cell(0, col_idx).text_frame.paragraphs[0].font.size = Pt(12)

activities = [
    "Literature Survey & Approval",
    "Data Collection (ICAR/IMD)",
    "Extraction & Cleaning",
    "Vector DB & Embeddings",
    "LLM Integration & RAG",
    "Testing & Final Report"
]
for i, activity in enumerate(activities):
    table.cell(i+1, 0).text = activity
    table.cell(i+1, 0).text_frame.paragraphs[0].font.size = Pt(12)

# Mark Gantt cells with an 'X'
table.cell(1, 1).text = "████"
table.cell(2, 2).text = "████"
table.cell(3, 3).text = "████"
table.cell(4, 4).text = "████"
table.cell(5, 5).text = "████"
table.cell(6, 6).text = "████"

# ----------------- SLIDE 10: REFERENCES -----------------
slide10 = prs.slides[9]
clear_all_text(slide10)
set_title(slide10, "REFERENCES")

refs = """[1] ICAR-CRIDA, "District Agriculture Contingency Plan for Latur, Maharashtra," 2011.
[2] NOAA Climate Prediction Center, "Oceanic Niño Index (ONI)," 2024.
[3] IMD, "Agromet Advisory Services (AAS) Bulletins," 2024.
[4] Kulkarni et al., "Marathwada Rainfall Analysis," Current Science, 2016.
[5] Shinde et al., "Spatiotemporal variation in drought characteristics over Vidarbha," 2022."""
add_text_box(slide10, refs, Inches(0.5), Inches(2.0), Inches(9), Inches(4.0), font_size=16)

# ----------------- SLIDE 11: THANK YOU -----------------
slide11 = prs.slides[10]
clear_all_text(slide11)
add_text_box(slide11, "Thank You", Inches(3.0), Inches(3.0), Inches(4.0), Inches(1.0), font_size=44, bold=True)
add_text_box(slide11, "We are now open to questions and feedback from the committee.", Inches(2.0), Inches(4.0), Inches(6.0), Inches(1.0), font_size=18)


# Save the new presentation
output_path = r'c:\Users\panth\Documents\projects\PBL complete\AgroMind_Final_Presentation.pptx'
prs.save(output_path)
print(f"Successfully generated {output_path}")
