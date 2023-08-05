# pylint: disable=ungrouped-imports
import yaml
from evidently import ColumnMapping
from utils.utils import get_config_path, get_report_path
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset


def get_column_mapping():
    """
    Get the column mapping for evidently report
    """
    config_path = get_config_path()

    with open(config_path, encoding="utf-8") as file:
        config = yaml.safe_load(file)

    num_vars = config["numerical_variables"]
    cat_vars = config["categorical_variables"]

    column_mapping = ColumnMapping(
        target=None,
        prediction="prediction",
        numerical_features=num_vars,
        categorical_features=cat_vars,
    )

    return column_mapping


def build_data_drift_report(current_data, reference_data, column_mapping):
    """
    make report for data drift
    Args:
        current_data (pandas.DataFrame): current data
        reference_data (pandas.DataFrame): reference data
        column_mapping (evidently.pipeline.column_mapping.ColumnMapping): column mapping

    Returns:
        str: A path where the report is saved
    """
    data_drift_report = Report(
        metrics=[
            DataDriftPreset(),
        ]
    )

    data_drift_report.run(
        current_data=current_data,
        reference_data=reference_data,
        column_mapping=column_mapping,
    )

    report_directory = get_report_path()
    report_path = report_directory + "/data_drift_report.html"
    data_drift_report.save_html(report_path)

    return report_path


def build_target_drift_report(current_data, reference_data, column_mapping):
    """
    Make report for target drift
    Args:
        current_data (pandas.DataFrame): current data
        reference_data (pandas.DataFrame): reference data
        column_mapping (evidently.pipeline.column_mapping.ColumnMapping): column mapping

    Returns:
        str: A path where the report is saved
    """
    target_drift_report = Report(
        metrics=[
            TargetDriftPreset(),
        ]
    )

    target_drift_report.run(
        current_data=current_data,
        reference_data=reference_data,
        column_mapping=column_mapping,
    )

    report_directory = get_report_path()
    report_path = report_directory + "/target_drift_report.html"
    target_drift_report.save_html(report_path)

    return report_path
