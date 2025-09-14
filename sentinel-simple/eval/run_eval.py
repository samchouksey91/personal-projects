import json, time, os
from agent.generator import generate_sql
from agent.oracle_sql import execute_sql

GOLD = [
    {"question": "Top 3 customers by spend in 2023",
     "gold_sql": "SELECT c.name, SUM(o.amount) AS total_spend FROM customers c JOIN orders o ON c.id = o.customer_id WHERE o.year=2023 GROUP BY 1 ORDER BY total_spend DESC LIMIT 3;"},
    {"question": "What is the total revenue in 2023?",
     "gold_sql": "SELECT SUM(amount) AS revenue_2023 FROM orders WHERE year=2023;"},
    {"question": "Show orders per customer (desc)",
     "gold_sql": "SELECT c.name, COUNT(o.id) AS orders_count FROM customers c LEFT JOIN orders o ON c.id=o.customer_id GROUP BY 1 ORDER BY orders_count DESC;"}
]

def hash_rows(rows):
    import hashlib
    m = hashlib.md5()
    for row in rows:
        s = "|".join(f"{k}={row[k]}" for k in sorted(row.keys()))
        m.update(s.encode("utf-8"))
        m.update(b"\n")
    return m.hexdigest()

def main():
    os.makedirs("reports", exist_ok=True)
    records, lats = [], []
    correct = 0
    for ex in GOLD:
        gold_rows = execute_sql(ex["gold_sql"])
        gold_hash = hash_rows(gold_rows)

        t0 = time.time()
        pred_sql = generate_sql(ex["question"])
        pred_rows = execute_sql(pred_sql)
        dt = (time.time() - t0) * 1000.0
        lats.append(dt)

        ok = hash_rows(pred_rows) == gold_hash
        correct += int(ok)

        records.append({"question": ex["question"], "pred_sql": pred_sql, "ok": ok, "latency_ms": dt})

    acc = correct / len(GOLD)
    p95 = sorted(lats)[int(0.95*len(lats))-1]
    summary = {"accuracy": acc, "p95_latency_ms": p95}
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "records": records}, f, indent=2)
    print(json.dumps({"summary": summary}, indent=2))

if __name__ == "__main__":
    main()
