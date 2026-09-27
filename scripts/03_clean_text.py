import os
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
EXTRACTED_DIR = BASE_DIR / 'knowledge_base' / 'extracted_text'
CLEANED_DIR = BASE_DIR / 'knowledge_base' / 'cleaned_text'

os.makedirs(CLEANED_DIR / 'ICAR', exist_ok=True)
os.makedirs(CLEANED_DIR / 'IMD', exist_ok=True)
os.makedirs(CLEANED_DIR / 'NOAA', exist_ok=True)

def clean_markdown_text(text):
    """
    Cleans extracted markdown text:
    - Removes page number markers like `--- Page 1 ---`
    - Removes excessive newlines
    - Ensures markdown tables are preserved properly
    """
    # Remove page markers
    text = re.sub(r'--- Page \d+ ---', '', text)
    
    # Normalize newlines (replace 3 or more newlines with 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def process_directory(input_dir, output_dir):
    if not input_dir.exists():
        print(f"Directory not found: {input_dir}")
        return
        
    for md_file in input_dir.glob('*.md'):
        print(f"Cleaning {md_file.name}...")
        with open(md_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
            
        cleaned_text = clean_markdown_text(raw_text)
        
        with open(output_dir / md_file.name, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

def main():
    print("🚀 Starting Milestone 3: Text Cleaning\n")
    
    print("Processing ICAR...")
    process_directory(EXTRACTED_DIR / 'ICAR', CLEANED_DIR / 'ICAR')
    
    print("\nProcessing IMD...")
    process_directory(EXTRACTED_DIR / 'IMD', CLEANED_DIR / 'IMD')

    print("\nProcessing NOAA...")
    process_directory(EXTRACTED_DIR / 'NOAA', CLEANED_DIR / 'NOAA')
    
    print("\n✅ Cleaning complete!")

if __name__ == "__main__":
    main()
