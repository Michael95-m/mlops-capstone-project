# pylint: disable=import-error, invalid-name
import os
import logging

from flask import Flask, jsonify, request
from model_loader import ModelLoader
from model_service import ModelService

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

is_test_service = os.getenv("IS_TEST_SERVICE", None)

model_loader = ModelLoader(is_test_service=is_test_service)
logging.info("test_service: %s", is_test_service)
if is_test_service:
    run_id = "local"  ## just mock run_id
    model = model_loader.load_model_from_local()
    logging.info("Model Loaded from local")
    dv = model_loader.load_dv(run_id=run_id, is_test_service=True)
    logging.info("Dict Vectorizer loaded from local")
else:
    run_id = model_loader.get_latest_run_id()
    logging.info("Getting run_id....")
    model = model_loader.load_model(run_id)
    logging.info("Model Loaded from registry")
    dv = model_loader.load_dv(run_id)
    logging.info("Dict Vectorizer loaded from registry")


model_service = ModelService(model, dv)
logging.info("Model Service Prepared")

app = Flask("Diabetes-Prediction")


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """
    Prediction endpoint
    Returns:
        json: A json that contains prediction results
    """
    health = request.get_json()
    logging.info("\nExample payload is: %s", health)

    pred = model_service.predict(health)

    result = {"diabetes chance": f"{float(pred[0]) * 100:.2f}", "model_version": run_id}

    logging.info("Prediction result is %s\n", result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)
