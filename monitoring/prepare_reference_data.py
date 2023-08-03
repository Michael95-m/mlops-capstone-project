import requests
import pandas as pd
from utils.utils import get_serve_url, get_reference_path, get_valid_path
import logging
from tqdm import tqdm

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

def predict_endpoint(payload):
    SERVE_ADDRESS = get_serve_url()
    resp = requests.post(SERVE_ADDRESS, json=payload).json()
    diabetes_chance = float(resp["diabetes chance"])

    return diabetes_chance


def prepare_reference_data(valid_data):

    df = pd.read_parquet(valid_data)
    df.drop("diabetes", axis=1, inplace=True)

    logging.info("Preparing Reference data...")
    df['prediction'] = [predict_endpoint(data) for data in tqdm(df.to_dict(orient="records"))]

    reference_path = get_reference_path()
    df.to_parquet(reference_path, index=False)
    logging.info("Reference data is ready!!!")

if __name__ == "__main__":
    valid_path = get_valid_path()
    prepare_reference_data(valid_path)