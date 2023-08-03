MLFLOW_TRACKING_DIRECTORY := $(HOME)/mnt/mlruns

export MLFLOW_TRACKING_DIRECTORY

setup-model-registry:
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/tracking
	mkdir -p ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	mkdir -p ${HOME}/mnt/serve

start-mlflow:
	docker compose -f docker-compose.registry.yaml up -d
	

stop-mlflow:
	docker compose -f docker-compose.registry.yaml down

reset-model-registry:
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/tracking
	rm -rf ${MLFLOW_TRACKING_DIRECTORY}/artifacts
	rm -rf ${HOME}/mnt/serve

start-service:
	docker compose -f docker-compose.serve.yaml up
	