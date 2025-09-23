import time
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from .pipeline import answer
from .metrics import record_request, record_error, observe_latency
from prometheus_client import make_asgi_app

app = FastAPI(title="Prod RAG Simple", version="0.2.0")
app.mount("/metrics", make_asgi_app())

class AskIn(BaseModel):
    question: str
    top_k: Optional[int] = 8
    alpha: Optional[float] = 0.6
    use_rerank: Optional[bool] = True

@app.post("/answer")
def post_answer(body: AskIn):
    record_request()
    t0 = time.time()
    try:
        return answer(body.question, top_k=body.top_k, alpha=body.alpha, use_rerank=body.use_rerank)
    except Exception:
        record_error()
        raise
    finally:
        observe_latency(time.time() - t0)

@app.get("/healthz")
def healthz():
    return {"ok": True}
