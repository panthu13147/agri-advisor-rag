"""
evaluate.py — AgriAdvisor Historical Accuracy Evaluation
Uses REAL Kharif 2023 El Niño drought data from Marathwada to validate:
  Before RAG (baseline LLM) vs After RAG (AgriAdvisor)
Metrics: Keyword Recall, Source Accuracy, Validation Criteria Score
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
    response_lower = response.lower()
    hits = sum(1 for kw in keywords if kw.lower() in response_lower)
    return round(hits / len(keywords), 4) if keywords else 0.0

def criteria_score(response: str, criteria: list) -> dict:
    """Check how many validation criteria the response satisfies."""
    response_lower = response.lower()
    results = {}
    for criterion in criteria:
        # Extract key terms from the criterion question
        key_terms = [w.lower() for w in criterion.replace("?", "").split() 
                     if len(w) > 3 and w.lower() not in {"did", "does", "the", "about", "under", "with", "from", "that", "this", "for", "was", "were"}]
        # Score: what fraction of key terms appear
        if key_terms:
            hits = sum(1 for t in key_terms if t in response_lower)
            score = hits / len(key_terms)
        else:
            score = 0.0
        results[criterion] = round(score, 2)
    return results

def source_hit(retrieved_docs: list, expected_keywords: list) -> bool:
    for doc in retrieved_docs:
        src = doc.metadata.get('source_file', '').lower()
        for kw in expected_keywords[:3]:
            if kw.lower() in src:
                return True
    return False

def main():
    print("=" * 90)
    print("  AgriAdvisor — Historical Accuracy Evaluation")
    print("  Dataset: REAL Kharif 2023 Marathwada El Niño Drought Outcomes")
    print("=" * 90)

    # Load
    print("\n⏳ Loading models & vector database...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text:v1.5")
    vectorstore = Chroma(persist_directory=str(DB_DIR), embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = OllamaLLM(model="llama3.1:8b", temperature=0.3)

    rag_prompt = PromptTemplate.from_template(
        "You are an expert agricultural extension officer. Using the provided ICAR/IMD/NOAA context, "
        "provide a detailed, structured advisory broken into: District Analysis, Crop Guidance, "
        "Stage-Specific Actions, and El Niño Impact Assessment.\n\n"
        "Context:\n{context}\n\nQuestion: {question}\n\nDetailed Advisory:"
    )
    baseline_prompt = PromptTemplate.from_template(
        "You are an AI assistant. Answer the following agricultural question with detailed guidance.\n\n"
        "Question: {question}\n\nDetailed Answer:"
    )
    rag_chain = rag_prompt | llm | StrOutputParser()
    baseline_chain = baseline_prompt | llm | StrOutputParser()

    # Load historical validation data
    with open(EVAL_DIR / 'historical_validation.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    print(f"📋 Loaded {len(test_cases)} historical validation cases.\n")

    results = []
    total_baseline_recall = 0.0
    total_rag_recall = 0.0
    total_baseline_criteria = 0.0
    total_rag_criteria = 0.0
    total_source_hits = 0

    for tc in test_cases:
        tc_id = tc['id']
        query = f"What is the agricultural contingency plan for {tc['crop']} in {tc['district']} during {tc['stage']} under {tc['scenario']} El Niño?"
        expected_kw = tc['expected_keywords']
        criteria = tc['validation_criteria']

        print(f"\n{'━' * 90}")
        print(f"  CASE {tc_id}: {tc['year']} | {tc['district']} | {tc['crop']} | {tc['stage']} | {tc['scenario']} El Niño")
        print(f"  ONI: {tc['oni_value']}")
        print(f"  ACTUAL OUTCOME: {tc['actual_outcome'][:120]}...")
        print(f"{'━' * 90}")

        # 1. Baseline
        print("  ⏳ Running Baseline LLM (no knowledge base)...")
        t0 = time.time()
        baseline_answer = baseline_chain.invoke({"question": query})
        baseline_time = time.time() - t0
        baseline_recall = keyword_recall(baseline_answer, expected_kw)
        baseline_crit = criteria_score(baseline_answer, criteria)
        baseline_crit_avg = round(sum(baseline_crit.values()) / len(baseline_crit), 4) if baseline_crit else 0

        # 2. RAG
        print("  ⏳ Running AgriAdvisor RAG (with ICAR/IMD/NOAA)...")
        t0 = time.time()
        retrieved_docs = retriever.invoke(query)
        context_str = format_docs(retrieved_docs)
        rag_answer = rag_chain.invoke({"question": query, "context": context_str})
        rag_time = time.time() - t0
        rag_recall = keyword_recall(rag_answer, expected_kw)
        rag_crit = criteria_score(rag_answer, criteria)
        rag_crit_avg = round(sum(rag_crit.values()) / len(rag_crit), 4) if rag_crit else 0
        src_hit = source_hit(retrieved_docs, [tc['district']])

        # Print
        print(f"\n  {'Metric':<35} {'🔴 Baseline':>15} {'🟢 RAG':>15}")
        print(f"  {'─'*35} {'─'*15} {'─'*15}")
        print(f"  {'Keyword Recall':<35} {baseline_recall*100:>13.1f}% {rag_recall*100:>13.1f}%")
        print(f"  {'Criteria Score':<35} {baseline_crit_avg*100:>13.1f}% {rag_crit_avg*100:>13.1f}%")
        print(f"  {'Source Retrieved':<35} {'N/A':>15} {'✅' if src_hit else '❌':>15}")
        print(f"  {'Response Time':<35} {baseline_time:>13.1f}s {rag_time:>13.1f}s")

        improvement_recall = (rag_recall - baseline_recall) * 100
        improvement_crit = (rag_crit_avg - baseline_crit_avg) * 100
        print(f"\n  📈 Keyword Recall Improvement: {'+' if improvement_recall >= 0 else ''}{improvement_recall:.1f}%")
        print(f"  📈 Criteria Score Improvement: {'+' if improvement_crit >= 0 else ''}{improvement_crit:.1f}%")

        total_baseline_recall += baseline_recall
        total_rag_recall += rag_recall
        total_baseline_criteria += baseline_crit_avg
        total_rag_criteria += rag_crit_avg
        total_source_hits += int(src_hit)

        results.append({
            "id": tc_id,
            "year": tc["year"],
            "district": tc["district"],
            "crop": tc["crop"],
            "stage": tc["stage"],
            "scenario": tc["scenario"],
            "baseline_keyword_recall": baseline_recall,
            "rag_keyword_recall": rag_recall,
            "baseline_criteria_score": baseline_crit_avg,
            "rag_criteria_score": rag_crit_avg,
            "keyword_improvement": round(improvement_recall, 2),
            "criteria_improvement": round(improvement_crit, 2),
            "source_hit": src_hit,
            "baseline_time_s": round(baseline_time, 2),
            "rag_time_s": round(rag_time, 2),
            "validation_criteria_detail": {
                "baseline": baseline_crit,
                "rag": rag_crit
            }
        })

    # === FINAL SUMMARY ===
    n = len(test_cases)
    avg_b_recall = (total_baseline_recall / n) * 100
    avg_r_recall = (total_rag_recall / n) * 100
    avg_b_crit = (total_baseline_criteria / n) * 100
    avg_r_crit = (total_rag_criteria / n) * 100
    src_acc = (total_source_hits / n) * 100

    print("\n" + "=" * 90)
    print("  📊 FINAL ACCURACY REPORT — Before RAG vs After RAG")
    print("  Dataset: Real Kharif 2023 Marathwada El Niño Drought")
    print("=" * 90)
    print(f"""
  ┌─────────────────────────────────┬───────────────┬───────────────┐
  │ Metric                          │  🔴 Before RAG │  🟢 After RAG  │
  ├─────────────────────────────────┼───────────────┼───────────────┤
  │ Avg Keyword Recall              │ {avg_b_recall:>11.1f}%  │ {avg_r_recall:>11.1f}%  │
  │ Avg Criteria Score              │ {avg_b_crit:>11.1f}%  │ {avg_r_crit:>11.1f}%  │
  │ Retrieval Source Accuracy       │     N/A       │ {src_acc:>11.1f}%  │
  │ Keyword Recall Improvement      │               │ +{avg_r_recall - avg_b_recall:>10.1f}%  │
  │ Criteria Score Improvement      │               │ +{avg_r_crit - avg_b_crit:>10.1f}%  │
  └─────────────────────────────────┴───────────────┴───────────────┘
    """)

    # Save
    report = {
        "evaluation_info": {
            "dataset": "Historical Validation — Kharif 2023 Marathwada El Niño Drought",
            "total_test_cases": n,
            "embedding_model": "nomic-embed-text:v1.5",
            "llm_model": "llama3.1:8b",
            "vector_db_chunks": 3556,
        },
        "summary": {
            "avg_baseline_keyword_recall_pct": round(avg_b_recall, 2),
            "avg_rag_keyword_recall_pct": round(avg_r_recall, 2),
            "keyword_recall_improvement_pct": round(avg_r_recall - avg_b_recall, 2),
            "avg_baseline_criteria_score_pct": round(avg_b_crit, 2),
            "avg_rag_criteria_score_pct": round(avg_r_crit, 2),
            "criteria_score_improvement_pct": round(avg_r_crit - avg_b_crit, 2),
            "retrieval_source_accuracy_pct": round(src_acc, 2),
        },
        "per_case_results": results
    }
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  📄 Full results saved to: {RESULTS_FILE}")
    print("  ✅ Evaluation complete!\n")

if __name__ == "__main__":
    main()
