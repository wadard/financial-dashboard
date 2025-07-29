from analytics_engine.result import AnalyticsResult

from .kpis import TransactionKPIs
from .metrics import TransactionMetrics


class AnalyticsEngine:
    def __init__(self, dataframe):
        self.df = dataframe
        self.metrics = TransactionMetrics(self.df)
        self.kpis = TransactionKPIs(self.df)

    def run_all_analytics(self) -> AnalyticsResult:
        metrics = self.metrics.calculate_all()
        kpis = self.kpis.evaluate_all()

        return AnalyticsResult(metrics=metrics, kpis=kpis)
