import os, duckdb, random

def seed(db_path=None):
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), "demo.duckdb")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)
    con.execute("DROP TABLE IF EXISTS customers;")
    con.execute("DROP TABLE IF EXISTS orders;")
    con.execute("CREATE TABLE customers(id INTEGER, name VARCHAR);")
    con.execute("CREATE TABLE orders(id INTEGER, customer_id INTEGER, amount DOUBLE, year INTEGER);")

    customers = [(1, 'Alice'), (2, 'Bob'), (3, 'Charlie'), (4, 'Diana'), (5, 'Ethan')]
    con.executemany("INSERT INTO customers VALUES (?, ?);", customers)

    orders = []
    oid = 1
    rng = random.Random(42)
    for year in (2022, 2023, 2024):
        for cid in range(1, 6):
            for _ in range(rng.randint(3, 8)):
                amt = round(rng.uniform(10, 500), 2)
                orders.append((oid, cid, amt, year))
                oid += 1
    con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?);", orders)
    con.close()
    return db_path

if __name__ == "__main__":
    seed()
    print("Seeded demo.duckdb")
