import sys
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'chroma_db'

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def main():
    print("🚀 Loading AgriAdvisor Pipeline for Evaluation...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    vectorstore = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    llm = OllamaLLM(model="llama3.1:8b", temperature=0.3)
    
    rag_prompt = PromptTemplate.from_template(
        "You are an expert agricultural extension worker advising farmers.\n"
        "Using the provided context from ICAR, IMD, and NOAA, provide specific advice.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\nActionable Advisory:"
    )
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )

    test_cases = [
        {"district": "Latur", "crop": "Soybean", "month": "Sowing", "scenario": "Strong"},
        {"district": "Yavatmal", "crop": "Cotton", "month": "Sowing", "scenario": "Moderate"},
        {"district": "Amravati", "crop": "Tur", "month": "Vegetative", "scenario": "Weak"},
    ]

    for case in test_cases:
        query_text = f"What is the agricultural contingency plan and advisory for {case['crop']} in {case['district']} district during the {case['month']} stage under a {case['scenario']} El Niño scenario?"
        
        print(f"\n" + "="*80)
        print(f"=== TEST CASE: {case['crop']} in {case['district']} | {case['month']} | {case['scenario']} El Niño ===")
        print("="*80)
        
        print("\n⏳ 1. Running Baseline LLM (No RAG)...")
        # Naked LLM call without context
        baseline_answer = llm.invoke(f"What agricultural advice would you give for {case['crop']} in {case['district']} during {case['month']} under a {case['scenario']} El Nino year?")
        
        print("\n⏳ 2. Running AgriAdvisor RAG (With ICAR/IMD/NOAA Context)...")
        rag_answer = rag_chain.invoke(query_text)
        
        print("\n" + "-"*40)
        print("🔴 BASELINE ANSWER (Hallucinations possible):")
        print("-" * 40)
        print(baseline_answer)
        
        print("\n" + "-"*40)
        print("🟢 RAG ANSWER (Grounded in Knowledge Base):")
        print("-" * 40)
        print(rag_answer)
        
    print("\n✅ Evaluation complete!")

if __name__ == "__main__":
    main()
