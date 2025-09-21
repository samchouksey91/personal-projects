import re
from typing import Dict, Any

FIELD_PATTERNS = {
    "name": re.compile(r"(?i)name\s*:\s*([A-Za-z\s\.'-]+)"),
    "dob": re.compile(r"(?i)(dob|date\s*of\s*birth)\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}/[0-9]{2}/[0-9]{4})"),
    "passport_no": re.compile(r"(?i)(passport\s*no|passport)\s*:\s*([A-Z0-9]+)"),
    "address": re.compile(r"(?i)address\s*:\s*([\w\s,.-]+)"),
    "city": re.compile(r"(?i)city\s*:\s*([A-Za-z\s.-]+)"),
    "country": re.compile(r"(?i)country\s*:\s*([A-Za-z\s.-]+)"),
}

OWNER_LINE = re.compile(r"(?i)^\s*owner\s*:\s*([^,]+),\s*percent\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*%")

def parse_fields(text: str) -> Dict[str, str]:
    data = {}
    for key, pat in FIELD_PATTERNS.items():
        m = pat.search(text or "")
        if m:
            data[key] = (m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)).strip()
    return data

def parse_owners(text: str):
    owners = []
    for line in (text or "").splitlines():
        m = OWNER_LINE.search(line)
        if m:
            owners.append({"name": m.group(1).strip(), "percent": float(m.group(2))})
    return owners

def extract_profile(texts: Dict[str, str]) -> Dict[str, Any]:
    merged = "\\n\\n".join([texts[k] for k in sorted(texts.keys())])
    base = parse_fields(merged)
    owners = parse_owners(merged)

    profile = {
        "customer_type": "individual",
        "name": base.get("name"),
        "dob": base.get("dob"),
        "id": {"passport_no": base.get("passport_no"), "source": None},
        "address": {
            "address": base.get("address"),
            "city": base.get("city"),
            "country": base.get("country"),
            "source": None,
        },
        "owners": owners,
        "sources": list(texts.keys()),
    }

    # naive source hinting
    for fname, txt in texts.items():
        if profile["id"]["passport_no"] and profile["id"]["passport_no"] in (txt or ""):
            profile["id"]["source"] = fname
        if profile["name"] and re.search(rf"(?i){re.escape(profile['name'])}", txt or ""):
            profile.setdefault("name_source", fname)
        if profile["address"]["address"] and profile["address"]["address"] in (txt or ""):
            profile["address"]["source"] = fname

    return profile
