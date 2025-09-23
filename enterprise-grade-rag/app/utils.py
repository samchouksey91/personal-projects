import re, hashlib, os

SENT_SPLIT = re.compile(r'(?<=[\.\!\?])\s+')

def normalize_text(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '')).strip()

def chunk_text(text: str, max_chars: int = 800):
    text = normalize_text(text)
    parts = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        slice_ = text[start:end]
        last = max(slice_.rfind('. '), slice_.rfind('? '), slice_.rfind('! '))
        if last > 0 and end < len(text):
            end = start + last + 1
        parts.append(text[start:end].strip())
        start = end
    return [p for p in parts if p]

def sent_tokenize(text: str):
    return [s.strip() for s in SENT_SPLIT.split(text or '') if s.strip()]

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8')).hexdigest()

def now_ts() -> str:
    import datetime
    return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)
