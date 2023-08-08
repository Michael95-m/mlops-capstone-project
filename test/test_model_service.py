# pylint: disable=too-few-public-methods, invalid-name
import json
from pathlib import Path

from deployment.model_service import ModelService


class ModelMock:
    """
    Just mocking the function of the xgboost model
    """

    def __init__(self, value):
        self.value = value

    def predict(self, X):
        """
        Mock predict function
        Args:
            X (dict): A sample data in dictionary format

        Returns:
            list: A list of the values of X with the size of the dictionary
        """
        n = len(X)
        return [self.value] * n


class DvMock:
    """
    Just mocking the dictvectorizer from scikit-learn
    """

    def transform(self, value):
        """
        Mock transform function
        Args:
            value (dict): A sample data in dictionary format

        Returns:
            dict: A sample data in dictionary format
        """
        return value


def read_data(file):
    """
    Reading sample data from json file
    Args:
        file (str): sample_data.json.

    Returns:
        dict: A sample data in dictionary form
    """

    test_directory = Path(__file__).parent

    with open(test_directory / file, "r", encoding="utf-8") as f:
        sample_data = json.load(f)

    return sample_data[0]


def get_model_service():
    """
    Preparation of model service object
    Returns:
        ModelService: A object from the ModelService
    """

    model_mock = ModelMock(10.0)
    dv_mock = DvMock()

    return ModelService(model_mock, dv_mock)


def test_predict():
    """
    test case for prediction function of ModelService class
    """
    model_service = get_model_service()
    sample_data = read_data("sample_data.json")

    y_pred = model_service.predict(sample_data)[0]
    expected_y_pred = 10

    assert y_pred == expected_y_pred
