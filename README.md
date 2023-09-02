[![CI_TEST](https://github.com/Michael95-m/mlops-capstone-project/actions/workflows/ci.yaml/badge.svg?branch=main)](https://github.com/Michael95-m/mlops-capstone-project/blob/main/.github/workflows/ci.yaml)

# MLOps-Capstone-Project

## Problem Description

Dataset can be downloaded from kaggle at [here](https://www.kaggle.com/datasets/iammustafatz/diabetes-prediction-dataset)

This is the implementation of capstone project for mlops-zoomcamp from [DataTalksClub](https://datatalks.club/). The project provides the **diabetes prediction service** for the patients in the hospital by using the patients' medical information. Let's imagine that the aim is to predict whether the patient has the diabetes or not and take necessary actions based on the result.

The main focus of the project is to apply the MLops principles like experiment tracking, training pipeline, model monitoring concepts to the machine learning projects rather than getting state-of-the-art accuracy.

## Process Diagram

You can see the complete system design below.

![](docs/system_design.png)<br>

## Contact for questions

- **Name** - Min Khant Maung Maung
- **Email** - minkhantmgmg.mk19@gmail.com

## Reproducibility

I have reproduced this process on **ubuntu 22.04** on **EC2 instances** with **python 3.9**.

## Prerequisites

When you tried to run this repository on the cloud servers like **EC2 instances**, we need to do the following steps:

```
sudo apt update
```

### 1. Installation of make and git

```
sudo apt install make git
```

### 2. Installation of necessary libries for sqlalchemy library

```
sudo apt-get install libpq-dev python3-dev
```

### 3. Installation of docker and docker compose

Since this project uses a lot of dockerized services, docker and docker compose are needed to be installed.

You need to follow these steps about **Install using the apt repository** from [here](https://docs.docker.com/engine/install/ubuntu/). You also need to install the post installation activity of docker from [here](https://docs.docker.com/engine/install/linux-postinstall/).

### 4. Installation of pip

If you server didn't have **pip**, ```sudo apt install python3-pip```

### 5. Solving Warning About the path

If you get the warning like ```WARNING: The scripts pip, pip3, pip3.10 and pip3.11 are installed in '/home/ubuntu/.local/bin' which is not on PATH.
Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location```.

Then you have

1. Open **~/.bashrc** by

```shell
nano ~/.bashrc
```

2. Add this line at the bottom of the file.
```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. Exit from the editor and run to take effect.
```shell
source ~/.bashrc
```

### 6. Installation of pipenv

You can install pipenv by
```
pip install -U pip
pip install pipenv --user
```

### 8. Cloning the git repository.

Clone the repository.
```shell
git clone https://github.com/Michael95-m/mlops-capstone-project.git
```

Go to the root directory by ```cd mlops-capstone-project```.



### 7. Creation of virtual environment using pipenv

This project is developed using **python3.9**. If your server didn't have python3.9, it's better to install it. You can install python3.9 by using anaconda's conda environment.

You can install **anaconda** like [that](https://linuxhint.com/install-anaconda-ubuntu-22-04/) and create a conda environment like [that](https://stackoverflow.com/questions/63216201/how-to-install-python-with-conda).

Then create an environment with **pipenv** (replace with the python path in the server)
```shell
pipenv --python=/path/to/anaconda/environment/python3.9
```

Then install dependencies by using
```shell
pipenv install --dev
```


**Warning:** The following instruction needed to be run at the **root directory** of the repo.

### 8. Dealing with environment variables

This project uses several environment variables like aws credentials. You need to export it before running the project or the easiest way is to create the file named **.env** file at the root level of the directory.

```
EMAIL_USERNAME=example@gmail.com
EMAIL_PASSWORD=1234567
AWS_ACCESS_KEY_ID=abcdefg
AWS_SECRET_ACCESS_KEY=123456
AWS_DEFAULT_REGION=ap-southeast-1
BUCKET_NAME=mlops-capstone-project-bucket
OBJECT_NAME=diabetes_prediction_dataset.csv
```

You need to copy the above variables to the .env file and replace it with your own credentials.

- **EMAIL_USERNAME** and **EMAIL_PASSWORD** is used for creating email block.
- **AWS_ACCESS_KEY_ID**, **AWS_SECRET_ACCESS_KEY**, **AWS_DEFAULT_REGION** is used for running training pipeline with s3 bucket.**BUCKET_NAME** and **OBJECT_NAME** are used to identity the bucket and the data placed inside it.
- If you don't specify these, you will get the errors in running with *training pipeline with s3 bucket* and *creating monitoring pipeline*.

**Note:** The following processes are needed to implement sequentially.

## Training Pipeline

You want to know more about training pipeline, take a look at [this readme](./pipeline/README.md)

### 1. Setup model's registry requirments

- Run `make setup-model-registry`. (Do it only for the first time running and yon don't need to do it for next time.)

- It just create the folder named **mnt** inside the home directory to save the metrics and artifacts from mlflow_server service.

### 2. Start prefect server

- Start the prefect server in **another terminal**  to run the training pipeline. Start by `make prefect-server-start`.

### 3. Run the training pipeline

- Run the training pipeline which train **XGBoost** model and registry the best model in the experiment in the **mlflow model registry**.

- You can run by `make run-training-pipeline`.

### 3.1. Run the training pipeline with the data from s3.(Optional)

- To run the training pipeline with the data downloaded from s3 (additionally, it will also upload the training, validation and test data to the s3 bucket), you can use `make run-training-pipeline-s3`.


### 4. Deploy the training pipeline in prefect

- You need to create the workpool named **train-pool** by using `make create-workpool`.

- After that, you can deploy the training pipeline by using `make deploy-training-pipeline`.

- (This step is only needed for the one time if it succeed.)

### 5. Run the deployed training pipeline

- In order to run the deployed training pipeline, you need to start a worker in a **separate terminal** by `make start-worker`.

- After starting the worker, you can run the deployed training pipeline by using `make run-deployed-training-pipeline`.

### 5.1. Run the deployed training pipeline  with s3 data

- It has the same behaviour as **3.1.**. In order to run, use `make run-deployed-training-pipeline-s3`.

## Model Serving

- The trained model will be deployed as HTTP service by using *flask* and *gunicorn*.
- **Note:** In order to deploy the model as a service, you need to run the **training pipeline** at least once to have the production model in the mlflow model registry. And you also need to up the **mlflow_server** service to access this model (which is already up if you follow the process above)

You want to know more about model serving, take a look at [this readme](./deployment/README.md)

### 1. Start the diabetes service

- You can start the diabetes-service by running `make start-diabetes-service`.

## Model Monitoring

For model monitoring, the **diabetes-service** from **model serving** part and the **mlflow_server** service will be needed to be up.

You want to know more about model monitoring, take a look at [this readme](./monitoring/README.md)

### 1. Preparing reference data

- You need to copy validation data named **valid.parquet** from the data folder to the **data** folder inside **monitoring**. Actually I have already copied for you.

- Then start diabetes-service by `make start-diabetes-service`. If this service is already up, you don't need to do this.

- After that,  run `make prepare-reference` to prepare reference data.

### 2. Start all other services inside docker-compose.yml

- All other services inside docker compose file will be needed to be up and you can do it by using `make start-all-services`.

### 3. Create the database named **production** in the postgresql service

- You need to create the database named **production** to save the prediction result for monitoring purpose.

- This prediction log will become the **current data** for checking the data drift. You can create it by using `make create-db`.

### 4. Send the simulation data to the monitoring api

- You have to send the **simulation data** to the monitoring api for the purpose of model monitoring. You can send it by using `send-data-monitoring-api` in **another terminal** or using creating of **screen service**.

- While sending the data, you can check the data inside the table named **prediction_log** inside the database.

### 5. Check the data drift and target drift

- You can check the data drift and target drift when there is a certain amount of data inside the table. You can check the data inside with [**adminer** tool](http://localhost:8080).

- You can login the adminer by using
    - **postgresql** for system
    - **db** for server
    - **admin** for username
    - **example** for password
    - **production** for database
<br><br>

- Then go to the [streamlit service](http://localhost:8501) and you will see the streamlit UI. Then click the **Data Drift** button to check the report about **data drift**.

- Then click the **Target Drift** button to check the report about **target drift**.

### 6. Deploy the monitoring pipeline in prefect

- We can deploy the **monitoring pipeline** that can send an email as an alert if the drift is detected on current data. You can implement it by deploying the workflow in the prefect.

### 6.1. Create an email block for prefect

- Create an email block by using `make create-email-block`. Before creating email block, you need to set environment variable named

    - EMAIL_USERNAME
    - EMAIL_PASSWORD

- The easiest way to set is using **.env** file. You can set the value inside of that file. **EMAIL_PASSWORD** is not your password; it's called the appword. You can check how to generate it at [here](https://support.google.com/mail/answer/185833?hl=en)

### 6.2. Running the monitoring pipeline.

- If you want to check the data drift for yesterday's data, just run `make run-monitoring-pipeline`.

- If you want to check for specific day's data, run `pipenv run python monitoring/send_alerts.py -d <day> -m <month> -y <year>`. You can replace <day>, <month> and <year> as the date you want to check.

Eg. This command, `pipenv run python monitoring/send_alerts.py -d 9 -m 8 -y 2023` will run the data drift check for **9 August 2023**.

### 6.3. Running the deployed monitoring pipeline

- First, you need to deploy monitoring pipeline with `make deploy-monitoring-pipeline`.

- In order to run monitoring pipeline, you need to start workpool by `make start-worker`.

- You can run the deployed workflow by `make run-deployed-monitoring-pipeline`. And it will check the data drift for yesterday.

- For specific day, run `pipenv run prefect deployment run -p day=<day> -p month=<month> -p year=<year> send-alert/deploy_monitor`. You can replace it as you like.

## Stopping and restarting the services

### 1. Stop all the running services

You have already set up the mlops-pipeline. You can stop the services ```make stop-all-services```

### 2. Restart all the running service

You can easily restart all these services for next time by running ```make start-all-services```. You don't need to repeat all these above steps to run.

## Testing

You want to know more about test cases, take a look at [this readme](./docs/Best_practices.md)

### 1. Check the unit test.

- You can run unit test by `make run-unit-test`.

### 2. Check the integration test.

- You can run integration test by `make run-integration-test`.
- In order to run integration test, you need to down all docker services. You can do this by `make stop-all-services`.

### 3. Check the quality of the code by linting tools.

- You can run by `make quality-check`.

## Services

All these service except prefect can be started by using **docker compose** by `make start-all-services`. If you run from the server instances like EC2, you need to place **127.0.0.1** with your **IP address** of the server

|   Service |   Port    |   Interface   |   Description |
| --- | --- | --- | --- |
|   mlflow_server   |   5000    |   127.0.0.1   |   MLflow experiment tracking and model registry   |
|   prefect   |   4200    |   127.0.0.1   |  Prefect Workflow Orchestration   |
|   diabetes_service   |   5010    |   127.0.0.1   |   Diabetes Prediction Service   |
|   monitoring_service   |   5020    |   127.0.0.1   |   Monitoring Service (use the prediction service above and save the result)   |
|   monitoring_db   |   5432    |   127.0.0.1   |   Postgresql Database   |
|   monitoring_adminer   |   8080    |   127.0.0.1   |   Adminer Tools (to check inside database)   |
|   streamlit_service   |   8501    |   127.0.0.1   |   Streamlit web service to visualize the data and target drift   |

## Scoring

For the scoring purpose, if you want to find out which steps are implemented throughout this project, check [this](./docs/plan.md)

## Certificate of Completion

![Certificate of Completion](./docs/mlops-zoomcamp-certificate.jpg)
