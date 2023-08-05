import json

import requests

if __name__ == "__main__":
    with open("../data/raw/sample_data.json", "r", encoding="utf-8") as f_in:
        payloads = json.load(f_in)

    for payload in payloads:
        URL = "http://127.0.0.1:5010/predict"
        response = requests.post(URL, json=payload, timeout=5)
        print(f"For payload: {payload}")
        print(f"Json data is {response.json()}")
