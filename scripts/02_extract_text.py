import os
import sys
import shutil
import pdfplumber
import pandas as pd
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PDF_DIR = BASE_DIR / 'knowledge_base' / 'raw_pdfs'
EXTRACTED_DIR = BASE_DIR / 'knowledge_base' / 'extracted_text'

# Ensure output directories exist
os.makedirs(EXTRACTED_DIR / 'ICAR', exist_ok=True)
os.makedirs(EXTRACTED_DIR / 'IMD', exist_ok=True)
os.makedirs(EXTRACTED_DIR / 'NOAA', exist_ok=True)

def table_to_markdown(table):
    """Converts a pdfplumber table (list of lists) into a Markdown formatted table."""
    if not table or len(table) < 2:
        return ""
    
    clean_table = []
    for row in table:
        clean_row = [str(cell).replace('\n', ' ').strip() if cell is not None else "" for cell in row]
        if any(clean_row):
            clean_table.append(clean_row)
            
    if not clean_table: return ""
    
    df = pd.DataFrame(clean_table[1:], columns=clean_table[0])
    try:
        return df.to_markdown(index=False)
    except Exception as e:
        return f"<!-- Failed to parse table to markdown: {e} -->"

def process_icar_pdf(pdf_path, output_path):
    print(f"Processing ICAR PDF: {pdf_path.name}")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for i, page in enumerate(pdf.pages):
                    out_file.write(f"\n\n--- Page {i+1} ---\n\n")
                    tables = page.extract_tables()
                    if tables:
                        for idx, table in enumerate(tables):
                            out_file.write(f"### Table {idx+1}\n")
                            md_table = table_to_markdown(table)
                            out_file.write(md_table + "\n\n")
                    text = page.extract_text()
                    if text:
                        out_file.write(text + "\n")
        print(f"✅ Saved to {output_path.name}")
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")

def process_imd_pdf(pdf_path, output_path):
    print(f"Processing IMD PDF: {pdf_path.name}")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for i, page in enumerate(pdf.pages):
                    out_file.write(f"\n\n--- Page {i+1} ---\n\n")
                    text = page.extract_text()
                    if text:
                        out_file.write(text + "\n")
        print(f"✅ Saved to {output_path.name}")
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")

def process_oni_txt(txt_path, output_path):
    print(f"Processing ONI TXT: {txt_path.name}")
    try:
        # Simply copy the text file over, renaming it to .md so the pipeline picks it up
        shutil.copy2(txt_path, output_path)
        print(f"✅ Copied ONI to {output_path.name} (Bypassed PDF extraction)")
    except Exception as e:
        print(f"❌ Error processing {txt_path.name}: {e}")

def main():
    print("🚀 Starting Milestone 2: PDF & Data Extraction\n")
    
    # 1. Process ICAR Contingency Plans
    icar_dir = RAW_PDF_DIR / 'ICAR'
    if icar_dir.exists():
        for pdf_file in icar_dir.glob('*.pdf'):
            if 'Kharif_Advisories' in pdf_file.name:
                continue
            out_file = EXTRACTED_DIR / 'ICAR' / f"{pdf_file.stem}.md"
            # Skipping re-extraction of ICAR if it already exists to save time
            if not out_file.exists():
                process_icar_pdf(pdf_file, out_file)
            else:
                print(f"Skipping {pdf_file.name} (already extracted)")
            
    # 2. Process IMD AAS Bulletins
    imd_dir = RAW_PDF_DIR / 'IMD'
    if imd_dir.exists():
        for pdf_file in imd_dir.glob('*.pdf'):
            out_file = EXTRACTED_DIR / 'IMD' / f"{pdf_file.stem}.md"
            if not out_file.exists():
                process_imd_pdf(pdf_file, out_file)
            else:
                print(f"Skipping {pdf_file.name} (already extracted)")

    # 3. Process ONI Knowledge Base (TXT -> MD)
    oni_txt_path = RAW_PDF_DIR / 'NOAA' / 'AgriAdvisor_ONI_KB' / 'oni_v5_knowledge_base.txt'
    if oni_txt_path.exists():
        oni_out_path = EXTRACTED_DIR / 'NOAA' / 'oni_v5.md'
        process_oni_txt(oni_txt_path, oni_out_path)
    else:
        print(f"❌ ONI file not found at {oni_txt_path}")

    print("\n🎉 Extraction complete!")

if __name__ == "__main__":
    main()
