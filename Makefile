MLFLOW_TRACKING_DIRECTORY := $(HOME)/mnt/mlruns

export MLFLOW_TRACKING_DIRECTORY

setup-model-registry:
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/tracking
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	mkdir -p ${HOME}/mnt/serve

start-mlflow:
	docker compose -f docker-compose.registry.yaml up -d

reset-model-registry:
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/tracking
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	rm -rf ${HOME}/mnt/serve

start-service:
	docker compose -f docker-compose.registry.yaml -f docker-compose.serve.yaml up -d

start-all-service:
	docker compose -f docker-compose.monitoring.yaml -f docker-compose.registry.yaml \
	-f docker-compose.serve.yaml up -d

start-monitoring-service:
	docker compose -f docker-compose.monitoring.yaml up -d 

start-send-data-monitoring:
	pipenv shell python monitoring/send_data_api.py

stop-mlflow:
	docker compose -f docker-compose.registry.yaml down

stop-service:
	docker compose -f docker-compose.registry.yaml -f docker-compose.serve.yaml down

stop-monitoring-service:
	docker compose -f docker-compose.monitoring.yaml down

stop-all-service:
	docker compose -f docker-compose.monitoring.yaml -f docker-compose.registry.yaml \
	-f docker-compose.serve.yaml down

run-unit-test:
	pipenv run pytest test/

run-integration-test:
	bash integration_test/run.sh







	





	