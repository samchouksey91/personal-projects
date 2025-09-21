from typing import List, Dict
import os
from PyPDF2 import PdfReader

try:
    import pytesseract
    from pdf2image import convert_from_path
except Exception:
    pytesseract = None
    convert_from_path = None

def read_text_from_pdf(path: str) -> str:
    text_parts = []
    try:
        reader = PdfReader(path)
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    except Exception:
        pass
    text = "\n".join(text_parts).strip()

    if not text and convert_from_path and pytesseract:
        try:
            pages = convert_from_path(path, dpi=200)  # requires Poppler
            ocr_texts = []
            for img in pages:
                ocr_texts.append(pytesseract.image_to_string(img))
            text = "\n".join(ocr_texts).strip()
        except Exception:
            text = ""
    return text

def read_files_to_texts(paths: List[str]) -> Dict[str, str]:
    out = {}
    for p in paths:
        out[os.path.basename(p)] = read_text_from_pdf(p)
    return out
