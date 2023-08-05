# pylint: disable=invalid-name
import logging

import pandas as pd
import requests
from tqdm import tqdm
from utils.utils import get_serve_url, get_valid_path, get_reference_path

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


def predict_endpoint(payload):
    """
    Predict the payload data which uses the prediction service
    Args:
        payload (dict): a sample data

    Returns:
        float: A chance that can be diabetes
    """
    serve_address = get_serve_url()
    resp = requests.post(serve_address, json=payload, timeout=5).json()
    diabetes_chance = float(resp["diabetes chance"])

    return diabetes_chance


def prepare_reference_data():
    """
    Prepare the validation data as the reference data
    by make prediction
    """
    valid_path = get_valid_path()

    df = pd.read_parquet(valid_path)
    df.drop("diabetes", axis=1, inplace=True)

    logging.info("Preparing Reference data...")
    df["prediction"] = [
        predict_endpoint(data) for data in tqdm(df.to_dict(orient="records"))
    ]

    reference_path = get_reference_path()
    df.to_parquet(reference_path, index=False)
    logging.info("Reference data is ready!!!")


if __name__ == "__main__":
    prepare_reference_data()
