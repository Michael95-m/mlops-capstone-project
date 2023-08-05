# pylint: disable=import-error
import logging

from flask import Flask, jsonify, request
from model_loader import ModelLoader
from model_service import ModelService

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

model_loader = ModelLoader()
run_id = model_loader.get_latest_run_id()
logging.info("Getting run_id....")
model = model_loader.load_model(run_id)
logging.info("Model Loaded")
dv = model_loader.load_dv(run_id)
logging.info("Dict Vectorizer loaded")

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
    logging.debug("\nExample payload is: %s", health)

    pred = model_service.predict(health)

    result = {"diabetes chance": f"{float(pred[0]) * 100:.2f}", "model_version": run_id}

    logging.debug("Prediction result is %s\n", result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=False)
