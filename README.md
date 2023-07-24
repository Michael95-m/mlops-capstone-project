# mlops-capstone-project

This is just a scratch (not final readme).

## Training Pipeline


1. Install the library at the root level.

```bash
pip install --user pipenv
pipenv install
```

2. Start mlflow server in termianl 1.

```bash
pipenv run mlflow server --backend-store-uri sqlite:///backend.db
```

3. Start the prefect server in terminal 2.
```bash
pipenv run prefect server start
```

4. Deploy the work-flow named **deploy_train** and Create the work-pool named **train_pool**. **Warning:** This is only needed for the first time. If you rerun this flow again, you can skip this skip.
```bash
pipenv shell
bash setup_prefect.sh
```

5. Start the work-pool in terminal 3. 
```bash
pipenv run prefect worker start --pool 'train-pool'
```

6. Run this deploynamed named **deploy_train** in terminal 4. 
```bash
pipenv run prefect deployment run 'training_pipeline/deploy_train'
```

