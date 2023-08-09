import argparse
from datetime import datetime, timedelta

import pandas as pd
from prefect import flow, task, logging
from sqlalchemy import select, create_engine
from utils.utils import get_db_url, get_reference_data
from utils.models import PredictionTable
from utils.report import get_column_mapping
from prefect_email import EmailServerCredentials, email_send_message
from evidently.test_suite import TestSuite
from evidently.test_preset import DataDriftTestPreset


@task
def get_yesterday_info():
    """
    get the start and end timestamp of the yesterday
    Returns:
        tuple: Start timestamp and end timestamp of yesterday
    """
    yesterday = datetime.now() - timedelta(days=1)
    start_of_the_day = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_the_day = datetime(
        yesterday.year, yesterday.month, yesterday.day, 23, 59, 59
    )

    return start_of_the_day, end_of_the_day


@task
def get_day_info(day, month, year):
    """
    get the start and end timestamp of the provided day
    Args:
        day (int): day of the month
        month (int): month of the year
        year (int): year
    Returns:
        tuple: start_of_the_day and end_of_the_day of the provided day
    """
    start_of_the_day = datetime(year, month, day, 0, 0, 0)
    end_of_the_day = datetime(year, month, day, 23, 59, 59)

    return start_of_the_day, end_of_the_day


@task
def get_reference():
    """
    Get the reference data which is the validation data used in training
    Returns:
        pd.DataFrame: reference data
    """
    reference_data = get_reference_data()
    return reference_data


@task
def get_current(start_of_yesterday, end_of_yesterday):
    """
    Get the current data which is the prediction log from yesterday
    Args:
        start_of_yesterday (datetime.datetime): yesterday's start timestamp
        end_of_yesterday (datetime.datetime): yesterday's end timestamp

    Returns:
        pd.DataFrame: prediction log from yesterday
    """
    database_url = get_db_url()
    engine = create_engine(database_url)
    with engine.connect() as db_connection:
        order = PredictionTable.timestamp.desc()
        query = (
            select(PredictionTable)
            .order_by(order)
            .filter(
                PredictionTable.timestamp.between(start_of_yesterday, end_of_yesterday)
            )
        )
        current_data = pd.read_sql_query(sql=query, con=db_connection)
        current_data.drop("id", axis=1, inplace=True)

    return current_data


@task
def get_test():
    """
    Get the DataDriftTestPreset which is a colleciton of tests
    for checking datadrift
    Returns:
        evidently.test_suite.test_suite.TestSuite: A collection of tests
    """
    test = TestSuite(tests=[(DataDriftTestPreset())])
    return test


@task
def run_test(test, current_data, reference_data):
    """

    Args:
        test (evidently.test_suite.test_suite.TestSuite):  A collection of tests
        current_data (pd.DataFrame): current data
        reference_data (pd.DataFrame): referene data

    Returns:
        dict: A result for datadrift testset
    """
    test.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=get_column_mapping(),
    )

    test_dict = test.as_dict()
    return test_dict


@task
def get_drift_status(test_dict):
    """
    Get the data drift status - "PASS" or "FAIL"
    Args:
        test_dict (dict): A result for datadrift testset

    Returns:
        str: "PASS" or "FAIL"
    """
    drift_status = test_dict["tests"][0]["status"]

    return drift_status


@task
def get_email_credentails():
    """
    Returns the email credentials which is saved as email-block
    """
    return EmailServerCredentials.load("email-block")


@flow
def send_alert(day, month, year):
    """
    A main function that will send email if the data drift is detected
    """
    logger = logging.get_run_logger()

    if day and month and year:  ## if user entered the date
        logger.info("Getting day data...")
        start_of_the_day, end_of_the_day = get_day_info(day, month, year)
    else:
        logger.info("Getting Yesterday data...")
        start_of_the_day, end_of_the_day = get_yesterday_info()

    logger.info("Getting Reference data...")
    reference_data = get_reference_data()

    logger.info("Getting current data...")
    current_data = get_current(start_of_the_day, end_of_the_day)

    logger.info("Checking the data for the provided day")
    logger.info("There are %d num of rows for the provided day", len(current_data))
    if len(current_data) == 0:
        logger.info("Since there is no data for the provided day")
        logger.info("Exiting...")
        return

    logger.info("Preparing test...")
    test = get_test()

    logger.info("Run test on current data and reference data...")
    test_dict = run_test(test, current_data, reference_data)

    logger.info("Getting drift status...")
    drift_status = get_drift_status(test_dict)

    logger.info("Email credentails setup...")
    email_server_credentials = get_email_credentails()

    logger.info("Drift Checking and sending email...")
    if day and month and year:
        date = datetime(year, month, day)
    else:
        date = datetime.now().date() - timedelta(days=1)
    if drift_status == "FAIL":
        email_send_message(
            email_server_credentials=email_server_credentials,
            subject=f"Status about data drift for {date}",
            msg="Data drift detected. Retrain the model with new data",
            email_to=email_server_credentials.username,
        )
    else:
        logger.info("drift not detected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitoring pipeline")
    args_day = parser.add_argument("--day", "-d", default=None, type=int, help="Day")
    args_month = parser.add_argument(
        "--month", "-m", default=None, type=int, help="Month"
    )
    args_year = parser.add_argument("--year", "-y", default=None, type=int, help="Year")
    args = parser.parse_args()
    send_alert(day=args.args_day, month=args.args_month, year=args.args_year)
