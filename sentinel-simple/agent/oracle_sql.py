import duckdb, os, pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "demo.duckdb")

def ensure_db():
    if not os.path.exists(DB_PATH):
        from data.seed_duckdb import seed
        seed(DB_PATH)

def execute_sql(sql: str):
    ensure_db()
    con = duckdb.connect(DB_PATH, read_only=False)
    try:
        df = con.execute(sql).fetchdf()
        return df.to_dict(orient="records")
    except Exception as e:
        return [{"error": str(e)}]
    finally:
        con.close()
