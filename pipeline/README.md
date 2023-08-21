## Training Pipeline

The training pipeline consists of the following steps.

1. Load configuration from *config.yaml*
2. Load the data from local or s3.
3. Splitting the data into train, test and valid.
4. Processing the features
5. Hyperparameter tuning with **optuna** library to find the best parameters of **XGBoost** model to find the best model.
6. After that, it will search the best model that has the highest **f1-score** from the experiments. If there is no registered model in the model registry, the best model will be transitioned into the **production stage**. If there is already a production model in the model registry, the **best model** from the **recent experiments** and the production model will be compared which one has got more **f1-score**. If the best model from recent experiment has more **f1-score**, it will be updated as the **production** model.

For loading the data, the data can be loaded from the local or loaded from s3. I don't like loading the data from s3 because it's not possible in real word if the data size is too big. I feel like loading the data from s3 is more realistic. But loading the data from local is easier one for now because there is no need to export the aws credentials.

#### Experiment Tracking example
<br>

![Experiment Tracking](../docs/mlflow_experiment_tracking.png)

#### Model Registry example
<br>

![Model Registry](../docs/model_registry.png)


**Warning:** If you choose to use the data loading with s3 and if you don't set the environment variables associated with aws credentials, you will get the error. For loading data from local, there is no need to set the environment variables.

## Deploying the training pipeline with prefect

This training workflow can be deployed with the **prefect** service. With prefect, the workflow can be scheduled and triggered via API. Deployment configuration about training pipeline can be seen at [here](../prefect.yaml). Deployment name is **deploy_train** and work pool name is **train-pool**

#### Prefect Workflow for training pipeline example
<br>

![Prefect Workflow for training pipeline](../docs/training_pipeline_prefect.png)
