from time import sleep

import pandas as pd
import requests
from utils.utils import get_test_path, get_monitor_serve_url

if __name__ == "__main__":
    test_path = get_test_path()

    test_df = pd.read_parquet(test_path)
    test_df.columns = test_df.columns.str.lower()
    test_df.drop("diabetes", axis=1, inplace=True)
    test_df = test_df.sample(frac=1).reset_index(drop=True)

    test_data = test_df.to_dict(orient="records")

    monitor_serve_url = get_monitor_serve_url()

    while True:
        print("start sending the data...")
        for payload in test_data:
            print("sending the data...")
            resp = requests.post(monitor_serve_url, json=payload, timeout=5).json()
            sleep(1)
