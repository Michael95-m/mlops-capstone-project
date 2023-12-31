#!/bin/bash
if [[ -z "${GITHUB_ACTIONS}" ]]; then
    diabetes_service=diabetes_service
else
    diabetes_service=diabetes_test_service
fi

echo "Mlflow server and prediction service starting"
docker compose up -d ${diabetes_service}

sleep 5

echo "Running integration test to the diabetes service API"
pipenv run python integration_test/test_service.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker compose logs ${diabetes_service}
    docker compose down ${mlflow_server} ${diabetes_service}
    exit ${ERROR_CODE}
fi

docker compose down ${mlflow_server} ${diabetes_service}

echo "Yayy!! Integration test passed"
