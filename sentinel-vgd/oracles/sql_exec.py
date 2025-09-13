import duckdb
import os
import hashlib
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo.duckdb")

def ensure_db():
    if not os.path.exists(DB_PATH):
        from data.seed_duckdb import seed
        seed(DB_PATH)

def get_connection():
    ensure_db()
    con = duckdb.connect(DB_PATH, read_only=False)
    return con

def execute_sql(sql: str):
    con = get_connection()
    try:
        df = con.execute(sql).fetchdf()
        return df.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]

def hash_rows(rows):
    m = hashlib.md5()
    for row in rows:
        s = "|".join(f"{k}={row[k]}" for k in sorted(row.keys()))
        m.update(s.encode("utf-8"))
        m.update(b"\n")
    return m.hexdigest()
