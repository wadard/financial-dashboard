import unittest

import pandas as pd
from dash import Dash

from dashboard.callbacks import DashboardCallbacks
from dashboard.figures import FigureBuilder
from dashboard.layout import DashboardLayout


class TestDashboardLayout(unittest.TestCase):
    def test_layout_structure(self):
        layout = DashboardLayout().create()
        self.assertIsNotNone(layout)
        self.assertGreater(len(layout.children), 0)

        layout_rows = [comp for comp in layout.children if hasattr(comp, "children")]

        found = any(
            hasattr(row, "children")
            and any(
                hasattr(col, "children")
                and any(getattr(el, "id", None) == "user-filter" for el in col.children)
                for col in row.children
            )
            for row in layout_rows
        )
        self.assertTrue(found)


class TestFigureBuilder(unittest.TestCase):
    def setUp(self):
        self.mock_data = pd.DataFrame(
            {
                "user_id": [101, 102],
                "amount": [1200.0, 900.5],
                "fee": [5.0, 3.5],
                "status": ["completed", "pending"],
                "date": pd.to_datetime(["2024-07-01", "2024-07-02"]),
                "transaction_id": [1, 2],
            }
        )
        self.builder = FigureBuilder(self.mock_data)

    def test_build_revenue_chart_returns_figure(self):
        dummy_data = {"Jan": 1000, "Feb": 1500, "Mar": 1200}
        fig = self.builder.build_revenue_chart(dummy_data)
        self.assertEqual(fig.layout.title.text, "Revenue by Month")
        self.assertEqual(len(fig.data), 1)
        self.assertEqual(fig.data[0].type, "bar")

    def test_build_kpi_table_structure(self):
        dummy_kpis = {"completion_rate": 0.75, "failure_rate": 0.25, "unique_users": 42}
        table_data = self.builder.build_kpi_table(dummy_kpis)
        self.assertEqual(len(table_data), 3)
        for row in table_data:
            self.assertIn("KPI", row)
            self.assertIn("Value", row)


class TestDashboardCallbacks(unittest.TestCase):
    def test_callback_registration_does_not_fail(self):
        app = Dash(__name__)
        mock_data = pd.DataFrame(
            {
                "user_id": [201, 202],
                "amount": [500.0, 600.0],
                "date": pd.to_datetime(["2024-07-03", "2024-07-04"]),
                "transaction_id": [10, 11],
            }
        )

        class TestableDashboardCallbacks(DashboardCallbacks):
            def __init__(self, mock_figures):
                self.figures = mock_figures

        try:
            callbacks = TestableDashboardCallbacks(FigureBuilder(mock_data))
            callbacks.register(app)
        except Exception as e:
            self.fail(f"Callback registration failed with error: {e}")
