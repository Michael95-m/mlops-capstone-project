import requests
import json 

with open("../data/raw/sample_data.json") as f_in:
    payloads = json.load(f_in)

for payload in payloads:
    url = "http://127.0.0.1:5010/predict"
    response = requests.post(url, json=payload)
    print(f"For payload: {payload}")
    print(f"Json data is {response.json()}")
