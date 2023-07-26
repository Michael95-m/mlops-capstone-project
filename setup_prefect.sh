#!/bin/bash

echo "Work-pool named train-pool is created"
pipenv run prefect work-pool create --type process train-pool

echo "Flow run named deploy_train is deployed "
pipenv run prefect deploy -n deploy_train