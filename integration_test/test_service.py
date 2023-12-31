import os
import json
from pathlib import Path

import requests
from deepdiff import DeepDiff

url = os.getenv("SERVER_ADDRESS", "http://127.0.0.1:5010/predict")

parent_path = Path(__file__).resolve().parent

with open(parent_path / "sample_data.json", encoding="utf-8") as f:
    sample_data = json.load(f)

predictions = requests.post(url, json=sample_data, timeout=5).json()

## need to change to fixed format
## need to check the model is correct for sample data
predictions["diabetes chance"] = 1 if float(predictions["diabetes chance"]) > 50 else 0
predictions["model_version"] = "test"

expected_predictions = {"diabetes chance": 1, "model_version": "test"}

diff = DeepDiff(predictions, expected_predictions)
assert not diff
