import os

import pytest

from analytics_engine.core import AnalyticsEngine
from dashboard.figures import FigureBuilder
from data_ingestion.pipeline import DataPipeline

TEST_FILES = ["transactions.csv", "transactions.json", "transactions.parquet"]


@pytest.mark.parametrize("file_name", TEST_FILES)
def test_full_pipeline_to_dashboard_figures(file_name):
    file_path = os.path.abspath(os.path.join("data", file_name))

    # Step 1: Ingest data
    df = DataPipeline(file_path).run_pipeline()
    assert df is not None and not df.empty, f"Failed ingesting {file_name}"

    # Step 2: Run analytics
    engine = AnalyticsEngine(df)
    results = engine.run_all_analytics()
    assert results.kpis, f"KPI extraction failed for {file_name}"
    assert results.metrics, f"Metric extraction failed for {file_name}"

    # Step 3: Build dashboard figures using analytics results
    builder = FigureBuilder(data=results.metrics)
    revenue_fig = builder.build_revenue_chart(results.metrics)
    kpi_table = builder.build_kpi_table(results.kpis)

    # Step 4: Validate dashboard outputs

    # Validate revenue figure
    assert revenue_fig.layout.title.text == "Revenue by Month", "Chart title mismatch"
    assert len(revenue_fig.data) >= 1, "No data series found in revenue chart"
    assert revenue_fig.data[0].type in [
        "bar",
        "line",
    ], f"Unexpected chart type: {revenue_fig.data[0].type}"

    # Validate KPI table structure and content (expects list[dict])
    assert isinstance(kpi_table, list), f"Expected list but got {type(kpi_table)}"
    assert all(
        isinstance(row, dict) for row in kpi_table
    ), "KPI table rows must be dictionaries"
    assert all(
        "KPI" in row and "Value" in row for row in kpi_table
    ), "Missing keys in KPI rows"
    assert len(kpi_table) >= 1, f"No KPI rows found for {file_name}"
