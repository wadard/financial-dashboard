class TransactionMetrics:
    def __init__(self, df):
        self.df = df[df["status"] == "completed"]  # only count valid transactions

    def total_revenue(self):
        return self.df["amount"].sum()

    def total_fees(self):
        return self.df["fee"].sum()

    def average_transaction_value(self):
        return self.df["amount"].mean()

    def transaction_volume_per_user(self):
        return self.df.groupby("user_id")["transaction_id"].count()

    def calculate_all(self):
        return {
            "Total Revenue": self.total_revenue(),
            "Total Fees": self.total_fees(),
            "Average Transaction": self.average_transaction_value(),
            "Volume per User": self.transaction_volume_per_user().to_dict(),
        }
