import os
import sys
import json
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / 'knowledge_base' / 'cleaned_text'
CHUNKS_DIR = BASE_DIR / 'knowledge_base' / 'chunks'

os.makedirs(CHUNKS_DIR / 'ICAR', exist_ok=True)
os.makedirs(CHUNKS_DIR / 'IMD', exist_ok=True)
os.makedirs(CHUNKS_DIR / 'NOAA', exist_ok=True)

def chunk_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        markdown_document = f.read()
        
    headers_to_split_on = [
        ("###", "Header 3"),
        ("##", "Header 2"),
        ("#", "Header 1"),
    ]
    
    # 1. Split by Markdown headers (preserves semantic sections and tables)
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    md_header_splits = markdown_splitter.split_text(markdown_document)
    
    # 2. Split long sections recursively, but try to keep tables intact
    chunk_size = 1200
    chunk_overlap = 200
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    
    final_chunks = text_splitter.split_documents(md_header_splits)
    
    # Format chunks into a clean list of dicts
    chunks_data = []
    for chunk in final_chunks:
        if not chunk.page_content.strip():
            continue
        chunks_data.append({
            "content": chunk.page_content,
            "headers": chunk.metadata,
            "metadata": {}, # Handled in metadata phase or later if ICAR/IMD
            "source_file": file_path.name
        })
        
    return chunks_data

def chunk_oni(file_path):
    """Custom chunking for ONI TXT to preserve exactly one season per chunk with metadata."""
    chunks_data = []
    
    # Required strict metadata for all ONI records
    oni_metadata = {
        "doc_type": "oni",
        "source": "NOAA Climate Prediction Center",
        "dataset": "Oceanic Niño Index (ONI) v5",
        "region": "Niño 3.4",
        "unit": "°C"
    }

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Find where Records: starts
    records_started = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line == "Records:":
            records_started = True
            continue
            
        if records_started and line.startswith("Year:"):
            # This is a single record chunk
            chunks_data.append({
                "content": line,
                "headers": {},
                "metadata": oni_metadata,
                "source_file": file_path.name
            })
            
    return chunks_data

def process_directory(input_dir, output_dir):
    if not input_dir.exists():
        return
        
    for md_file in input_dir.glob('*.md'):
        print(f"Chunking {md_file.name}...")
        
        if input_dir.name == "NOAA":
            chunks_data = chunk_oni(md_file)
        else:
            chunks_data = chunk_markdown(md_file)
        
        out_file = output_dir / f"{md_file.stem}_chunks.json"
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, indent=4, ensure_ascii=False)
            
        print(f"  -> Generated {len(chunks_data)} chunks.")

def main():
    print("🚀 Starting Milestone 4: Semantic Chunking\n")
    
    process_directory(CLEANED_DIR / 'ICAR', CHUNKS_DIR / 'ICAR')
    process_directory(CLEANED_DIR / 'IMD', CHUNKS_DIR / 'IMD')
    process_directory(CLEANED_DIR / 'NOAA', CHUNKS_DIR / 'NOAA')
    
    print("\n✅ Chunking complete!")

if __name__ == "__main__":
    main()
