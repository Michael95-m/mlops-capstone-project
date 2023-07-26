class ModelService:

    def __init__(self, model, dv):
        self.model = model
        self.dv = dv

    def predict(self, dicts):
        X = self.dv.transform(dicts)
        y_pred = self.model.predict(X)

        return y_pred