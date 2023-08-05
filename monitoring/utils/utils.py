# pylint: disable=invalid-name
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import select, create_engine
from utils.models import PredictionTable


def get_db_url():
    """
    Get the database url to interact with the database
    Returns:
        str: a string which indicates database url
    """
    DB_ADDRESS = os.getenv("DB_ADDRESS", "localhost")
    DATABASE_URL = f"postgresql://admin:example@{DB_ADDRESS}:5432/production"

    return DATABASE_URL


def get_serve_url():
    """
    Get the diabetes service url
    Returns:
        str: a string which indicates diabetes service url
    """
    SERVE_ADDRESS = os.getenv("SERVE_ADDRESS", "http://127.0.0.1:5010")
    SERVE_URL = f"{SERVE_ADDRESS}/predict"

    return SERVE_URL


def get_monitor_serve_url():
    """
    Get the monitoring service url
    Returns:
        str: a string which indicates monitoring service url
    """
    MONITOR_SERVE_ADDRESS = os.getenv("MONITOR_SERVE_ADDRESS", "http://127.0.0.1:5020")
    MONITOR_SERVE_URL = f"{MONITOR_SERVE_ADDRESS}/predict_monitor"

    return MONITOR_SERVE_URL


def get_reference_path():
    """
    Get the path for reference data
    Returns:
        str: A string which indicates the reference data
    """
    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/reference.parquet"

    return reference_path


def get_report_path():
    """
    Get the directory path for the reports
    Returns:
        str: A string which indicates the directory path for the reports
    """
    parent_path = Path(__file__).resolve().parent.parent
    report_path = os.path.join(parent_path, "reports")

    return report_path


def get_test_path():
    """
    Get the path for test data
    Returns:
        str: A string which indicates the test data
    """
    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/test.parquet"

    return reference_path


def get_valid_path():
    """
    Get the path for validation data
    Returns:
        str: A string which indicates the validation data
    """
    parent_path = Path(__file__).resolve().parent.parent
    reference_path = parent_path / "data/valid.parquet"

    return reference_path


def get_config_path():
    """
    Get the path for configuration data
    Returns:
        str: A string which indicates the configuration data
    """
    parent_path = Path(__file__).resolve().parent.parent
    config_path = parent_path / "config/config.yaml"

    return config_path


def get_reference_data():
    """
    Get the reference data
    Returns:
        pandas.Dataframe: the reference data
    """
    reference_path = get_reference_path()
    reference_data = pd.read_parquet(reference_path)
    reference_data.columns = reference_data.columns.str.lower()

    return reference_data


def get_current_data(window_size):
    """
    Get the current data
    Returns:
        pandas.Dataframe: the current data
    """
    DATABASE_URL = get_db_url()
    engine = create_engine(DATABASE_URL)
    with engine.connect() as db_connection:
        order = PredictionTable.timestamp.desc()
        query = select(PredictionTable).order_by(order).limit(window_size)
        current_data = pd.read_sql_query(sql=query, con=db_connection)
        current_data.drop("id", axis=1, inplace=True)

    return current_data
