import logging
import os

import pytest

from analytics_engine.core import AnalyticsEngine
from analytics_engine.result import AnalyticsResult
from data_ingestion.pipeline import DataPipeline

# Set up logging for test traceability
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="module")
def csv_path():
    return os.path.abspath("data/transactions.csv")


@pytest.fixture(scope="module")
def cleaned_data(csv_path):
    df = DataPipeline(csv_path).run_pipeline()
    assert df is not None, "DataPipeline returned None — ingestion failed"
    return df


@pytest.fixture(scope="module")
def analytics_engine(cleaned_data):
    return AnalyticsEngine(cleaned_data)


def test_full_ingestion_to_analytics_flow(analytics_engine):
    results = analytics_engine.run_all_analytics()

    #  Validate structured object
    assert isinstance(results, AnalyticsResult), "Expected AnalyticsResult object"

    #  Core analytics checks
    assert "Total Revenue" in results.metrics, "Missing 'Total Revenue' in metrics"
    assert "Unique Users" in results.kpis, "Missing 'Unique Users' in KPIs"
    assert results.kpis["Unique Users"] >= 1, "Expected at least one unique user"
    assert results.metrics["Total Revenue"] > 0, "Revenue should be greater than 0"

    logger.info("Metrics result: %s", results.metrics)
    logger.info("KPIs result: %s", results.kpis)
