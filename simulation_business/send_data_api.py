import requests
import pandas as pd
import os
from time import sleep

test_df = pd.read_parquet("test.parquet")
test_data = test_df.to_dict(orient="records")

SERVE_ADDRESS = os.getenv("SERVE_ADDRESS", "http://127.0.0.1:5010")
full_address = f"{SERVE_ADDRESS}/predict"


for payload in test_data:
    resp = requests.post(full_address, json=payload).json()
    sleep(3)