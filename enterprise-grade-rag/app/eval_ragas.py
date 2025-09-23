"""
RAGAS quick harness for the toy eval set.
Usage:
  export LANGCHAIN_TRACING_V2=true
  export LANGSMITH_API_KEY=...   # optional
  python -m app.eval_ragas --k 5
"""
import os, json, argparse
from pathlib import Path

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import context_precision, faithfulness

from .pipeline import hybrid_retrieve, compose_answer, citation_check
from .index import load_corpus

EVAL_FILE = Path("data/eval/eval.jsonl")

def build_dataset(k: int):
    rows = [json.loads(l) for l in EVAL_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    all_chunks = load_corpus()
    questions, contexts, ground_truths, answers = [], [], [], []
    for r in rows:
        q = r["question"]; gold_ids = r.get("gold_doc_ids", [])
        cand = hybrid_retrieve(q, top_k=k)
        chosen = [i for i,_ in cand[:min(5, len(cand))]]
        ans, cites = compose_answer(q, chosen)
        cites = citation_check(cites)
        ctx = [c["quote"] for c in cites]
        gt_texts = [d["text"] for d in all_chunks if d["doc_id"] in gold_ids]
        gt = "\\n".join(gt_texts)
        questions.append(q); contexts.append(ctx); ground_truths.append(gt); answers.append(ans)
    return Dataset.from_dict({"question": questions, "contexts": contexts, "ground_truth": ground_truths, "answer": answers})

def main(k: int):
    ds = build_dataset(k)
    report = evaluate(ds, metrics=[context_precision, faithfulness])
    print(report)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    main(args.k)
