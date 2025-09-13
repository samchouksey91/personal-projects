from fastapi import FastAPI
from pydantic import BaseModel
import time

from policy.controller import solve_with_policy
from oracles.sql_exec import ensure_db

app = FastAPI(title="Sentinel-VGD API", version="0.1.0")

class SolveRequest(BaseModel):
    question: str

@app.on_event("startup")
def startup():
    ensure_db()

@app.post("/solve_sql")
def solve_sql(req: SolveRequest):
    t0 = time.time()
    result = solve_with_policy(req.question)
    result["latency_ms"] = int((time.time() - t0) * 1000)
    return result

@app.get("/healthz")
def healthz():
    return {"ok": True}

from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
