# data_ingestion/pipeline.py

import logging
import os

import pandas as pd

logging.basicConfig(level=logging.INFO)


class DataPipeline:
    def __init__(self, source_path: str, engine: str = "pandas"):
        self.source_path = source_path
        self.engine = engine
        self.df = None

    def ingest(self):
        if not os.path.exists(self.source_path):
            logging.error(f"Source file not found: {self.source_path}")
            return None

        ext = os.path.splitext(self.source_path)[-1].lower()
        logging.info(
            f"Ingesting data from '{self.source_path}' using engine '{self.engine}'"
        )

        try:
            if self.engine == "pandas":
                if ext == ".csv":
                    self.df = pd.read_csv(self.source_path)
                elif ext == ".json":
                    self.df = pd.read_json(self.source_path)
                elif ext == ".parquet":
                    self.df = pd.read_parquet(self.source_path)

            elif self.engine == "polars":
                import polars as pl

                if ext == ".csv":
                    self.df = pl.read_csv(self.source_path)
                elif ext == ".json":
                    self.df = pl.read_json(self.source_path)
                elif ext == ".parquet":
                    self.df = pl.read_parquet(self.source_path)

            elif self.engine == "spark":
                from pyspark.sql import SparkSession

                spark = SparkSession.builder.appName("DataPipeline").getOrCreate()
                if ext == ".csv":
                    self.df = spark.read.csv(
                        self.source_path, header=True, inferSchema=True
                    )
                elif ext == ".json":
                    self.df = spark.read.json(self.source_path)
                elif ext == ".parquet":
                    self.df = spark.read.parquet(self.source_path)

            else:
                logging.error(f"Unsupported engine: {self.engine}")
                return None

        except Exception as e:
            logging.error(f"Failed to ingest data: {e}")
            return None

        return self.df

    def clean(self):
        if self.df is None:
            logging.warning("No data to clean.")
            return None

        logging.info(f"Cleaning data using engine: {self.engine}")
        try:
            if self.engine == "pandas":
                self.df = self.df.dropna(subset=["amount", "user_id"])
                self.df["amount"] = pd.to_numeric(self.df["amount"], errors="coerce")
                self.df["fee"] = pd.to_numeric(self.df["fee"], errors="coerce")
                self.df["status"] = self.df["status"].str.strip().str.lower()
                self.df.drop_duplicates(inplace=True)

            elif self.engine == "polars":
                import polars as pl

                self.df = self.df.drop_nulls()
                self.df = self.df.with_columns(
                    [
                        pl.col("amount").cast(pl.Float64),
                        pl.col("fee").cast(pl.Float64),
                        pl.col("status").str.strip_chars().str.to_lowercase(),
                    ]
                )
                self.df = self.df.unique()

            elif self.engine == "spark":
                from pyspark.sql.functions import col, lower, trim

                self.df = self.df.dropna(subset=["amount", "user_id"])
                self.df = self.df.withColumn("amount", col("amount").cast("double"))
                self.df = self.df.withColumn("fee", col("fee").cast("double"))
                self.df = self.df.withColumn("status", lower(trim(col("status"))))
                self.df = self.df.dropDuplicates()

        except Exception as e:
            logging.error(f"Failed to clean data: {e}")

        return self.df

    def transform(self):
        if self.df is None:
            logging.warning("No data to transform.")
            return None

        logging.info(f"Transforming data using engine: {self.engine}")
        try:
            if self.engine == "pandas":
                self.df["net_amount"] = self.df["amount"] - self.df["fee"]
                return (
                    self.df[self.df["status"] == "completed"]
                    .groupby("user_id")["net_amount"]
                    .sum()
                    .reset_index()
                )

            elif self.engine == "polars":
                import polars as pl

                self.df = self.df.with_columns(
                    [(pl.col("amount") - pl.col("fee")).alias("net_amount")]
                )
                self.df = self.df.filter(pl.col("status") == "completed")
                return (
                    self.df.groupby("user_id")
                    .agg(pl.sum("net_amount"))
                    .rename({"net_amount_sum": "net_amount"})
                )

            elif self.engine == "spark":
                from pyspark.sql.functions import col
                from pyspark.sql.functions import sum as spark_sum

                self.df = self.df.withColumn("net_amount", col("amount") - col("fee"))
                filtered_df = self.df.filter(col("status") == "completed")
                return filtered_df.groupBy("user_id").agg(
                    spark_sum("net_amount").alias("net_amount")
                )

        except Exception as e:
            logging.error(f"Failed to transform data: {e}")
            return None

    def preview(self, df=None):
        df_to_show = df if df is not None else self.df
        if df_to_show is None:
            logging.warning("No data to preview.")
            return

        try:
            print(df_to_show.head())
        except AttributeError:
            df_to_show.show()  # Spark fallback


if __name__ == "__main__":
    pipeline = DataPipeline("transactions.csv", engine="pandas")
    pipeline.ingest()
    pipeline.clean()
    summary = pipeline.transform()
    logging.info("Final Summary Preview:")
    pipeline.preview(summary)
