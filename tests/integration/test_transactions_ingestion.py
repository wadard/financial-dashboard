# File: tests/integration/test_transactions_ingestion.py

import os
import unittest

from data_ingestion.pipeline import DataPipeline

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")


class TestTransactionFiles(unittest.TestCase):
    def test_ingest_csv_file(self):
        path = os.path.join(DATA_DIR, "transactions.csv")
        pipeline = DataPipeline(engine="pandas", source_path=path)
        df = pipeline.ingest()
        self.assertFalse(df.empty)
        print("✅ CSV ingestion successful:", df.shape)

    def test_ingest_json_file(self):
        path = os.path.join(DATA_DIR, "transactions.json")
        pipeline = DataPipeline(engine="pandas", source_path=path)
        df = pipeline.ingest()
        self.assertFalse(df.empty)
        print("✅ JSON ingestion successful:", df.shape)

    def test_ingest_parquet_file(self):
        path = os.path.join(DATA_DIR, "transactions.parquet")
        pipeline = DataPipeline(engine="pandas", source_path=path)
        df = pipeline.ingest()
        self.assertFalse(df.empty)
        print("✅ Parquet ingestion successful:", df.shape)
