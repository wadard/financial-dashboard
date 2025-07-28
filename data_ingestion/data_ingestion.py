# data_ingestion/data_ingestion.py

import logging
import os
import pandas as pd

logging.basicConfig(level=logging.INFO)

def ingest_data(source_path: str) -> pd.DataFrame | None:
    """Ingests data from a source file path into a DataFrame."""
    if not os.path.exists(source_path):
        logging.error(f"Source file not found: {source_path}")
        return None

    logging.info(f"Ingesting data from: {source_path}")
    try:
        df = pd.read_csv(source_path)
        logging.info(f"Successfully ingested {len(df)} rows.")
        return df
    except Exception as e:
        logging.error(f"Failed to ingest data: {e}")
        return None

if __name__ == "__main__":
    # Adjusted path to point directly to the project root file
    df = ingest_data("transactions.csv")
    if df is not None:
        print(df.head())  # Preview the ingested data