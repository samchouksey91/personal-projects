# Personal Projects — Applied GenAI Portfolio

A curated set of **production-oriented** GenAI projects that demonstrate solution design, measurable quality, and pragmatic engineering.

> Each folder has its own README with deeper technical details and setup steps. This root README gives busy reviewers a fast overview.

## What’s inside

| Project | One-liner | Why it matters (enterprise) |
|---|---|---|
| [`enterprise-grade-rag/`](enterprise-grade-rag) | **Trustworthy RAG** with hybrid retrieval, citations, FAISS/pgvector-ready, metrics & evals | Reliable answers with evidence, measurable quality, and cost/latency controls |
| [`feedback-learning/`](feedback-learning) | **User feedback → model learning** (A/B logging → DPO + LoRA) | Turns real usage into weekly improvements with safe offline updates & canary rollout |
| [`kyc-agent/`](kyc-agent) | **KYC intake & risk notes**: document upload → OCR → structured summary + risk flags | Cuts onboarding time and manual effort; auditable outputs with extracted fields |
| [`sentinel-simple/`](sentinel-simple) | **Guarded agent / SQL validator**: verify before answer, repair on failure, budgeted steps | Safer agentic patterns for enterprise data access and query generation |

---

## Quick demo run (summary)

All projects use Python. Recommended: **Python 3.10+** and a virtual environment.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 1) Enterprise-grade RAG
```bash
cd enterprise-grade-rag
pip install -r requirements.txt
python -m app.index build                 # build BM25 + embeddings + FAISS
uvicorn app.main:app --reload             # serves /answer and /metrics

# Ask a question
curl -s -X POST http://localhost:8000/answer   -H "Content-Type: application/json"   -d '{"question":"What are the controls for customer data access?"}' | jq .

# Evaluate (RAGAS + simple citation precision)
python -m app.eval_ragas --k 5
python -m app.eval --k 5
```

**Highlights**
- Hybrid retrieval (BM25 + embeddings via FAISS), optional re-ranker  
- Citations + simple citation checker  
- Prometheus `/metrics` (requests, errors, latency)  
- RAGAS metrics (context precision, faithfulness)

---

### 2) Feedback Learning (DPO + LoRA)
```bash
cd feedback-learning
pip install -r requirements.txt
uvicorn app.main:app --reload             # /generate (A/B), /feedback (log)

# Build preference pairs (starts with seeds)
python -m app.build_prefs --out data/prefs/train.jsonl

# Train a small LoRA adapter with DPO
python -m app.trainer_dpo --prefs data/prefs/train.jsonl --out_dir out/adapters/dpo-run

# Offline evaluation (heuristic win-rate vs base)
python -m app.eval --ckpt out/adapters/dpo-run --n 50
```

**Highlights**
- Online path stays **stateless**; learning is **offline** and auditable  
- Canary rollout pattern (base vs adapter A/B)  
- Easy to plug your **real thumbs/A-B logs** and task KPIs later

---

### 3) KYC Agent (intake & risk notes)
```bash
cd kyc-agent
pip install -r requirements.txt
uvicorn api.main:app --reload             # serves a clean upload UI at /
```

**Typical flow**
1. Upload **KYC PDFs** (IDs, proof of address, ownership docs)  
2. OCR → extract **entities/fields** → classify risks → produce a **concise memo**  
3. Download JSON/CSV of extracted fields and the memo

**Notes**
- Works with image-only PDFs (Tesseract + Poppler)  
- Clear README diagrams and step-by-step runbook

---

### 4) Sentinel (guarded agent / SQL validator)
```bash
cd sentinel-simple
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Idea**
- For tasks like **text-to-SQL** or **policy Q&A**, responses are **verified first**.  
- If verification fails, the agent attempts **small repairs** (bounded “budget”); otherwise it stops.

---

## Design themes across the portfolio

- **Reliability over flash**: citations, verification, offline evals, and guardrails come first.  
- **Measurability**: every project includes simple, extensible metrics (accuracy proxies, latency, cost).  
- **Ops-ready**: config via env vars, Prometheus hooks (where useful), and clear runbooks.  
- **Swap-friendly**: model/vector-store choices are easy to change as infra and budgets evolve.

---

## Tech stack (at a glance)

- **Python**, FastAPI, Uvicorn  
- Retrieval: **Rank-BM25**, **Sentence-Transformers**, **FAISS** (pgvector-ready)  
- Training: **Transformers**, **TRL (DPO)**, **PEFT/LoRA**  
- OCR: **Tesseract**, **pdf2image/Poppler** (in `kyc-agent`)  
- Observability: **Prometheus** metrics (RAG)  
- Evaluation: **RAGAS**, simple heuristic win-rates, JSONL logs

---

## How to read this repo

- Start with **[`enterprise-grade-rag/`](enterprise-grade-rag)** for the backbone patterns (retrieval, citations, evals).  
- See **[`feedback-learning/`](feedback-learning)** to close the loop with real user signals.  
- Review **[`kyc-agent/`](kyc-agent)** for a concrete BFSI-friendly workflow with documents.  
- Use **[`sentinel-simple/`](sentinel-simple)** as a pattern for guarded/verified agent steps.

---

## Roadmap (next steps)

- Add **Redis** caching and full **pgvector** wiring to RAG.  
- Replace heuristic evals with a **reward model** and **task-level KPIs**.  
- Add **policy/guardrail checks** (PII, toxicity, compliance) to all online paths.  
- Optional **web UIs** for RAG and Sentinel with session history and download-able outputs.

---

**Questions or suggestions?** Open an issue, or ping me on LinkedIn.
