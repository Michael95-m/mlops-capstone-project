from sqlalchemy import create_engine, select
from utils.utils import get_db_url
from utils.models import PredictionTable
import pandas as pd
from datetime import datetime, timedelta
from utils.report import get_column_mapping
from evidently.test_suite import TestSuite
from evidently.test_preset import (
    DataDriftTestPreset
)
from utils.utils import get_reference_data
from prefect_email import EmailServerCredentials, email_send_message
from prefect import task, flow, logging

@task
def get_yesterday_info():
    yesterday = datetime.now() - timedelta(days=1)
    start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    return start_of_yesterday, end_of_yesterday

@task
def get_reference():
    reference_data = get_reference_data()
    return reference_data

@task
def get_current(start_of_yesterday, end_of_yesterday):
    DATABASE_URL = get_db_url()
    engine = create_engine(DATABASE_URL)
    with engine.connect() as db_connection:
        order = PredictionTable.timestamp.desc()
        query = (
            select(PredictionTable).order_by(order)
            .filter(PredictionTable.timestamp.between(start_of_yesterday, end_of_yesterday))
        )
        current_data = pd.read_sql_query(
            sql=query,
            con=db_connection
        )
        current_data.drop('id', axis=1, inplace=True)

    return current_data

@task
def get_test():
    test = TestSuite(tests=[(
        DataDriftTestPreset()
    )]  
    )
    return test

@task
def run_test(test, current_data, reference_data):
    test.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=get_column_mapping())

    test_dict = test.as_dict()
    return test_dict

@task
def get_drift_status(test_dict):

    drift_status = test_dict['tests'][0]['status']

    return drift_status

@task
def get_email_credentails():

    return EmailServerCredentials.load("email-block")
    
@flow
def send_alert():
    logger = logging.get_run_logger()

    logger.info("Getting Yesterday data...")
    start_of_yesterday, end_of_yesterday = get_yesterday_info()

    logger.info("Getting Reference data...")
    reference_data = get_reference_data()

    logger.info("Getting current data...")
    current_data = get_current(start_of_yesterday, end_of_yesterday)

    logger.info("Preparing test...")
    test = get_test()

    logger.info("Run test on current data and reference data...")
    test_dict = run_test(test, current_data, reference_data)

    logger.info("Getting drift status...")
    drift_status = get_drift_status(test_dict)

    logger.info("Email credentails setup...")
    email_server_credentials = get_email_credentails()

    logger.info("Drift Checking and sending email...")
    yesterday = datetime.now().date() - timedelta(days=1)
    if drift_status == "FAIL":
        email_send_message(
            email_server_credentials=email_server_credentials,
            subject=f"Status about data drift for {yesterday}",
            msg="Data drift detected. Retrain the model with new data",
            email_to=email_server_credentials.username
        )
    else:
        print("drift not detected")
    

if __name__ == "__main__":
    
    send_alert()