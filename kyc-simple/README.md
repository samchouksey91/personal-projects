# KYC Intake & Risk Note 

A **beginner-friendly** demo that reads a small KYC pack, extracts a few facts, runs simple checks,
and drafts a short **risk note** with **citations** to the source files. Now with **PDF samples** and **basic OCR**.

![Workflow](docs/kyc-workflow-arch.png)

> Place your exported diagram at `docs/kyc-workflow-arch.png`. The app flow and steps below match the diagram.

## Inputs and Outputs
- Inputs: `passport.pdf`, `poa.pdf`, `ownership.pdf` (samples included)
- Outputs: `out/<run-id>/profile.json`, `checklist.json`, `risk_note.md`

## Simple design (Mermaid)
```mermaid
flowchart LR
  subgraph User
    U[/"Upload KYC Pack<br/>passport.pdf • poa.pdf • ownership.pdf"/]
  end

  subgraph App[FastAPI Service]
    ING[Read + OCR] --> EXT[Extract fields]
    EXT --> VER[Run checks]
    VER --> NOTE[Draft risk note cited]
  end

  U --> ING
  NOTE -->|Write files| OUT[./out/run-id]
```

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
# UI: http://localhost:8000
```

## OCR
Install Poppler + Tesseract for OCR (see README full variant in earlier message).
