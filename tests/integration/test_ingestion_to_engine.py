import logging
import os

import pytest

from analytics_engine.core import AnalyticsEngine
from analytics_engine.result import AnalyticsResult
from data_ingestion.pipeline import DataPipeline

# ✅ Set up logging for test traceability
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# 📁 Data files to test ingestion for
TEST_FILES = ["transactions.csv", "transactions.json", "transactions.parquet"]


@pytest.mark.parametrize("file_name", TEST_FILES)
def test_ingestion_to_analytics_engine(file_name):
    file_path = os.path.abspath(os.path.join("data", file_name))
    logger.info("Testing ingestion and analytics for file: %s", file_path)

    # 🚀 Run ingestion pipeline
    try:
        df = DataPipeline(file_path).run_pipeline()
    except Exception as e:
        pytest.fail(f"Pipeline ingestion failed for {file_name}: {e}")

    assert df is not None, f"DataFrame is None for {file_name}"
    assert not df.empty, f"DataFrame is empty for {file_name}"

    # 🎯 Run analytics engine
    engine = AnalyticsEngine(df)
    results = engine.run_all_analytics()

    assert isinstance(
        results, AnalyticsResult
    ), f"Expected AnalyticsResult object for {file_name}"
    assert (
        results.kpis.get("Unique Users", 0) >= 1
    ), f"Expected at least one unique user for {file_name}"
    assert (
        results.metrics.get("Total Revenue", 0) > 0
    ), f"Total Revenue should be positive for {file_name}"

    logger.info("✅ Metrics for %s: %s", file_name, results.metrics)
    logger.info("✅ KPIs for %s: %s", file_name, results.kpis)
