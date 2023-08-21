# Deployment

In deployment stage, the **xgboost model** and the **Dictvectorizer** will be loaded from the **mlflow registry**. That's why there is at least one production model in the model registry.

For test purposes like integration testing, there are already artifacts in the folder and they will be loaded to use. But for serving purpose, the artifacts will be loaded from the model registry to serve with the latest production model.

**Flask** and **gunicorn** are used to make a deployable HTTP api and the models, codes and dependencies are packaged as **docker service**.
