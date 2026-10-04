"""
evaluate.py — AgriAdvisor Historical Accuracy Evaluation
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

def calculate_metrics(response: str, generic_kw: list, specific_kw: list, hallucination_traps: list):
    response_lower = response.lower()
    
    # Generic Recall
    generic_hits = sum(1 for kw in generic_kw if kw.lower() in response_lower)
    generic_recall = generic_hits / len(generic_kw) if generic_kw else 0.0
    
    # Specific Recall (True Positives)
    specific_hits = sum(1 for kw in specific_kw if kw.lower() in response_lower)
    specific_recall = specific_hits / len(specific_kw) if specific_kw else 0.0
    
    # Hallucinations (False Positives)
    hallucination_hits = sum(1 for kw in hallucination_traps if kw.lower() in response_lower)
    
    # RAG Confusion Matrix equivalents
    TP = specific_hits
    FP = hallucination_hits
    FN = len(specific_kw) - specific_hits
    TN = len(hallucination_traps) - hallucination_hits
    
    return {
        "generic_recall": round(generic_recall, 4),
        "specific_recall": round(specific_recall, 4),
        "hallucination_hits": hallucination_hits,
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "TN": TN
    }

def main():
    print("⏳ Loading models & vector database...")
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

    with open(EVAL_DIR / 'historical_validation.json', 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    results = []
    total_baseline_spec = 0.0
    total_rag_spec = 0.0
    total_baseline_hal = 0
    total_rag_hal = 0
    
    # Aggregating confusion matrix
    cm_baseline = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}
    cm_rag = {"TP": 0, "FP": 0, "FN": 0, "TN": 0}

    for tc in test_cases:
        query = f"What is the agricultural contingency plan for {tc['crop']} in {tc['district']} during {tc['stage']} under {tc['scenario']} El Niño?"
        
        print(f"Testing Case {tc['id']}...")
        # Baseline
        baseline_answer = baseline_chain.invoke({"question": query})
        b_metrics = calculate_metrics(baseline_answer, tc['generic_keywords'], tc['specific_keywords'], tc['hallucination_traps'])
        
        # RAG
        retrieved_docs = retriever.invoke(query)
        context_str = format_docs(retrieved_docs)
        rag_answer = rag_chain.invoke({"question": query, "context": context_str})
        r_metrics = calculate_metrics(rag_answer, tc['generic_keywords'], tc['specific_keywords'], tc['hallucination_traps'])

        total_baseline_spec += b_metrics["specific_recall"]
        total_rag_spec += r_metrics["specific_recall"]
        total_baseline_hal += b_metrics["hallucination_hits"]
        total_rag_hal += r_metrics["hallucination_hits"]
        
        for key in cm_baseline:
            cm_baseline[key] += b_metrics[key]
            cm_rag[key] += r_metrics[key]

        results.append({
            "id": tc['id'],
            "district": tc['district'],
            "crop": tc['crop'],
            "baseline_specific_recall": b_metrics["specific_recall"],
            "rag_specific_recall": r_metrics["specific_recall"],
            "baseline_hallucinations": b_metrics["hallucination_hits"],
            "rag_hallucinations": r_metrics["hallucination_hits"]
        })

    n = len(test_cases)
    avg_b_spec = (total_baseline_spec / n) * 100
    avg_r_spec = (total_rag_spec / n) * 100

    report = {
        "summary": {
            "avg_baseline_specific_recall_pct": round(avg_b_spec, 2),
            "avg_rag_specific_recall_pct": round(avg_r_spec, 2),
            "improvement_pct": round(avg_r_spec - avg_b_spec, 2),
            "total_baseline_hallucinations": total_baseline_hal,
            "total_rag_hallucinations": total_rag_hal,
            "confusion_matrix_baseline": cm_baseline,
            "confusion_matrix_rag": cm_rag
        },
        "per_case_results": results
    }
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("✅ Evaluation complete!")

if __name__ == "__main__":
    main()
