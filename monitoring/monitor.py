from flask import Flask, request, jsonify, send_file
import requests
import logging

from utils.save_db import save_predictions
from utils.utils import (
    get_current_data, 
    get_reference_data,
    get_serve_url
)
from utils.report import (
    get_column_mapping, 
    build_data_drift_report, 
    build_target_drift_report
)

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")

SERVE_ADDRESS = get_serve_url()

app = Flask("Monitoring Service")


@app.route("/predict_monitor", methods=["POST"])
def predict_monitor():
    data = request.get_json()
    result = requests.post(SERVE_ADDRESS, json=data).json()

    data["prediction"] = float(result["diabetes chance"])
    data["model_version"] = result["model_version"]

    save_predictions(data)

    logging.debug(f"Save data is: \n {data}")

    return jsonify(data)

@app.route("/monitor_target_drift")
def monitor_target_drift():

    window_size = request.args.get('window_size', default=300, type=int)
    reference_df = get_reference_data()

    current_df = get_current_data(window_size=window_size)

    column_mapping = get_column_mapping()

    report_path = build_target_drift_report(
    current_data=current_df,
    reference_data=reference_df,
    column_mapping=column_mapping
    )
    return send_file(report_path)

@app.route("/monitor_data_drift")
def monitor_data_drift():

    window_size = request.args.get('window_size', default=300, type=int)
    reference_df = get_reference_data()

    current_df = get_current_data(window_size=window_size)

    column_mapping = get_column_mapping()

    report_path = build_data_drift_report(
    current_data=current_df,
    reference_data=reference_df,
    column_mapping=column_mapping
    )
    return send_file(report_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=False)