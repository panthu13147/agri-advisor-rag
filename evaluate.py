"""
evaluate.py — AgriAdvisor Accuracy Evaluation
Compares Before RAG (Baseline LLM) vs After RAG (AgriAdvisor)
Measures: Keyword Recall, Source Accuracy, and Contextual Grounding
"""

import sys
import json
import time
from pathlib import Path
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / 'chroma_db'
EVAL_DIR = BASE_DIR / 'evaluation'
RESULTS_FILE = EVAL_DIR / 'accuracy_results.json'

def format_docs(docs):
    return "\n\n---\n\n".join(doc.page_content for doc in docs)

def keyword_recall(response: str, keywords: list) -> float:
    """What fraction of expected keywords appear in the response."""
    response_lower = response.lower()
    hits = sum(1 for kw in keywords if kw.lower() in response_lower)
    return round(hits / len(keywords), 4) if keywords else 0.0

def source_hit(retrieved_docs: list, expected_source: str) -> bool:
    """Did the retriever pull back the expected source file?"""
    for doc in retrieved_docs:
        if expected_source in doc.metadata.get('source_file', ''):
            return True
    return False

def main():
    print("=" * 80)
    print("  AgriAdvisor — Accuracy Evaluation: Before RAG vs After RAG")
    print("=" * 80)

    # Load components
    print("\n⏳ Loading models & database...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    vectorstore = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = OllamaLLM(model="llama3.1:8b", temperature=0.3)

    # Prompts
    rag_prompt = PromptTemplate.from_template(
        "You are an expert agricultural extension officer. Using the provided ICAR/IMD/NOAA context, "
        "provide a detailed advisory.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAdvisory:"
    )
    baseline_prompt = PromptTemplate.from_template(
        "You are an AI assistant. Answer the following agricultural question.\n\n"
        "Question: {question}\n\nAnswer:"
    )

    rag_chain = rag_prompt | llm | StrOutputParser()
    baseline_chain = baseline_prompt | llm | StrOutputParser()

    # Load test data
    with open(EVAL_DIR / 'test_dataset.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    print(f"📋 Loaded {len(test_cases)} test cases.\n")

    results = []
    total_baseline_recall = 0.0
    total_rag_recall = 0.0
    total_source_hits = 0

    for tc in test_cases:
        tc_id = tc['id']
        query = tc['query']
        expected_kw = tc['expected_keywords']
        expected_src = tc['expected_source']

        print(f"\n{'─' * 70}")
        print(f"  Test Case {tc_id}: {tc['district']} | {tc['crop']} | {tc['stage']} | {tc['scenario']} El Niño")
        print(f"{'─' * 70}")

        # 1. Baseline (No RAG)
        print("  ⏳ Running Baseline LLM (no context)...")
        t0 = time.time()
        baseline_answer = baseline_chain.invoke({"question": query})
        baseline_time = time.time() - t0
        baseline_recall = keyword_recall(baseline_answer, expected_kw)

        # 2. RAG
        print("  ⏳ Running AgriAdvisor RAG...")
        t0 = time.time()
        retrieved_docs = retriever.invoke(query)
        context_str = format_docs(retrieved_docs)
        rag_answer = rag_chain.invoke({"question": query, "context": context_str})
        rag_time = time.time() - t0
        rag_recall = keyword_recall(rag_answer, expected_kw)
        src_hit = source_hit(retrieved_docs, expected_src)

        # Print comparison
        print(f"\n  🔴 BASELINE — Keyword Recall: {baseline_recall*100:.1f}%  |  Time: {baseline_time:.1f}s")
        print(f"  🟢 RAG      — Keyword Recall: {rag_recall*100:.1f}%  |  Time: {rag_time:.1f}s  |  Source Hit: {'✅' if src_hit else '❌'}")
        improvement = (rag_recall - baseline_recall) * 100
        print(f"  📈 Improvement: {'+' if improvement >= 0 else ''}{improvement:.1f}%")

        total_baseline_recall += baseline_recall
        total_rag_recall += rag_recall
        total_source_hits += int(src_hit)

        results.append({
            "id": tc_id,
            "district": tc['district'],
            "crop": tc['crop'],
            "stage": tc['stage'],
            "scenario": tc['scenario'],
            "baseline_keyword_recall": baseline_recall,
            "rag_keyword_recall": rag_recall,
            "improvement": round(improvement, 2),
            "source_hit": src_hit,
            "baseline_time_s": round(baseline_time, 2),
            "rag_time_s": round(rag_time, 2),
        })

    # --- SUMMARY ---
    n = len(test_cases)
    avg_baseline = (total_baseline_recall / n) * 100
    avg_rag = (total_rag_recall / n) * 100
    src_accuracy = (total_source_hits / n) * 100

    print("\n" + "=" * 80)
    print("  FINAL ACCURACY REPORT")
    print("=" * 80)
    print(f"""
  ┌───────────────────────────────┬──────────────┬──────────────┐
  │ Metric                        │ Before RAG   │ After RAG    │
  ├───────────────────────────────┼──────────────┼──────────────┤
  │ Avg Keyword Recall            │ {avg_baseline:>10.1f}%  │ {avg_rag:>10.1f}%  │
  │ Retrieval Source Accuracy     │     N/A      │ {src_accuracy:>10.1f}%  │
  │ Overall Improvement           │              │ +{avg_rag - avg_baseline:>9.1f}%  │
  └───────────────────────────────┴──────────────┴──────────────┘
    """)

    # Save results
    report = {
        "summary": {
            "total_test_cases": n,
            "avg_baseline_keyword_recall_pct": round(avg_baseline, 2),
            "avg_rag_keyword_recall_pct": round(avg_rag, 2),
            "avg_improvement_pct": round(avg_rag - avg_baseline, 2),
            "retrieval_source_accuracy_pct": round(src_accuracy, 2),
        },
        "per_case_results": results
    }
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  📄 Detailed results saved to: {RESULTS_FILE}")
    print("  ✅ Evaluation complete!\n")

if __name__ == "__main__":
    main()
