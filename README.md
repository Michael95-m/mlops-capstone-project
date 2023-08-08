# mlops-capstone-project

You can see the complete system design below.

![drawing|4526x2790](docs/system_design.png)<br>

## Training Pipeline

### 1. Install the library at the root level.

```bash
pip install --user pipenv
pipenv install
```

### 2. Setup model's registry requirments.

Run `make setup-model-registry`. Do it only for the first time running and yon don't need to do it for next time.

### 3. Start prefect server.

Start the prefect server to run the training pipeline. Start by `make prefect-server-start`.

### 4. Run the training pipeline.

Run the training pipeline which train **XGBoost** model and registry the best model in the experiment in the **mlflow model registry**. You can run by `make run-training-pipeline`.

### 5. Deploy the training pipeline in prefect

You need to create the workpool named **train-pool** by using `make create-workpool`.
After that, you can deploy the training pipeline by using `make deploy-training-pipeline`.

### 6. Run the deployed training pipeline 



