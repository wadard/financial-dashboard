import pandas as pd


class TransactionKPIs:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def failure_rate(self) -> float:
        total = len(self.df)
        failed = len(self.df[self.df["status"] == "failed"])
        return failed / total if total else 0

    def completion_rate(self) -> float:
        completed = len(self.df[self.df["status"] == "completed"])
        return completed / len(self.df) if len(self.df) else 0

    def active_users(self) -> int:
        return self.df["user_id"].nunique()

    def transactions_per_day(self) -> pd.Series:
        df_copy = self.df.copy()

        # ✅ Use schema-normalized 'date' column
        if "date" not in df_copy.columns:
            raise KeyError("Expected 'date' column not found for transactions_per_day.")

        df_copy["day"] = pd.to_datetime(df_copy["date"], errors="coerce").dt.date
        return df_copy.groupby("day")["transaction_id"].count()

    def evaluate_all(self) -> dict:
        return {
            "Failure Rate": self.failure_rate(),
            "Completion Rate": self.completion_rate(),
            "Unique Users": self.active_users(),
            "Transactions Per Day": self.transactions_per_day().to_dict(),
        }
