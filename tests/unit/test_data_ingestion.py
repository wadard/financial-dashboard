# tests/unit/test_data_ingestion.py

import pandas as pd
from data_ingestion.data_ingestion import ingest_data


def test_ingest_data_valid_path(tmp_path):
    # Create a temporary CSV file
    test_file = tmp_path / "test.csv"
    test_file.write_text("Date,Amount,Category\n2025-07-01,-45.00,Groceries")

    df = ingest_data(str(test_file))
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.columns.tolist() == ["Date", "Amount", "Category"]


def test_ingest_data_missing_file():
    df = ingest_data("nonexistent.csv")
    assert df is None
