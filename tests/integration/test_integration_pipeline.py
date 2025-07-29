import unittest

import pandas as pd

from analytics_engine.core import AnalyticsEngine
from analytics_engine.result import AnalyticsResult


class TestIntegrationPipeline(unittest.TestCase):
    def setUp(self):
        # Simulated ingestion output from transactions.csv
        self.df = pd.DataFrame(
            {
                "transaction_id": [f"T{str(i).zfill(4)}" for i in range(1, 6)],
                "user_id": [101, 102, 101, 103, 104],
                "amount": [50.0, 75.0, 100.0, 125.0, 80.0],
                "fee": [1.0, 1.5, 2.0, 2.5, 1.0],
                "status": ["completed", "failed", "completed", "pending", "completed"],
                "timestamp": [
                    "2023-09-01 00:00:00",
                    "2023-09-01 01:00:00",
                    "2023-09-01 02:00:00",
                    "2023-09-01 03:00:00",
                    "2023-09-01 04:00:00",
                ],
            }
        )

        # Instantiate the full analytics engine with simulated ingestion
        self.engine = AnalyticsEngine(self.df)

    def test_run_all_analytics_returns_result_object(self):
        results = self.engine.run_all_analytics()
        self.assertIsInstance(results, AnalyticsResult)

        # Validate presence of expected fields
        self.assertTrue(hasattr(results, "metrics"))
        self.assertTrue(hasattr(results, "kpis"))
        self.assertIsInstance(results.metrics, dict)
        self.assertIsInstance(results.kpis, dict)

    def test_metrics_content(self):
        metrics = self.engine.metrics.calculate_all()
        self.assertIn("Total Revenue", metrics)
        self.assertAlmostEqual(metrics["Total Revenue"], 230.0)
        self.assertIn("Volume per User", metrics)
        self.assertEqual(metrics["Volume per User"][101], 2)

    def test_kpis_content(self):
        kpis = self.engine.kpis.evaluate_all()
        self.assertIn("Completion Rate", kpis)
        self.assertAlmostEqual(kpis["Completion Rate"], 3 / 5)
        self.assertIn("Failure Rate", kpis)
        self.assertAlmostEqual(kpis["Failure Rate"], 1 / 5)
        self.assertGreaterEqual(kpis["Unique Users"], 4)
        self.assertIn("Transactions Per Day", kpis)
        self.assertEqual(len(kpis["Transactions Per Day"]), 1)  # all on same date

    def test_kpi_transactions_per_day_keys(self):
        per_day = self.engine.kpis.transactions_per_day()
        dates = list(per_day.keys())
        self.assertTrue(
            all(isinstance(d, str) or hasattr(d, "isoformat") for d in dates)
        )
