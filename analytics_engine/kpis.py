import pandas as pd


class TransactionKPIs:
    def __init__(self, df):
        self.df = df

    def failure_rate(self):
        total = len(self.df)
        failed = len(self.df[self.df["status"] == "failed"])
        return failed / total if total else 0

    def completion_rate(self):
        completed = len(self.df[self.df["status"] == "completed"])
        return completed / len(self.df)

    def active_users(self):
        return self.df["user_id"].nunique()

    def transactions_per_day(self):
        df_copy = self.df.copy()
        df_copy["date"] = pd.to_datetime(df_copy["timestamp"]).dt.date
        return df_copy.groupby("date")["transaction_id"].count()

    def evaluate_all(self):
        return {
            "Failure Rate": self.failure_rate(),
            "Completion Rate": self.completion_rate(),
            "Unique Users": self.active_users(),
            "Transactions Per Day": self.transactions_per_day().to_dict(),
        }
