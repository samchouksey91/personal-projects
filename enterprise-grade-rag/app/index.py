import os, json, argparse, pickle
from pathlib import Path
from typing import List, Dict
from .utils import chunk_text, ensure_dir

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import numpy as np

from .vectorstore import FaissStore

DATA_DIR = Path("data/corpus")
OUT_DIR = Path("out")
IDX_DIR = OUT_DIR / "index"

def load_corpus() -> List[Dict]:
    docs = []
    for p in sorted(DATA_DIR.glob("*.txt")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text, max_chars=800)
        for i, ch in enumerate(chunks):
            docs.append({"doc_id": p.stem, "chunk_id": f"{p.stem}_{i}", "text": ch, "source": str(p.name)})
    return docs

def build_bm25(chunks: List[Dict]):
    tokenized = [c["text"].lower().split() for c in chunks]
    return BM25Okapi(tokenized), tokenized

def build_embeddings(chunks: List[Dict], model_name: str):
    model = SentenceTransformer(model_name)
    X = model.encode([c["text"] for c in chunks], normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=True)
    return X

def build(args):
    ensure_dir(str(IDX_DIR))
    model_name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    chunks = load_corpus()
    (IDX_DIR / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    bm25, tokenized = build_bm25(chunks)
    with open(IDX_DIR / "bm25.pkl", "wb") as f:
        pickle.dump({"bm25": bm25, "tokenized": tokenized}, f)

    X = build_embeddings(chunks, model_name)
    np.save(IDX_DIR / "embeddings.npy", X)

    fs = FaissStore(dim=X.shape[1])
    fs.save(X)

    print(f"Built index for {len(chunks)} chunks at {IDX_DIR}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build"])
    args = ap.parse_args()
    if args.cmd == "build":
        build(args)
