# pylint: disable=invalid-name, redefined-outer-name, ungrouped-imports
import os
import pickle
import argparse
from pathlib import Path
from datetime import datetime

import yaml
import boto3
import mlflow
import optuna
import pandas as pd
import xgboost as xgb
from prefect import flow, task, get_run_logger
from prefect_aws import S3Bucket
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient
from sklearn.metrics import f1_score, recall_score, roc_auc_score, precision_score
from mlflow.models.signature import infer_signature
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_EXPERIMENT_URI", "http://127.0.0.1:5000")
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
experiment_name = os.getenv("EXPERIMENT_NAME", "training-pipeline")
mlflow.set_experiment(experiment_name)


def model_eval(y_true, y_pred, y_pred_prob):
    """
     Calculates evaluation metrics like auc, f1-score, precision and recall
    Args:
        y_true (numpy.ndarray): actual target value
        y_pred (numpy.ndarray): predicted value
        y_pred_prob (numpy.ndarray): probability of predicted value

    Returns:
        tuple(float, float, float, float): area under the curve, f1-score, precision, recall
    """
    auc = roc_auc_score(y_true, y_pred_prob)
    f1 = f1_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)

    return auc, f1, precision, recall


def f1_eval(y_pred, dtrain):
    """
    A function which will used inside optuna objective function
    Args:
        y_pred (numpy.ndarray): actual target value
        dtrain (): training data

    Returns:
        tuple: ("f1", f1_score)
    """
    y_true = dtrain.get_label()
    y_pred = (y_pred > 0.5).astype(int)
    return "f1", f1_score(y_true, y_pred)


def get_save_path():
    """
    Get the path for saving the raw data
    Returns:
        str: csv path
    """
    parent = Path(__file__).resolve().parent.parent
    file_path = "data/raw/diabetes_prediction_dataset.csv"
    data_path = parent / file_path
    return data_path


@task(retries=3)
def download_data_from_s3(s3, raw_data_path, BUCKET_NAME, OBJECT_NAME):
    """
    Download the raw data from s3
    Args:
        s3 (): s3 obj from boto3
        raw_data_path (str): the file path in local to save raw data
        BUCKET_NAME (str): name of the bucket from s3
        OBJECT_NAME (str): name of the object from s3
    """
    with open(raw_data_path, "wb") as f:
        s3.download_fileobj(BUCKET_NAME, OBJECT_NAME, f)


@task(retries=3)
def save_data_to_s3(s3, data_path, BUCKET_NAME):
    """
    Save data to s3 bucket
    Args:
        s3 (): s3 obj from boto3
        data_path (str): the file path to upload (eg. train.parquet etc.)
        BUCKET_NAME (str): name of the bucket from s3
    """
    data_path = Path(data_path)
    OBJECT_NAME = data_path.name

    with open(data_path, "rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME, OBJECT_NAME)


@task(retries=2, retry_delay_seconds=5)
def load_config(config_path):
    """
    Load the configuration path
    Args:
        config_path (str): A path where configuration file exists

    Returns:
        dict: the configuration
    """
    with open(config_path, "r", encoding="utf-8") as yaml_file:
        config = yaml.safe_load(yaml_file)

    return config


@task(retries=2, retry_delay_seconds=5)
def download_s3_data(s3_bucket_block, s3_folder_path, dataset_folder_path):
    """
    Download data from s3 data
    Args:
        s3_bucket_block (str): s3 bucket block from prefect
        s3_folder_path (str): a directory path inside s3 where the data is saved
        dataset_folder_path (str): a directory from local which will store the data
    """
    s3_bucket_block = S3Bucket.load(s3_bucket_block)
    s3_bucket_block.download_folder_to_path(
        from_folder=s3_folder_path,
        to_folder=dataset_folder_path,
    )


@task(retries=2, retry_delay_seconds=5)
def load_data(file_path):
    """
    Load the data from csv file
    Args:
        file_path (str): csv file path

    Returns:
        pandas.DataFrame:
    """
    df = pd.read_csv(file_path)

    return df


@task
def data_split(
    df,
    train_path,
    valid_path,
    test_path,
):
    """
    Train test split and these data will be saved in data/processed
    Args:
        df (pandas.DataFrame): all data read from csv file
        train_path (str): training csv file
        valid_path (str): valid csv file
        test_path (str): test csv file
    """
    train, test_val = train_test_split(df, test_size=0.25, random_state=42)
    valid, test = train_test_split(test_val, test_size=0.5, random_state=42)

    os.makedirs("data/processed", exist_ok=True)
    train.to_parquet(train_path, index=False)
    valid.to_parquet(valid_path, index=False)
    test.to_parquet(test_path, index=False)


def drop_features(train, valid, target_var):
    """
    Dropping features
    Args:
        train (pandas.DataFrame): training data
        valid (pandas.DataFrame): validation data
        target_var (str): target column

    Returns:
        tuple: (input_train, output_train, input_valid, output_valid)
    """
    x_train = train.drop(target_var, axis=1)
    y_train = train[target_var]
    x_valid = valid.drop(target_var, axis=1)
    y_valid = valid[target_var]

    return x_train, y_train, x_valid, y_valid


@task
def process_features(train_path, valid_path, target_var, save_dv=True):
    # pylint: disable=too-many-locals
    """
    Dropped and processed features by using DictVectorizer
    Args:
        train_path (str): training data
        valid_path (str): validation data
        target_var (str): testing data
        save_dv (bool, optional): save DictVectorizer or not. Defaults to True.

    Returns:
        tuple: (input_train, output_train, input_valid, output_valid)
    """

    training = pd.read_parquet(train_path)
    valid = pd.read_parquet(valid_path)

    x_train, y_train, x_valid, y_valid = drop_features(training, valid, target_var)

    dv = DictVectorizer()
    train_dict = x_train.to_dict(orient="records")
    val_dict = x_valid.to_dict(orient="records")
    X_train = dv.fit_transform(train_dict)
    X_valid = dv.transform(val_dict)

    if save_dv:
        os.makedirs("model", exist_ok=True)
        with open("model/preprocessor.b", "wb") as f:
            pickle.dump(dv, f)

    return X_train, y_train, X_valid, y_valid


@task
def hpo(X_train, y_train, X_valid, y_valid, n_trials=3):
    """
    Hyperparameter Optimization stage
    Args:
        X_train (pandas.DataFrame): input training data
        y_train (pandas.DataFrame): output training data
        X_valid (pandas.DataFrame): input validation data
        y_valid (pandas.DataFrame): output validation data
        n_trials (int, optional): number of trials. Defaults to 3.
    """
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dvalid = xgb.DMatrix(X_valid, label=y_valid)

    def objective(trial):
        with mlflow.start_run():
            params = {
                "objective": "binary:logistic",
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "eta": trial.suggest_float("eta", 0.01, 0.1),
                "lambda": trial.suggest_float("lambda", 0.0, 1.0),
                "alpha": trial.suggest_float("alpha", 0.0, 1.0),
            }

            mlflow.log_params(params)

            # Create xgboost Classifier with the hyperparameters
            model = xgb.train(
                params,
                dtrain,
                num_boost_round=500,
                evals=[(dvalid, "validation")],
                maximize=True,
                custom_metric=f1_eval,
                early_stopping_rounds=10,
                verbose_eval=500,
            )

            # Evaluate the model's performance on the validation set
            y_pred_prob = model.predict(dvalid)
            y_pred = (y_pred_prob > 0.5).astype(int)
            auc, f1, precision, recall = model_eval(y_valid, y_pred, y_pred_prob)

            metrics = {
                "auc": auc,
                "f1_score": f1,
                "precision": precision,
                "recall": recall,
            }
            signature = infer_signature(X_valid, y_pred)
            mlflow.log_metrics(metrics)
            mlflow.log_artifact("model/preprocessor.b", artifact_path="artifact")
            mlflow.xgboost.log_model(model, artifact_path="model", signature=signature)

        return f1

    # Create an Optuna study and optimize the objective function
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)


@task
def search_best_model(experiment_name):
    """
    Search the best model from all the trials in the experiment and its metadata

    Args:
        experiement_name (str): An experiment name used in the mlflow

    Returns:
        model_meta_data : metadata about best model in the model registry
    """
    experiment = client.get_experiment_by_name(experiment_name)
    best_model_meta_data = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        order_by=["metrics.f1_score DESC"],
        max_results=1,
    )[0]
    return best_model_meta_data


@task
def register_best_model(model_meta_data, model_name="diabetes-classifier"):
    """
    Register the best model from the training trials in the model registry
    Args:
        model_meta_data (): metadata about best model in the model registry
        model_name (str, optional): model name used in mlflow.
                                    Defaults to "diabetes-classifier".

    Returns:
        metadata about registered model
    """
    best_model_id = model_meta_data.info.run_id
    best_model_uri = f"runs:/{best_model_id}/model"

    reg_model_meta_data = mlflow.register_model(
        model_uri=best_model_uri, name=model_name
    )

    return reg_model_meta_data


def get_latest_version_model(model_name="diabetes-classifier", stage="production"):
    """
    Get the latest version of the production model in the model registry
    Args:
        model_name (str, optional): model name used in mlflow.
                                    Defaults to "diabetes-classifier".
        stage (str, optional): stage inside mlflow model registry. Defaults to "production".

    Returns:
        str: the latest version in the mlflow model registry
    """
    latest_version = client.get_latest_versions(name=model_name, stages=[stage])

    return latest_version


@task(name="Model Comparision")
def compare_models(prod_model, best_model_meta_data):
    """
    Comparison between the latest production model and the best model
    from the running experiment

    Returns:
        bool: A boolean value to register the best model or not
    """
    prod_model_run_id = prod_model[0].run_id
    prod_model_metrics_data = client.get_metric_history(
        prod_model_run_id, key="f1_score"
    )
    prod_model_metrics = prod_model_metrics_data[0].value

    best_model_metrics = best_model_meta_data.data.metrics["f1_score"]

    # True if current best model metrics is better than production metrics
    is_register = best_model_metrics > prod_model_metrics

    return is_register


@task
def transition_model_stage(
    reg_model_meta_data, model_name="diabetes-classifier", stage="production"
):
    """
    Transitioned the best model from the training trials to the production stage
    Args:
        reg_model_meta_data (): metadata about registered model
        model_name (str, optional): model name used in mlflow.
                                    Defaults to "diabetes-classifier".
        stage (str, optional): stage inside mlflow model registry. Defaults to "production".
    """
    client.transition_model_version_stage(
        name=model_name,
        version=reg_model_meta_data.version,
        stage=stage,
        archive_existing_versions=True,
    )

    date = datetime.today().date()
    client.update_model_version(
        name=model_name,
        version=reg_model_meta_data.version,
        description=f"The model version {reg_model_meta_data.version} "
        f"was transition to {stage} on {date}",
    )


@flow(name="training_pipeline")
def train_pipeline(experiment_name, use_s3, config_path):
    # pylint: disable=too-many-locals
    """
    Main training pipeline
    Args:
        experiement_name (str): An experiment name used in the mlflow
        config_path (str): A configuration path used in training
    """
    logger = get_run_logger()

    logger.info("Loading configuration")
    config = load_config(config_path)

    dataset_path = config["dataset_path"]
    train_path = config["train_path"]
    valid_path = config["valid_path"]
    test_path = config["test_path"]
    target_var = config["target_variable"]
    trials = config["trials"]

    logger.info("Getting information about s3")
    if use_s3:
        s3 = boto3.client("s3")
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        OBJECT_NAME = os.getenv("OBJECT_NAME")
        raw_data_path = get_save_path()

        logger.info("Download data from s3 bucket to local")
        download_data_from_s3(s3, raw_data_path, BUCKET_NAME, OBJECT_NAME)

    logger.info("Loading the data")
    df = load_data(dataset_path)

    logger.info("Splitting the data into train, valid and test")
    data_split(df, train_path, valid_path, test_path)

    if use_s3:
        logger.info("Saving the data (train, valid, test) to s3 bucket ")
        for data_path in [train_path, valid_path, test_path]:
            save_data_to_s3(s3, data_path, BUCKET_NAME)

    logger.info("Processing Features")
    X_train, y_train, X_valid, y_valid = process_features(
        train_path, valid_path, target_var
    )

    logger.info("Hyperparameter Tuning with XGBoost model")
    hpo(X_train, y_train, X_valid, y_valid, trials)

    logger.info("Searching the best model")
    best_model_meta_data = search_best_model(experiment_name)

    register_models = client.search_registered_models()

    if len(register_models) == 0:
        is_register = True
    else:
        prod_model = get_latest_version_model()
        is_register = compare_models(
            prod_model=prod_model, best_model_meta_data=best_model_meta_data
        )

    if is_register:
        logger.info("Registering the best model")
        reg_model_meta_data = register_best_model(model_meta_data=best_model_meta_data)

        logger.info("Transition the best model to the production stage")
        transition_model_stage(reg_model_meta_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training pipeline")
    parser.add_argument("--use_s3", action="store_true", help="Use data from AWS S3")
    args = parser.parse_args()

    use_s3 = args.use_s3

    train_pipeline(experiment_name, use_s3, config_path="config.yaml")
