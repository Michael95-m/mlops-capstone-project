# mlops-capstone-project

The project is still in progress. Some components are still needed to be implemented. You can see the complete system design below.

<img src="docs/system_design.png" width="500" height="300"><br>

## Training Pipeline


1. Install the library at the root level.

```bash
pip install --user pipenv
pipenv install
```

2. Setup the model's registry requirement with `make setup-model-registry`. Do it only for the first time running. For the next time, you don't need to do it.

3. Start mlflow server by docker compose.

```bash
docker compose -f docker-compose.registry.yaml up -d
```

4. Start the prefect server in terminal 1.
```bash
pipenv run prefect server start
```

5. Then run the training pipeline with this command.
```bash
python pipeline/training_pipeline.py
```

If you want to deploy the training pipeline and run with the schedule, follow the instructions below:

6. Deploy the work-flow named **deploy_train** and Create the work-pool named **train_pool**. **Warning:** This is only needed for the first time. If you rerun this flow again, you can skip this skip.
```bash
bash setup_prefect.sh
```

7. Start the work-pool in terminal 3. 
```bash
pipenv run prefect worker start --pool 'train-pool'
```

8. Run this deploynamed named **deploy_train** in terminal 4. 
```bash
pipenv run prefect deployment run 'training_pipeline/deploy_train'
```

## Model Serving

1. As the prerequisites, you need to up the mlflow server by running docker compose `docker compose -f docker-compose.registry.yaml up -d`. You must run **training pipeline** at least once to have the production model inside the model registry.

2. Then run the diabetes-prediction api service and input simulation service by running `docker compose -f docker-compose.serve.yaml up`. After running that, the input simulation service will continuously send the data to the api service. You can check the result in the command line.

## Model Monitoring

1. You need to up the services inside `docker-compose.registry.yaml` and `docker-compose.serve.yaml` as the prerequisites. This following command can be run to setup the services.
```shell
docker compose -f docker-compose.registry.yaml -f docker-compose.serve.yaml up -d
```

2. Then, you also need to run the services inside `docker-compose.monitoring.yaml`
```shell
docker compose -f docker-compose.monitoring.yaml up -d
```

3. After that, go to **monitoring** folder and  you have to create the table named **prediction_log** inside the database named **production**. 
```shell
cd monitoring
python create_db.py
```

4. Then you have to prepare reference data for monitoring by using the script named `prepare_reference_data.py`.
```shell
python prepare_reference_data.py
```

5. You have to make simulation about sending data to api by running this script.
```shell
python send_data_api.py
```

After that, you need to take some time to have the data inside prediction_log table inside the database.




