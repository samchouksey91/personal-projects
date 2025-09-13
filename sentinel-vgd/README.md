# Sentinel-VGD — Verifier-Guided, Budgeted Decoding (MVP)

A production-style **agentic reliability** starter that solves SQL tasks end-to-end with:
- A **policy controller** (budgets, retries, guardrails)
- A pluggable **generator** (LLM adapter; mock included for demo)
- Deterministic **oracles** (DuckDB execution + row-hash comparison)
- Simple **verifier** stub (calibratable later)
- **Eval harness** + CI-style gates
- FastAPI service exposing `/solve_sql` and `/metrics`

> MVP is self-contained, no secrets needed. Default generator is a tiny heuristic “mock” so reviewers can run it instantly. Swap to your LLM provider via `generator/` adapters.

## Quickstart (local, no Docker)
```bash
# 1) Create demo DuckDB and seed sample data
python data/seed_duckdb.py

# 2) Run evaluation (prints a scorecard, writes reports/summary.json and report.html)
python eval/run_eval.py

# 3) Start API
uvicorn api.main:app --reload
# curl -X POST localhost:8000/solve_sql -H "Content-Type: application/json" #   -d '{"question":"Top 3 customers by spend in 2023"}'
```

## Makefile targets
```bash
make seed     # seed DuckDB demo data
make demo     # run eval harness (scorecard in terminal)
make up       # start FastAPI (uvicorn)
make ci       # run eval with pass/fail gates
```

## Docker (optional)
```bash
docker compose up --build
```

## Endpoints
- `POST /solve_sql`: `{question}` → `{sql, rows, retrieved_context, latency_ms, cost_estimate, guardrail_pass}`
- `GET  /metrics`: Prometheus metrics (QPS, latency histogram placeholders)

## Repo map
```
sentinel-vgd/
├─ README.md
├─ Makefile
├─ docker-compose.yml
├─ requirements.txt
├─ Dockerfile
├─ api/
│  └─ main.py
├─ policy/
│  └─ controller.py
├─ generator/
│  ├─ mock_generator.py
│  └─ providers.py
├─ verifier/
│  ├─ model.py
│  └─ train.py
├─ oracles/
│  └─ sql_exec.py
├─ data/
│  ├─ seed_duckdb.py
│  └─ demo.duckdb        # created by seed script
├─ eval/
│  ├─ sql_gold.jsonl
│  └─ run_eval.py
├─ reports/
│  └─ (generated) summary.json / report.html
└─ dashboards/
   └─ grafana.json
```

## CI Gates (MVP defaults)
- Execution accuracy (exact row match) ≥ 0.66
- p95 latency ≤ 2.5s (mock generator is fast)
- Guardrail violations = 0

Tune thresholds in `eval/run_eval.py`.

## Roadmap
- Train real **verifier** (MiniLM) on pass/fail traces; calibrate with temperature scaling
- Add **repair strategies** (reflective promptlets) when `p_pass < τ`
- Providers: OpenAI/Gemini/local HF; vLLM serving path
- Extend scenarios: code (unit tests), RAG QA (grounding), math (exact match)
