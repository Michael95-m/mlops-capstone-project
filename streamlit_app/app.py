# pylint: disable=import-error,no-name-in-module, invalid-name, broad-exception-caught
import os

import requests
import streamlit as st
from utils.ui import (
    display_header,
    display_report,
    display_sidebar_header,
    set_page_container_style
)

if __name__ == "__main__":
    set_page_container_style()

    display_sidebar_header()
    MONITORING_SERVE_API = os.getenv("MONITOR_SERVE_ADDRESS", "http://localhost:5020")

    try:
        window_size = st.sidebar.number_input(
            label="window_size", min_value=1, step=1, value=3000
        )

        clicked_data_drift = st.sidebar.button(label="Data Drift")

        clicked_target_drift = st.sidebar.button(label="Target drift")

        report_selected = False
        request_url = MONITORING_SERVE_API
        report_name = ""

        if clicked_data_drift:
            report_selected = True
            request_url += f"/monitor_data_drift?window_size={window_size}"
            report_name = "Data Drift"

        if clicked_target_drift:
            report_selected = True
            request_url += f"/monitor_target_drift?window_size={window_size}"
            report_name = "Target drift"

        if report_selected:
            resp = requests.get(request_url, timeout=5)
            display_header(report_name, window_size)
            display_report(resp.content)

    except Exception as e:
        st.error(e)
