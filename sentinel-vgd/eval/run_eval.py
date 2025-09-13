import json, time, argparse, os
from oracles.sql_exec import execute_sql, hash_rows, ensure_db
from generator.mock_generator import generate_sql

def load_gold(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def run_suite():
    ensure_db()
    records = []
    latencies = []
    correct = 0
    total = 0

    for ex in load_gold(os.path.join(os.path.dirname(__file__), "sql_gold.jsonl")):
        q = ex["question"]
        gold_sql = ex["gold_sql"]
        gold_rows = execute_sql(gold_sql)
        gold_hash = hash_rows(gold_rows)

        t0 = time.time()
        pred_sql = generate_sql(q)
        pred_rows = execute_sql(pred_sql)
        dt = (time.time() - t0) * 1000.0
        latencies.append(dt)

        pred_hash = hash_rows(pred_rows)
        ok = (pred_hash == gold_hash)
        correct += int(ok)
        total += 1

        records.append({
            "question": q,
            "gold_sql": gold_sql,
            "pred_sql": pred_sql,
            "gold_hash": gold_hash,
            "pred_hash": pred_hash,
            "ok": ok,
            "latency_ms": dt,
            "error": pred_rows[0].get("error") if pred_rows and isinstance(pred_rows, list) and "error" in pred_rows[0] else None
        })

    p95 = sorted(latencies)[int(0.95*len(latencies))-1] if latencies else 0.0
    acc = correct / max(total, 1)
    summary = {"total": total, "correct": correct, "accuracy": acc, "p95_latency_ms": p95}
    return records, summary

def write_reports(records, summary):
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "reports"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "..", "reports", "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "records": records}, f, indent=2)

    # Tiny HTML
    rows = "".join(
        f"<tr><td>{r['question']}</td><td><pre>{r['pred_sql']}</pre></td><td>{'✅' if r['ok'] else '❌'}</td><td>{r['latency_ms']:.1f}</td></tr>"
        for r in records
    )
    html = f"""
    <html><head><meta charset='utf-8'><title>Sentinel Eval</title></head>
    <body>
      <h2>Sentinel-VGD Eval</h2>
      <p><b>Accuracy:</b> {summary['accuracy']:.2%} &nbsp; <b>p95 latency (ms):</b> {summary['p95_latency_ms']:.1f}</p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Question</th><th>Pred SQL</th><th>OK</th><th>Latency (ms)</th></tr>
        {rows}
      </table>
    </body></html>
    """
    with open(os.path.join(os.path.dirname(__file__), "..", "reports", "report.html"), "w", encoding="utf-8") as f:
        f.write(html)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true", help="Apply pass/fail gates")
    args = parser.parse_args()

    records, summary = run_suite()
    write_reports(records, summary)
    print("SUMMARY:", json.dumps(summary, indent=2))

    if args.ci:
        ok = True
        if summary["accuracy"] < 0.66:
            print("Gate failed: accuracy < 0.66")
            ok = False
        if summary["p95_latency_ms"] > 2500:
            print("Gate failed: p95 latency > 2500ms")
            ok = False
        if not ok:
            raise SystemExit(1)

if __name__ == "__main__":
    main()
