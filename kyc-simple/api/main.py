from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os, json

from kyc.ingest import read_files_to_texts
from kyc.extract import extract_profile
from kyc.verify import run_checks
from kyc.note import draft_note

app = FastAPI(title="KYC Simple Demo", version="0.2.0")

os.makedirs("out", exist_ok=True)
app.mount("/out", StaticFiles(directory="out"), name="out")
app.mount("/docs", StaticFiles(directory="docs"), name="docs")
app.mount("/samples", StaticFiles(directory="samples"), name="samples")

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

class ProcessResponse(BaseModel):
    run_id: str
    profile_path: str
    checklist_path: str
    risk_note_path: str

@app.post("/kyc/process", response_model=ProcessResponse)
async def process(files: List[UploadFile] = File(...)):
    run_id = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = os.path.join("out", run_id)
    os.makedirs(out_dir, exist_ok=True)

    saved = {}
    for f in files:
        dest = os.path.join(out_dir, f.filename)
        with open(dest, "wb") as w:
            w.write(await f.read())
        saved[f.filename] = dest

    texts = read_files_to_texts(list(saved.values()))
    profile = extract_profile(texts)
    checks = run_checks(profile)
    note = draft_note(profile, checks)

    profile_path = os.path.join(out_dir, "profile.json")
    checklist_path = os.path.join(out_dir, "checklist.json")
    risk_note_path = os.path.join(out_dir, "risk_note.md")

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    with open(checklist_path, "w", encoding="utf-8") as f:
        json.dump(checks, f, indent=2, ensure_ascii=False)
    with open(risk_note_path, "w", encoding="utf-8") as f:
        f.write(note)

    return ProcessResponse(run_id=run_id, profile_path=profile_path, checklist_path=checklist_path, risk_note_path=risk_note_path)

@app.get("/healthz")
def healthz():
    return {"ok": True}
