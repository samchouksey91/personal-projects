# KYC Intake & Risk Note (Simple Demo)

This is a **beginner-friendly** demo that shows how AI workflows can help with KYC document intake,
*without* getting complicated. It reads a small "KYC pack" (a few files), pulls out a few facts,
runs simple checks, and drafts a short **risk note** with **citations** pointing back to the source files.

## Inputs and Outputs

**Inputs (you upload any subset):**
- `passport.txt` *(simulated ID doc)* — contains lines like `Name:`, `DOB:`, `PassportNo:`
- `poa.txt` *(proof of address)* — contains lines like `Address:`, `City:`, `Country:`
- `ownership.txt` *(optional)* — contains owner names and percentages (sum to 100)

> Use the **sample files** in `./samples/` to test immediately.

**Outputs (written to `./out/<run-id>/`):**
- `profile.json` — normalized facts we extracted
- `checklist.json` — simple pass/fail checks (completeness/consistency)
- `risk_note.md` — clear, readable summary with **inline citations** like `[source: poa.txt]`

## Simple design (Mermaid)

```mermaid
flowchart LR
  subgraph User
    U[/"Upload KYC Pack<br/>(passport.txt • poa.txt • ownership.txt)"/]
  end

  subgraph App[FastAPI Service]
    ING[Read files] --> EXT[Extract fields]
    EXT --> VER[Run simple checks]
    VER --> NOTE[Draft risk note (cited)]
  end

  U --> ING
  NOTE -->|Write files| OUT[(./out/run-id)]
```

**What each step does:**
1) **Read files** → load text from `.txt` or simple `.pdf` (text only).  
2) **Extract fields** → regex parse for `Name`, `DOB`, `Address`, `Owner %`.  
3) **Run checks** → ID and Address present? Owners sum to 100% if provided?  
4) **Draft risk note** → short markdown with claims and a `[source: filename]` citation next to each fact.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
# new terminal:
curl -X POST "http://localhost:8000/kyc/process"   -F "files=@samples/passport.txt"   -F "files=@samples/poa.txt"   -F "files=@samples/ownership.txt"
```

**Response:**
```json
{
  "run_id": "2025-09-20T12-34-56",
  "profile_path": "out/2025-09-20T12-34-56/profile.json",
  "checklist_path": "out/2025-09-20T12-34-56/checklist.json",
  "risk_note_path": "out/2025-09-20T12-34-56/risk_note.md"
}
```

## Tech stack
FastAPI, Uvicorn, Pydantic, PyPDF2 (optional PDF text reading)
