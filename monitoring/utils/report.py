from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

import yaml
from utils.utils import get_report_path, get_config_path


def get_column_mapping():
    config_path = get_config_path()

    with open(config_path) as f:
        config = yaml.safe_load(f)

    num_vars = config["numerical_variables"]
    cat_vars = config["categorical_variables"]

    column_mapping = ColumnMapping(
    target=None,
    prediction="prediction",
    numerical_features=num_vars,
    categorical_features=cat_vars
    )

    return column_mapping

def build_data_drift_report(current_data, reference_data, column_mapping):

    data_drift_report = Report(
    metrics=[
        DataDriftPreset(),
    ]
    )

    data_drift_report.run(
        current_data=current_data, 
        reference_data=reference_data, 
        column_mapping=column_mapping)


    report_directory = get_report_path()
    report_path = report_directory + "/data_drift_report.html"
    data_drift_report.save_html(report_path)

    return report_path

def build_target_drift_report(current_data, reference_data, column_mapping):

    target_drift_report = Report(
    metrics=[
        TargetDriftPreset(),
    ]
    )

    target_drift_report.run(
        current_data=current_data, 
        reference_data=reference_data, 
        column_mapping=column_mapping)

    report_directory = get_report_path()
    print(report_directory)
    report_path = report_directory + "/target_drift_report.html"
    print(report_path)
    target_drift_report.save_html(report_path)

    return report_path