from agent.generator import generate_sql
from agent.oracle_sql import execute_sql

DENYLIST = {"drop", "delete", "update"}

def safe(sql: str) -> bool:
    s = sql.lower()
    return not any(word in s for word in DENYLIST)

def try_once(question: str):
    sql = generate_sql(question)
    if not safe(sql):
        return {"ok": False, "sql": sql, "rows": [], "reason": "blocked_by_guardrails"}
    rows = execute_sql(sql)
    if rows and isinstance(rows, list) and "error" in rows[0]:
        return {"ok": False, "sql": sql, "rows": rows, "reason": "execution_error"}
    return {"ok": True, "sql": sql, "rows": rows, "reason": "verified"}

def answer_question(question: str):
    a1 = try_once(question)
    if a1["ok"]:
        return {
            "question": question,
            "sql": a1["sql"],
            "rows": a1["rows"],
            "verified": True,
            "note": a1["reason"]
        }

    # Simple repair example: missing year filter
    if "spend" in question.lower() and "2023" in question.lower() and "WHERE o.year=2023" not in a1.get("sql",""):
        repaired = a1.get("sql","") + " WHERE o.year=2023" if "WHERE" not in a1.get("sql","") else a1["sql"]
        if safe(repaired):
            rows = execute_sql(repaired)
            if rows and not ("error" in rows[0] if isinstance(rows, list) else False):
                return {
                    "question": question,
                    "sql": repaired,
                    "rows": rows,
                    "verified": True,
                    "note": "repaired_missing_year"
                }

    return {
        "question": question,
        "sql": a1.get("sql",""),
        "rows": a1.get("rows", []),
        "verified": False,
        "note": a1["reason"]
    }
