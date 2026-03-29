import os
import sys
import time
import requests

SONAR_HOST_URL = os.getenv("SONAR_HOST_URL")
SONAR_TOKEN = os.getenv("SONAR_TOKEN")
SONAR_PROJECT_KEY = os.getenv("SONAR_PROJECT_KEY")

if not SONAR_HOST_URL or not SONAR_TOKEN or not SONAR_PROJECT_KEY:
    print("ERROR: Missing required SonarQube environment variables.")
    sys.exit(1)

url = f"{SONAR_HOST_URL}/api/qualitygates/project_status"
params = {"projectKey": SONAR_PROJECT_KEY}

max_attempts = 12
wait_seconds = 5

for attempt in range(1, max_attempts + 1):
    try:
        response = requests.get(url, params=params, auth=(SONAR_TOKEN, ""))
        response.raise_for_status()
        data = response.json()

        project_status = data.get("projectStatus", {})
        status = project_status.get("status")

        if status:
            print(f"SonarQube Quality Gate Status: {status}")

            conditions = project_status.get("conditions", [])
            if conditions:
                print("Condition Details:")
                for condition in conditions:
                    metric = condition.get("metricKey", "unknown")
                    condition_status = condition.get("status", "unknown")
                    actual = condition.get("actualValue", "N/A")
                    print(f" - {metric}: {condition_status} (actual={actual})")

            if status != "OK":
                print("FAIL: Quality gate failed.")
                sys.exit(1)

            print("PASS: Quality gate passed.")
            sys.exit(0)

    except requests.RequestException as e:
        print(f"Attempt {attempt}: Error querying SonarQube API: {e}")

    print(f"Attempt {attempt}: Quality gate not ready yet. Retrying in {wait_seconds} seconds...")
    time.sleep(wait_seconds)

print("ERROR: Timed out waiting for SonarQube quality gate result.")
sys.exit(1)