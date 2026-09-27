import os
import sys
import json
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_DIR = BASE_DIR / 'knowledge_base' / 'chunks'
DB_DIR = BASE_DIR / 'chroma_db'

def load_chunks():
    documents = []
    chunk_files = list(CHUNKS_DIR.glob('**/*.json'))
    
    for file_path in chunk_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                # Merge metadata fields flatly for Chroma
                meta = {}
                meta['source_file'] = item.get('source_file', '')
                
                # Bring existing metadata
                if 'metadata' in item and isinstance(item['metadata'], dict):
                    for k, v in item['metadata'].items():
                        meta[k] = str(v)
                
                # Bring headers
                if 'headers' in item and isinstance(item['headers'], dict):
                    for k, v in item['headers'].items():
                        meta[k] = str(v)
                
                doc = Document(
                    page_content=item.get('content', ''),
                    metadata=meta
                )
                documents.append(doc)
    return documents

def main():
    print("🚀 Starting Phase 2: Building Vector Database...")
    print(f"Loading chunks from {CHUNKS_DIR}...")
    
    documents = load_chunks()
    print(f"Loaded {len(documents)} chunks.")
    
    if not documents:
        print("❌ No chunks found! Exiting.")
        return

    print("Initializing OllamaEmbeddings (nomic-embed-text:v1.5)...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    
    print(f"Creating Chroma vectorstore at {DB_DIR}... (This may take a few minutes)")
    
    # We create the vectorstore first
    vectorstore = Chroma(
        persist_directory=str(DB_DIR), 
        embedding_function=embeddings
    )
    
    # Batch adding documents
    batch_size = 50
    total_docs = len(documents)
    
    import time
    for i in range(0, total_docs, batch_size):
        batch = documents[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(total_docs//batch_size) + 1} (Chunks {i} to {i+len(batch)})...")
        try:
            vectorstore.add_documents(batch)
            time.sleep(1) # Prevent overloading the local server
        except Exception as e:
            print(f"Error on batch {i}: {e}")
            # we will try to just keep going, or we can wait and retry
            time.sleep(5)
            vectorstore.add_documents(batch)
        
    print("✅ Vector database built successfully!")

if __name__ == "__main__":
    main()
