import logging

import requests
from flask import Flask, jsonify, request, send_file
from utils.utils import get_serve_url, get_current_data, get_reference_data
from utils.report import (
    get_column_mapping,
    build_data_drift_report,
    build_target_drift_report,
)
from utils.save_db import save_predictions

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s"
)

SERVE_ADDRESS = get_serve_url()

app = Flask("Monitoring Service")


@app.route("/predict_monitor", methods=["POST"])
def predict_monitor():
    """
    Monitoring service that uses prediction service from diabetes_service
    and save the result into the database for monitoring
    Returns:
        json: A prediction result
    """
    data = request.get_json()
    result = requests.post(SERVE_ADDRESS, json=data, timeout=5).json()

    data["prediction"] = float(result["diabetes chance"])
    data["model_version"] = result["model_version"]

    save_predictions(data)

    logging.debug("Save data is: \n %s", data)

    return jsonify(data)


@app.route("/monitor_target_drift")
def monitor_target_drift():
    """
    Monitor target drift to the latest data inside the database
    Returns:
        Response: A target drift report
    """
    window_size = request.args.get("window_size", default=300, type=int)
    reference_df = get_reference_data()

    current_df = get_current_data(window_size=window_size)

    column_mapping = get_column_mapping()

    report_path = build_target_drift_report(
        current_data=current_df,
        reference_data=reference_df,
        column_mapping=column_mapping,
    )
    return send_file(report_path)


@app.route("/monitor_data_drift")
def monitor_data_drift():
    """
    Monitor data drift to the latest data inside the database
    Returns:
        Response: A data drift report
    """
    window_size = request.args.get("window_size", default=300, type=int)
    reference_df = get_reference_data()

    current_df = get_current_data(window_size=window_size)

    column_mapping = get_column_mapping()

    report_path = build_data_drift_report(
        current_data=current_df,
        reference_data=reference_df,
        column_mapping=column_mapping,
    )
    return send_file(report_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020, debug=False)
