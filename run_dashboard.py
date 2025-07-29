import logging

import plotly.express as px
import plotly.graph_objects as go
from dash import Dash
from dash.dependencies import Input, Output
from dotenv import load_dotenv

from analytics_engine.core import AnalyticsEngine
from dashboard.figures import FigureBuilder
from dashboard.layout import DashboardLayout
from data_ingestion.pipeline import DataPipeline

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Optional for deployment

# Ingest and clean data once for layout population and dropdown setup
DATA_PATH = "data/transactions.csv"
pipeline = DataPipeline(source_path=DATA_PATH, engine="pandas")
df = pipeline.run_pipeline()

if df is None or df.empty:
    raise ValueError("No valid data available for dashboard rendering.")

# Run analytics
analytics = AnalyticsEngine(df)
results = analytics.run_all_analytics()

# Compose layout
app.layout = DashboardLayout().create()


# Callback: Filter KPI table based on selected user
@app.callback(Output("kpi-table", "children"), Input("user-filter", "value"))
def update_kpi_table(selected_user):
    pipeline = DataPipeline(source_path="data/transactions.csv", engine="pandas")
    df = pipeline.run_pipeline()

    if selected_user:
        df = df[df["user_id"] == selected_user]

    builder = FigureBuilder(df)
    return builder.kpi_summary().children


# Callback: Display scatter plot for revenue data
@app.callback(Output("revenue-chart", "figure"), Input("user-filter", "value"))
def update_revenue_chart(selected_user):
    pipeline = DataPipeline(source_path="data/transactions.csv", engine="pandas")
    df = pipeline.run_pipeline()

    if selected_user:
        df = df[df["user_id"] == selected_user]

    if df.empty:
        return go.Figure().update_layout(
            title="No data available",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[
                {
                    "text": "No data found for this user",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 16},
                }
            ],
        )

    fig = px.scatter(
        df,
        x="transaction_id",  # Confirm this column exists and is appropriate
        y="amount",  # Confirm this column matches your schema
        title=(
            f"Transactions for User {selected_user}"
            if selected_user
            else "All Transactions"
        ),
        color_discrete_sequence=["#636EFA"],
        hover_data=["user_id", "transaction_id"],
    )

    fig.update_traces(marker=dict(size=6, opacity=0.6))
    fig.update_layout(margin=dict(t=40, l=20, r=20, b=40))

    return fig


# Launch the app
if __name__ == "__main__":
    app.run(debug=True)
