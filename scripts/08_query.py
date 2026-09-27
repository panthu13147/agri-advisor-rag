import os
import sys
import argparse
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / 'chroma_db'

def query_db(query_text, n_results=5):
    print(f"Loading Chroma vectorstore from {DB_DIR}...")
    
    if not DB_DIR.exists():
        print("❌ chroma_db does not exist. Please run 07_build_vector_db.py first.")
        return
        
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    vectorstore = Chroma(
        persist_directory=str(DB_DIR), 
        embedding_function=embeddings
    )
    
    print(f"\n🔍 Query: '{query_text}'")
    print("-" * 50)
    
    results = vectorstore.similarity_search_with_score(query_text, k=n_results)
    
    if not results:
        print("No results found.")
        return
        
    for i, (doc, score) in enumerate(results):
        print(f"\n[{i+1}] Score: {score:.4f}")
        print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
        print("Metadata:")
        for k, v in doc.metadata.items():
            if k != 'source_file':
                print(f"  {k}: {v}")
        print("Content Preview:")
        preview = doc.page_content.replace('\n', ' ')
        if len(preview) > 300:
            preview = preview[:300] + "..."
        print(f"  \"{preview}\"")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the AgriAdvisor Vector Database")
    parser.add_argument("query", type=str, nargs="?", default="What is the contingency plan for Latur during delayed sowing?", help="The query string to search for")
    parser.add_argument("-k", type=int, default=5, help="Number of results to return")
    
    args = parser.parse_args()
    query_db(args.query, args.k)
