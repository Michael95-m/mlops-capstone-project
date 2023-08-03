import requests
import os

MONITOR_SERVE_ADDRESS = os.getenv("MONITOR_SERVE_ADDRESS", "http://127.0.0.1:5020")

full_url = f"{MONITOR_SERVE_ADDRESS}/monitor_target_drift?window_size=600"
file = requests.get(full_url)