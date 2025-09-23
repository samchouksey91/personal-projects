import json
from pathlib import Path
from typing import List, Tuple
import numpy as np

IDX_DIR = Path("out/index")

class FaissStore:
    def __init__(self, dim: int):
        import faiss  # type: ignore
        self.faiss = faiss
        self.dim = dim
        self.index = None
        self.chunks = None

    def load(self):
        import faiss
        self.chunks = json.loads((IDX_DIR / "chunks.json").read_text(encoding="utf-8"))
        self.index = faiss.read_index(str(IDX_DIR / "faiss.index"))

    def save(self, X: np.ndarray):
        import faiss
        idx = faiss.IndexFlatIP(X.shape[1])
        idx.add(X.astype("float32"))
        faiss.write_index(idx, str(IDX_DIR / "faiss.index"))

    def search(self, qv: np.ndarray, top_k: int = 8):
        D, I = self.index.search(qv.astype("float32"), top_k)
        return [(int(i), float(d)) for i, d in zip(I[0], D[0])]

class PgVectorStore:
    def __init__(self, url: str, table: str = "chunks"): pass
    def load(self): pass
    def save(self, X: np.ndarray): pass
    def search(self, qv: np.ndarray, top_k: int = 8): raise NotImplementedError
