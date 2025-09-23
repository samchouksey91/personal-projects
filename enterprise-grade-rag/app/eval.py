import json, argparse, statistics
from pathlib import Path
from typing import List, Dict
from .pipeline import answer
from .utils import now_ts

EVAL_FILE = Path("data/eval/eval.jsonl")
OUT_DIR = Path("out")

def citation_precision(citations: List[Dict], gold_docs: List[str]) -> float:
    if not citations: return 0.0
    hit = sum(1 for c in citations if c.get("doc_id") in gold_docs)
    return hit / len(citations)

def run(k: int):
    rows = [json.loads(l) for l in EVAL_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
    results = []
    for r in rows:
        q = r["question"]; gold_docs = r.get("gold_doc_ids", [])
        res = answer(q, top_k=k, alpha=0.6, use_rerank=True)
        cp = citation_precision(res["citations"], gold_docs)
        results.append({"q": q, "latency_s": res["latency_s"], "citation_precision": cp})
    report = {
        "k": k,
        "n": len(results),
        "avg_latency_s": round(statistics.mean([r["latency_s"] for r in results]), 3),
        "avg_citation_precision": round(statistics.mean([r["citation_precision"] for r in results]), 3),
        "per_query": results,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outp = OUT_DIR / f"eval-{now_ts()}.json"
    outp.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    run(args.k)
