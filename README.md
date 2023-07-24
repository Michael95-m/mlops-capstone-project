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

4. 