import os, json, time, pickle
from typing import List, Dict
from pathlib import Path
import numpy as np

from .utils import sent_tokenize, normalize_text
from cachetools import TTLCache, cached

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .vectorstore import FaissStore

IDX_DIR = Path("out/index")

RETR_CACHE = TTLCache(maxsize=512, ttl=300)
EMB_CACHE = TTLCache(maxsize=256, ttl=1800)

def load_index():
    chunks = json.loads((IDX_DIR / "chunks.json").read_text(encoding="utf-8"))
    with open(IDX_DIR / "bm25.pkl", "rb") as f:
        p = pickle.load(f)
    X = None
    if (IDX_DIR / "embeddings.npy").exists():
        X = np.load(IDX_DIR / "embeddings.npy")
    return chunks, p["bm25"], p["tokenized"], X

def get_embed_model(name="sentence-transformers/all-MiniLM-L6-v2"):
    if name in EMB_CACHE: return EMB_CACHE[name]
    m = SentenceTransformer(name); EMB_CACHE[name] = m; return m

@cached(RETR_CACHE)
def hybrid_retrieve_cached(question: str, top_k: int, alpha: float, embed_model: str):
    return hybrid_retrieve(question, top_k=top_k, alpha=alpha, embed_model=embed_model)

def hybrid_retrieve(question: str, top_k: int = 8, alpha: float = 0.6,
                    embed_model="sentence-transformers/all-MiniLM-L6-v2"):
    chunks, bm25, tokenized, X = load_index()
    bm25_scores = bm25.get_scores(question.lower().split())
    bm25_scores = np.array(bm25_scores, dtype=np.float32)

    fs = FaissStore(dim=X.shape[1] if X is not None else 384)
    fs.load()
    em = get_embed_model(embed_model)
    qv = em.encode([question], normalize_embeddings=True, convert_to_numpy=True)
    faiss_hits = fs.search(qv, top_k=top_k)
    emb_scores = np.zeros(len(chunks), dtype=np.float32)
    for idx, s in faiss_hits:
        emb_scores[idx] = max(emb_scores[idx], s)

    def norm(a):
        a = a - a.min(); m = a.max()
        return a / m if m > 0 else a
    s1, s2 = norm(bm25_scores), norm(emb_scores)
    score = (1-alpha)*s1 + alpha*s2
    idx = np.argsort(-score)[:top_k]
    return [(int(i), float(score[i])) for i in idx]

def rerank(question: str, candidates, max_n: int = 8, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
    try:
        ce = CrossEncoder(model_name)
    except Exception:
        return candidates
    chunks, _, _, _ = load_index()
    pairs = [[question, chunks[i]["text"]] for i,_ in candidates[:max_n]]
    ce_scores = ce.predict(pairs)
    order = np.argsort(-ce_scores)
    return [(candidates[i][0], float(ce_scores[i])) for i in order]

def compose_answer(question: str, chosen: List[int], max_sentences: int = 3):
    chunks, _, _, _ = load_index()
    sents, meta = [], []
    for idx in chosen:
        ch = chunks[idx]
        for s in sent_tokenize(ch["text"]):
            if len(s) > 15:
                sents.append(s)
                meta.append({"doc_id": ch["doc_id"], "chunk_id": ch["chunk_id"], "source": ch["source"], "text": s})
    if not sents:
        return "I couldn't find relevant information.", []
    vect = TfidfVectorizer().fit([question] + sents)
    qv = vect.transform([question]); sv = vect.transform(sents)
    sims = cosine_similarity(qv, sv).ravel()
    order = np.argsort(-sims)[:max_sentences]
    picked = [meta[i] for i in order]
    answer = " ".join([m["text"] for m in picked])
    citations = [{"source": m["source"], "doc_id": m["doc_id"], "chunk_id": m["chunk_id"], "quote": m["text"]} for m in picked]
    return answer, citations

def citation_check(citations: List[Dict]) -> List[Dict]:
    out = []
    for c in citations:
        q = normalize_text(c.get("quote",""))
        if len(q) >= 20: out.append(c)
    return out

def answer(question: str, top_k=8, alpha=0.6, use_rerank=True) -> Dict:
    T0 = time.time()
    cand = hybrid_retrieve_cached(question, top_k=top_k, alpha=alpha, embed_model=os.getenv("EMBED_MODEL","sentence-transformers/all-MiniLM-L6-v2"))
    if use_rerank: cand = rerank(question, cand)
    chosen = [i for i,_ in cand[:min(5, len(cand))]]
    ans, cites = compose_answer(question, chosen)
    cites = citation_check(cites)
    T1 = time.time()
    return {
        "question": question,
        "answer": ans,
        "citations": cites,
        "latency_s": round(T1-T0, 3),
        "retrieval": [{"chunk_index": int(i), "score": float(s)} for i,s in cand]
    }
