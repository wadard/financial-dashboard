import dash_bootstrap_components as dbc
from dash import dcc, html

from data_ingestion.pipeline import DataPipeline


class DashboardLayout:
    def create(self, figures=None):
        # Initialize data pipeline and get user IDs and full data
        pipeline = DataPipeline("data/transactions.csv", engine="pandas")
        pipeline.ingest()
        pipeline.clean()

        user_ids = pipeline.get_user_ids()
        df = pipeline.get_data()

        dropdown_options = [{"label": str(uid), "value": uid} for uid in user_ids]

        revenue_fig = (
            figures.get("revenue_fig") if figures else dcc.Graph(id="revenue-chart")
        )
        kpi_table = figures.get("kpi_table") if figures else html.Div(id="kpi-table")

        return dbc.Container(
            [
                html.H2("Transaction Analytics", className="text-center my-4"),
                # Persist full cleaned data for callbacks
                dcc.Store(id="full-data", data=df.to_dict("records")),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Label("Select User"),
                                dcc.Dropdown(
                                    id="user-filter",
                                    options=dropdown_options,
                                    placeholder="Filter by User ID",
                                    clearable=True,
                                ),
                            ],
                            width=4,
                        )
                    ],
                    className="mb-4",
                ),
                dbc.Row(
                    [dbc.Col([revenue_fig], width=8), dbc.Col([kpi_table], width=4)]
                ),
            ],
            fluid=True,
        )
