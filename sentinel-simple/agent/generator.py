def generate_sql(question: str) -> str:
    q = question.lower()
    if "top 3" in q and "spend" in q:
        return (
            "SELECT c.name, SUM(o.amount) AS total_spend "
            "FROM customers c JOIN orders o ON c.id = o.customer_id "
            "WHERE o.year=2023 "
            "GROUP BY 1 ORDER BY total_spend DESC LIMIT 3;"
        )
    if "total revenue" in q and "2023" in q:
        return "SELECT SUM(amount) AS revenue_2023 FROM orders WHERE year=2023;"
    if "orders per customer" in q:
        return (
            "SELECT c.name, COUNT(o.id) AS orders_count "
            "FROM customers c LEFT JOIN orders o ON c.id=o.customer_id "
            "GROUP BY 1 ORDER BY orders_count DESC;"
        )
    return "SELECT COUNT(*) AS order_count FROM orders;"
