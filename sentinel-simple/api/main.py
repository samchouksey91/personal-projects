from fastapi import FastAPI
from pydantic import BaseModel
import time

from agent.policy import answer_question
from agent.oracle_sql import ensure_db

app = FastAPI(title="Reliable SQL Agent", version="0.1.0")

class Ask(BaseModel):
    question: str

@app.on_event("startup")
def startup():
    ensure_db()

@app.post("/solve_sql")
def solve_sql(body: Ask):
    t0 = time.time()
    out = answer_question(body.question)
    out["latency_ms"] = int((time.time() - t0) * 1000)
    return out

@app.get("/healthz")
def healthz():
    return {"ok": True}
