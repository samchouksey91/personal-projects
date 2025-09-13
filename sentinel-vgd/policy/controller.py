from generator.mock_generator import generate_sql
from oracles.sql_exec import execute_sql

DENYLIST = {"drop", "delete", "update"}

BUDGET = {
    "max_tokens": 4096,
    "max_steps": 3,
    "max_tool_calls": 2,
}

def guardrails(sql: str) -> bool:
    s = sql.lower()
    return not any(word in s for word in DENYLIST)

def solve_with_policy(question: str):
    steps = 0
    tool_calls = 0

    # Step 1: generate SQL
    sql = generate_sql(question)
    steps += 1

    # Guardrails
    guard_ok = guardrails(sql)
    if not guard_ok:
        return {
            "question": question,
            "sql": sql,
            "retrieved_context": [],
            "rows": [],
            "guardrail_pass": False,
            "cost_estimate": {"tokens": 0, "usd": 0.0},
            "note": "Guardrails blocked potentially destructive SQL."
        }

    # Step 2: execute via oracle
    tool_calls += 1
    rows = execute_sql(sql)
    return {
        "question": question,
        "sql": sql,
        "retrieved_context": [],
        "rows": rows,
        "guardrail_pass": True,
        "cost_estimate": {"tokens": 0, "usd": 0.0},
    }
