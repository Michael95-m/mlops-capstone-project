#!/bin/bash

echo "Mlflow server and prediction service starting"
docker compose -f docker-compose.serve.yaml -f docker-compose.registry.yaml up -d

sleep 5

echo "Running integration test"
pipenv run python integration_test/test_service.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker compose -f docker-compose.serve.yaml -f docker-compose.registry.yaml logs
    docker compose -f docker-compose.serve.yaml -f docker-compose.registry.yaml down
    exit ${ERROR_CODE}
fi

docker compose -f docker-compose.serve.yaml -f docker-compose.registry.yaml down

echo "Yayy!! Integration test passed"

