import pandas as pd
from dash import Input, Output

from analytics_engine.core import AnalyticsEngine
from dashboard.figures import FigureBuilder


class DashboardCallbacks:
    def __init__(self):
        self.figures = FigureBuilder()

    def register(self, app):
        @app.callback(
            Output("revenue-chart", "figure"),
            Output("kpi-table", "children"),
            Input("user-filter", "value"),
        )
        def update_dashboard(selected_user):
            df = pd.read_csv("data/transactions.csv")
            if selected_user:
                df = df[df["user_id"] == selected_user]

            engine = AnalyticsEngine(df)
            results = engine.run_all_analytics()

            revenue_figure = self.figures.build_revenue_chart(
                results.metrics.get("revenue", {})
            )
            kpi_table = self.figures.build_kpi_table(results.kpis)

            return revenue_figure, kpi_table
