import mlflow
import os
from mlflow.tracking import MlflowClient
import pickle

def get_prod_run_id(tracking_uri, model_name, stage="Production"):
    client = MlflowClient(tracking_uri=tracking_uri)
    model_metadata = client.get_latest_versions(name=model_name, stages=[stage])[0]
    run_id = model_metadata.run_id

    return run_id

def get_model(run_id):
    logged_model = f'runs:/{run_id}/model'
    load_model = mlflow.pyfunc.load_model(logged_model)

    return load_model

def download_artifacts(run_id, artifact_path, dst_path):
    mlflow.artifacts.download_artifacts(
        run_id=run_id, 
        artifact_path=artifact_path, 
        dst_path=dst_path)

    return None

class ModelLoader:

    def __init__(self):
        home_directory = os.environ.get("HOME")
        self.mlflow_tracking_uri = os.getenv("MLFLOW_EXPERIMENT_URI", "http://0.0.0.0:5000")
        self.model_name = os.getenv("MODEL_NAME", "diabetes-classifier")
        self.experiment_name = os.getenv("EXPERIMENT_NAME", "training-pipeline")
        self.local_serve_folder = os.getenv("LOCAL_SERVER_FOLDER", f"{home_directory}/mnt/serve")

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        mlflow.set_experiment(self.experiment_name)

    def get_latest_run_id(self):

        run_id = get_prod_run_id(
            tracking_uri=self.mlflow_tracking_uri,
            model_name=self.model_name,
        )

        return run_id

    def load_model(self, run_id):

        load_model = get_model(run_id)

        return load_model


    def load_dv(self, run_id, artifact_path="artifact/preprocessor.b"):

        download_artifacts(
            run_id=run_id,
            artifact_path=artifact_path,
            dst_path=self.local_serve_folder
        )

        preprocessor_path = os.path.join(self.local_serve_folder, artifact_path)
        with open(preprocessor_path, 'rb') as f_in:
            dv = pickle.load(f_in)

        return dv