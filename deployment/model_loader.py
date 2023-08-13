import os
import pickle
from pathlib import Path

import mlflow
from mlflow.tracking import MlflowClient


def get_prod_run_id(tracking_uri, model_name, stage="Production"):
    """
    get the latest production run_id from model registry
    Args:
        tracking_uri (str): tracking uri of mlflow server
        model_name (str): experiment_name
        stage (str, optional): Staging or Production. Defaults to "Production".

    Returns:
        str: run_id of the latest production model
    """
    client = MlflowClient(tracking_uri=tracking_uri)
    model_metadata = client.get_latest_versions(name=model_name, stages=[stage])[0]
    run_id = model_metadata.run_id

    return run_id


def get_model(run_id):
    """
    load the model from the model registry
    Args:
        run_id (str): run_id of the model
    Returns:
        PyFuncModel: loaded model from the model registry
    """

    logged_model = f"runs:/{run_id}/model"

    load_model = mlflow.pyfunc.load_model(logged_model)

    return load_model


def get_model_from_local():
    """
    load the model from local path
    Returns:
        PyFuncModel: loaded model from the local
    """

    directory = Path(__file__).resolve().parent
    logged_model = directory / "model"

    load_model = mlflow.pyfunc.load_model(logged_model)

    return load_model


def download_artifacts(run_id, artifact_path, dst_path):
    """
    Download the artifact(dict vectorizer) from the model registry
    Args:
        run_id (str): run_id of the model
        artifact_path (str): artifact path in the model registry
        dst_path (str): destination path in the local
    """
    mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path=artifact_path, dst_path=dst_path
    )


class ModelLoader:
    """
    This class will load the Dictvectorizer and the model that will be used
    to predict
    Args:
        is_test_service (bool): check integration test or not
    """

    def __init__(self, is_test_service):
        self.mlflow_tracking_uri = os.getenv(
            "MLFLOW_EXPERIMENT_URI", "http://0.0.0.0:5000"
        )
        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        if not is_test_service:
            home_directory = os.environ.get("HOME")
            self.model_name = os.getenv("MODEL_NAME", "diabetes-classifier")
            self.experiment_name = os.getenv("EXPERIMENT_NAME", "training-pipeline")
            self.local_serve_folder = os.getenv(
                "LOCAL_SERVER_FOLDER", f"{home_directory}/mnt/serve"
            )
            mlflow.set_experiment(self.experiment_name)

    def get_latest_run_id(self):
        """
        Get the run_id of the production model inside the model registry.
        Returns:
            str: run_id of the latest production model
        """
        run_id = get_prod_run_id(
            tracking_uri=self.mlflow_tracking_uri,
            model_name=self.model_name,
        )

        return run_id

    def load_model(self, run_id):
        """
        Load the model from the model registry.
        Args:
            run_id (str): run_id of the model

        Returns:
            PyFuncModel: loaded model from the model registry
        """
        load_model = get_model(run_id)

        return load_model

    def load_model_from_local(self):
        """
        Load the model from the model registry.

        Returns:
            PyFuncModel: loaded model from the model registry
        """
        load_model = get_model_from_local()

        return load_model

    def load_dv(
        self, run_id, artifact_path="artifact/preprocessor.b", is_test_service=False
    ):
        # pylint: disable=invalid-name
        """
        Download the dictvectorizer and load it from the local path.
        Args:
            run_id (str): run_id of the model
            artifact_path (str, optional):  artifact path in the model registry.
                                            Defaults to "artifact/preprocessor.b".
        Returns:
            DictVectorizer: A dictVectorizer
        """
        if not is_test_service:
            download_artifacts(
                run_id=run_id,
                artifact_path=artifact_path,
                dst_path=self.local_serve_folder,
            )

            preprocessor_path = os.path.join(self.local_serve_folder, artifact_path)
        else:
            directory = Path(__file__).resolve().parent
            preprocessor_path = directory / artifact_path

        with open(preprocessor_path, "rb") as f_in:
            dv = pickle.load(f_in)

        return dv
