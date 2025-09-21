from typing import List, Dict
import os
from PyPDF2 import PdfReader

def read_text_from_pdf(path: str) -> str:
    try:
        reader = PdfReader(path)
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception:
        return ""

def read_text_from_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def read_files_to_texts(paths: List[str]) -> Dict[str, str]:
    out = {}
    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        if ext == ".pdf":
            out[os.path.basename(p)] = read_text_from_pdf(p)
        else:
            out[os.path.basename(p)] = read_text_from_txt(p)
    return out
