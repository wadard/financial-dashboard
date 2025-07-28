import pandas as pd

# Generate 50 synthetic transactions
statuses = ["completed", "pending", "failed"]
data = {
    "transaction_id": [f"T{str(i).zfill(4)}" for i in range(1, 51)],
    "user_id": [101 + (i % 10) for i in range(50)],
    "amount": [round(50 + i * 1.5, 2) for i in range(50)],
    "fee": [round(0.75 + (i % 5) * 0.25, 2) for i in range(50)],
    "status": [statuses[i % 3] for i in range(50)],
    "timestamp": pd.date_range("2023-09-01", periods=50, freq="H"),
}

df = pd.DataFrame(data)

# Export to Parquet
df.to_parquet("transactions.parquet", index=False)

print("Parquet file saved: transactions.parquet")
