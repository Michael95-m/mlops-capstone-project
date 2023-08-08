MLFLOW_TRACKING_DIRECTORY := $(HOME)/mnt/mlruns

export MLFLOW_TRACKING_DIRECTORY

setup-model-registry:
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/tracking
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	mkdir -p ${HOME}/mnt/serve
	docker compose up --build -d mlflow_server

reset-model-registry:
	docker compose down -v mlflow_server
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/tracking
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	rm -rf ${HOME}/mnt/serve

start-mlflow-server:
	docker compose up -d mlflow_server

prefect-server-start:
	pipenv run prefect server start

run-training-pipeline:
	pipenv run python pipeline/training_pipeline.py

create-workpool:
	pipenv run prefect work-pool create --type process train-pool


deploy-training-pipeline: 
	pipenv run prefect deploy -n deploy_train

start-worker:
	pipenv run prefect worker start --pool 'train-pool'

run-deployed-training-pipeline:
	pipenv run prefect deployment run 'training_pipeline/deploy_train'

start-diabetes-service:
	docker compose up -d diabetes_service

start-all-services:
	docker compose up -d

create-db:
	pipenv run python monitoring/create_db.py

reset-db:
	pipenv run python monitoring/drop_db.py

send-data-monitoring-api:
	pipenv shell python monitoring/send_data_api.py

stop-services:
	docker compose down 

run-unit-test:
	pipenv run pytest test/

run-integration-test:
	bash integration_test/run.sh

quality-check:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .







	





	