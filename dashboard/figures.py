import pandas as pd
import plotly.express as px
from dash import dash_table, html


class FigureBuilder:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def revenue_by_month(self):
        monthly_revenue = (
            self.data.groupby(self.data["date"].dt.to_period("M"))
            .agg({"amount": "sum"})
            .reset_index()
        )
        monthly_revenue["date"] = monthly_revenue["date"].dt.to_timestamp()
        fig = px.bar(
            monthly_revenue,
            x="date",
            y="amount",
            title="Monthly Revenue",
            labels={"amount": "Total (£)", "date": "Month"},
            template="plotly_dark",
        )
        fig.update_traces(marker_color="#636EFA")
        fig.update_layout(margin=dict(t=50, l=40, r=40, b=40))
        return fig

    def build_revenue_chart(self, revenue_dict: dict):
        df = pd.DataFrame(list(revenue_dict.items()), columns=["Month", "Revenue"])
        fig = px.bar(
            df,
            x="Month",
            y="Revenue",
            title="Revenue by Month",
            labels={"Revenue": "Total (£)", "Month": "Month"},
            template="plotly_dark",
        )
        fig.update_traces(marker_color="#00CC96")
        fig.update_layout(margin=dict(t=40, l=40, r=40, b=40))
        return fig

    def kpi_summary(self, filtered_df=None):
        df = filtered_df if filtered_df is not None else self.data

        total_revenue = df["amount"].sum()
        avg_transaction = df["amount"].mean()
        num_users = df["user_id"].nunique()

        kpis = pd.DataFrame(
            {
                "Metric": ["Total Revenue (£)", "Avg. Transaction (£)", "Unique Users"],
                "Value": [
                    f"{total_revenue:,.2f}",
                    f"{avg_transaction:,.2f}",
                    str(num_users),
                ],
            }
        )

        table = dash_table.DataTable(
            data=kpis.to_dict("records"),
            columns=[{"name": i, "id": i} for i in kpis.columns],
            style_table={"width": "100%"},
            style_cell={
                "textAlign": "center",
                "padding": "10px",
                "fontWeight": "500",
                "fontFamily": "Arial",
                "fontSize": "14px",
            },
            style_header={"backgroundColor": "#1a1a1a", "color": "white"},
        )

        return html.Div(
            children=[html.H5("KPI Summary", className="text-center mb-3"), table]
        )

    def build_kpi_table(self, kpi_dict: dict):
        df = pd.DataFrame(
            [{"KPI": key, "Value": value} for key, value in kpi_dict.items()]
        )
        return df.to_dict("records")
