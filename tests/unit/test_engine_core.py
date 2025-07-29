import unittest

import pandas as pd

from analytics_engine.core import AnalyticsEngine
from analytics_engine.result import AnalyticsResult


class TestAnalyticsEngine(unittest.TestCase):
    def setUp(self):
        # Create mock DataFrame with proper schema
        self.df = pd.DataFrame(
            {
                "transaction_id": ["T001", "T002", "T003"],
                "user_id": [101, 102, 103],
                "amount": [100.0, 150.0, 200.0],
                "fee": [2.0, 3.0, 5.0],
                "status": ["completed", "failed", "completed"],
                "timestamp": [
                    "2023-09-01 00:00:00",
                    "2023-09-01 01:00:00",
                    "2023-09-01 02:00:00",
                ],
            }
        )

        # ✅ Normalize a 'date' column expected by KPI logic
        self.df["date"] = pd.to_datetime(self.df["timestamp"]).dt.date

        self.engine = AnalyticsEngine(self.df)

    def test_metrics_output(self):
        metrics = self.engine.metrics.calculate_all()
        self.assertEqual(metrics["Total Revenue"], 300.0)
        self.assertEqual(metrics["Total Fees"], 7.0)
        self.assertIn(101, metrics["Volume per User"])
        self.assertTrue(metrics["Average Transaction"] > 0)

    def test_kpis_output(self):
        kpis = self.engine.kpis.evaluate_all()
        self.assertAlmostEqual(kpis["Failure Rate"], 1 / 3)
        self.assertAlmostEqual(kpis["Completion Rate"], 2 / 3)
        self.assertEqual(kpis["Unique Users"], 3)
        self.assertTrue(len(kpis["Transactions Per Day"]) >= 1)

    def test_combined_analytics(self):
        results = self.engine.run_all_analytics()
        self.assertIsInstance(results, AnalyticsResult)
        self.assertIn("Total Revenue", results.metrics)
        self.assertIn("Unique Users", results.kpis)
        self.assertGreater(results.metrics["Total Revenue"], 0)
        self.assertGreaterEqual(results.kpis["Unique Users"], 1)
