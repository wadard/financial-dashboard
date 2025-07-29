polars_sql_queries = {
    "completed_transactions_per_day": """
        SELECT DATE(timestamp) AS day, COUNT(*) AS completed
        FROM data WHERE status = 'completed'
        GROUP BY day
    """,
    "fee_rate": """
        SELECT SUM(fee) / SUM(amount) AS fee_rate FROM data
        WHERE status = 'completed'
    """,
    "user_activity": """
        SELECT user_id, COUNT(*) AS tx_count FROM data
        GROUP BY user_id
    """,
}
