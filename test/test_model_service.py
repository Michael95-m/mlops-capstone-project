from unittest.mock import MagicMock

import pytest

from deployment.model_service import ModelService

# Sample input data for testing
sample_data = [{"feature1": 1.5, "feature2": 2.0}, {"feature1": 3.0, "feature2": 4.5}]


# Mocking the model and dv objects
@pytest.fixture
def model_service():
    """
    Return the ModelService object which use the mock_model and mock_dv
    """
    # Mock the model and dv objects
    mock_model = MagicMock()
    mock_dv = MagicMock()

    # Return ModelService with mocked model and dv
    return ModelService(mock_model, mock_dv)


def test_predict(model_service):
    """
    Test the predict function from ModelService object
    """
    # Sample expected output from the model
    expected_output = [0, 1]

    # Mock the transform method of dv
    model_service.dv.transform.return_value = [[1.5, 2.0], [3.0, 4.5]]

    # Mock the predict method of the model
    model_service.model.predict.return_value = expected_output

    # Call the predict method of ModelService with sample data
    result = model_service.predict(sample_data)

    # Assert the result is as expected
    assert result == expected_output

    # Assert the dv.transform method is called with the sample data
    model_service.dv.transform.assert_called_once_with(sample_data)

    # Assert the model.predict method is called with the transformed data
    model_service.model.predict.assert_called_once_with([[1.5, 2.0], [3.0, 4.5]])
