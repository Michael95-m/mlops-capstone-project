import pandas as pd
from sqlalchemy import create_engine, select

from utils.models import PredictionTable
from pathlib import Path
import os

def get_db_url():

    DB_ADDRESS = os.getenv("DB_ADDRESS", "localhost")
    DATABASE_URL = f'postgresql://admin:example@{DB_ADDRESS}:5432/production'

    return DATABASE_URL

def get_serve_url():

    SERVE_ADDRESS = os.getenv("SERVE_ADDRESS", "http://127.0.0.1:5010")
    SERVE_URL = f"{SERVE_ADDRESS}/predict"

    return SERVE_URL

def get_monitor_serve_url():

    MONITOR_SERVE_ADDRESS = os.getenv("MONITOR_SERVE_ADDRESS", "http://127.0.0.1:5020")
    MONITOR_SERVE_URL = f"{MONITOR_SERVE_ADDRESS}/predict_monitor"

    return MONITOR_SERVE_URL

def get_reference_path():

    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/reference.parquet"

    return reference_path

def get_report_path():

    parent_path = Path(__file__).resolve().parent.parent
    report_path = os.path.join(parent_path, "reports")

    return report_path

def get_test_path():

    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/test.parquet"

    return reference_path

def get_valid_path():

    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/valid.parquet"

    return reference_path

def get_config_path():

    parent_path = Path(__file__).resolve().parent.parent
    config_path = parent_path / "config/config.yaml"

    return config_path


def get_reference_data():

    reference_path = get_reference_path()
    reference_data = pd.read_parquet(reference_path)
    reference_data.columns = reference_data.columns.str.lower()

    return reference_data

def get_current_data(window_size):

    DATABASE_URL = get_db_url()
    engine = create_engine(DATABASE_URL)
    with engine.connect() as db_connection:
        order = PredictionTable.timestamp.desc()
        query = (
            select(PredictionTable).order_by(order)
            .limit(window_size)
        )
        current_data = pd.read_sql_query(
            sql=query,
            con=db_connection
        )
        current_data.drop('id', axis=1, inplace=True)

    return current_data