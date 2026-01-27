import requests
import time

try:
    response = requests.get("http://localhost:8501")
    if response.status_code == 200:
        print("SUCCESS: App is running and reachable.")
    else:
        print(f"FAILURE: App returned status code {response.status_code}")
except Exception as e:
    print(f"FAILURE: Could not connect to app. Error: {e}")
