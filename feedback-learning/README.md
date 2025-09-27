# Feedback Learning — Prod-Friendly Starter (DPO + LoRA)

**Use case:** Improve a production LLM feature using real user choices (A vs B / thumbs) via **offline DPO + LoRA**.

## Design
```mermaid
flowchart LR
  U[User prompt] --> AGEN[/Generate A & B/]
  AGEN --> LOG[Log feedback]
  LOG --> STORE[(logs.jsonl)]
  STORE --> BUILD[Prefs: {prompt, chosen, rejected}]
  BUILD --> DPO[Train LoRA via DPO]
  DPO --> CKPT[(adapter)]
  CKPT --> EVAL[Offline eval]
  CKPT -->|Canary| AGEN
```

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Train from feedback
```bash
python -m app.build_prefs --out data/prefs/train.jsonl
python -m app.trainer_dpo --prefs data/prefs/train.jsonl --out_dir out/adapters/dpo-$(date +%Y%m%d-%H%M)
```

## Evaluate
```bash
python -m app.eval --ckpt out/adapters/<your-dir> --n 50
```

## Layout
- `app/main.py` (API), `app/policy.py` (models), `app/build_prefs.py` (dataset), `app/trainer_dpo.py` (DPO), `app/eval.py` (win-rate)
- `data/seeds/prefs.jsonl`, `data/eval/eval.jsonl`, `data/logs/logs.jsonl`
