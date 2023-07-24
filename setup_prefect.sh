#!/bin/bash

echo "Work-pool named train-pool is created"
prefect work-pool create --type process train-pool

echo "Flow run named deploy_train is deployed "
prefect deploy -n deploy_train