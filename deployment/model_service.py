class ModelService:
    # pylint: disable=too-few-public-methods, invalid-name
    """
    A class for model service
    """

    def __init__(self, model, dv):
        self.model = model
        self.dv = dv

    def predict(self, dicts):
        """
        Predict the data in the dictionary
        Args:
            dicts (dict): A dictionary that contains input features

        Returns:
            numpy.ndarray: Predicted data in the form of numpy array
        """
        X = self.dv.transform(dicts)
        y_pred = self.model.predict(X)

        return y_pred
