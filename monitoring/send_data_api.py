import requests
import pandas as pd
import os
from time import sleep

from utils.utils import get_test_path, get_monitor_serve_url

if __name__ == "__main__":
    test_path = get_test_path()

    test_df = pd.read_parquet(test_path)
    test_df.columns = test_df.columns.str.lower()
    test_df.drop("diabetes", axis=1, inplace=True)

    test_data = test_df.to_dict(orient="records")

    monitor_serve_url = get_monitor_serve_url()

    for payload in test_data:
        resp = requests.post(monitor_serve_url, json=payload).json()
        sleep(1)
    