import os
import tempfile
import unittest

import pandas as pd

try:
    import polars as pl

    HAS_POLARS = True
except ImportError:
    HAS_POLARS = False

try:
    from pyspark.sql import SparkSession

    HAS_SPARK = True
except ImportError:
    HAS_SPARK = False

from data_ingestion.pipeline import DataPipeline


class BasePipelineTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.df = pd.DataFrame(
            {
                "transaction_id": ["T001", "T002", "T003"],
                "user_id": [101, 102, None],
                "amount": [100.0, None, 50.0],
                "fee": [2.0, 1.0, None],
                "status": [" Completed ", "PENDING", "failed"],
            }
        )

    def tearDown(self):
        self.temp_dir.cleanup()


class TestPandasPipeline(BasePipelineTest):
    def save_and_test_ingest(self, ext):
        path = os.path.join(self.temp_dir.name, f"sample.{ext}")
        if ext == "csv":
            self.df.to_csv(path, index=False)
        elif ext == "json":
            self.df.to_json(path, orient="records")
        elif ext == "parquet":
            self.df.to_parquet(path, index=False)

        pipeline = DataPipeline(path, engine="pandas")
        df = pipeline.ingest()
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)

    def test_ingest_csv(self):
        self.save_and_test_ingest("csv")

    def test_ingest_json(self):
        self.save_and_test_ingest("json")

    def test_ingest_parquet(self):
        self.save_and_test_ingest("parquet")

    def test_clean(self):
        pipeline = DataPipeline("dummy", engine="pandas")
        pipeline.df = self.df.copy()
        cleaned = pipeline.clean()
        self.assertIsNotNone(cleaned)
        self.assertTrue(
            cleaned["status"].isin(["completed", "pending", "failed"]).all()
        )
        self.assertFalse(cleaned["user_id"].isnull().any())
        self.assertFalse(cleaned["amount"].isnull().any())

    def test_transform(self):
        df = pd.DataFrame(
            {
                "user_id": [101, 101, 102],
                "amount": [100.0, 200.0, 150.0],
                "fee": [2.0, 3.0, 5.0],
                "status": ["completed", "completed", "pending"],
            }
        )
        pipeline = DataPipeline("dummy", engine="pandas")
        pipeline.df = df
        result = pipeline.transform()
        self.assertEqual(result.iloc[0]["net_amount"], (100 - 2) + (200 - 3))

    def test_preview(self):
        pipeline = DataPipeline("dummy", engine="pandas")
        pipeline.df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        try:
            pipeline.preview()
        except Exception as e:
            self.fail(f"Preview failed with error: {e}")


@unittest.skipUnless(HAS_POLARS, "Polars not installed")
class TestPolarsPipeline(BasePipelineTest):
    def test_ingest_parquet(self):
        path = os.path.join(self.temp_dir.name, "sample.parquet")
        self.df.to_parquet(path, index=False)
        pipeline = DataPipeline(path, engine="polars")
        df = pipeline.ingest()
        self.assertIsNotNone(df)
        self.assertEqual(df.shape[0], 3)

    def test_clean_polars(self):
        pipeline = DataPipeline("dummy", engine="polars")
        df = pl.DataFrame(self.df.dropna())
        pipeline.df = df
        cleaned = pipeline.clean()
        self.assertGreaterEqual(cleaned.shape[0], 1)

    def test_transform_polars(self):
        df = pl.DataFrame(
            {
                "user_id": [101, 101, 102],
                "amount": [100.0, 200.0, 150.0],
                "fee": [2.0, 3.0, 5.0],
                "status": ["completed", "completed", "pending"],
            }
        )
        pipeline = DataPipeline("dummy", engine="polars")
        pipeline.df = df
        result = pipeline.transform()
        self.assertTrue("user_id" in result.columns)
        self.assertGreaterEqual(result.shape[0], 1)


@unittest.skipUnless(HAS_SPARK, "Spark not installed")
class TestSparkPipeline(BasePipelineTest):
    def test_ingest_json(self):
        path = os.path.join(self.temp_dir.name, "sample.json")
        self.df.to_json(path, orient="records")
        pipeline = DataPipeline(path, engine="spark")
        df = pipeline.ingest()
        self.assertIsNotNone(df)
        self.assertEqual(df.count(), 3)

    def test_clean_spark(self):
        spark = SparkSession.builder.master("local[*]").getOrCreate()
        df = spark.createDataFrame(self.df.dropna())
        pipeline = DataPipeline("dummy", engine="spark")
        pipeline.df = df
        cleaned = pipeline.clean()
        self.assertTrue(cleaned.count() >= 1)

    def test_transform_spark(self):
        spark = SparkSession.builder.master("local[*]").getOrCreate()
        df = spark.createDataFrame(
            pd.DataFrame(
                {
                    "user_id": [101, 101, 102],
                    "amount": [100.0, 200.0, 150.0],
                    "fee": [2.0, 3.0, 5.0],
                    "status": ["completed", "completed", "pending"],
                }
            )
        )
        pipeline = DataPipeline("dummy", engine="spark")
        pipeline.df = df
        result = pipeline.transform()
        self.assertTrue(result.count() == 1)
