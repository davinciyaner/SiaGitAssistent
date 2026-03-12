import os
import subprocess
import time

import requests


def run_pipeline(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/ci.yml/dispatches"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "ref": "main"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in [200,204]:
        return {"status": "Ich habe deine Pipeline gestartet"}

    return {"error": response.text}


def get_pipeline_status(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    if "workflow_runs" in data and len(data["workflow_runs"]) > 0:
        run = data["workflow_runs"][0]

        return {"status": run["status"], "conclusion": run["conclusion"], "url": run["html_url"]}

    return {"error": "Ich habe keine Pipeline gefunden"}


def get_pipeline_logs(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    runs = response.json()["workflow_runs"]

    if not runs:
        return {"error": "no runs"}

    run_id = runs[0]["id"]
    log_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs"
    logs = requests.get(log_url, headers=headers)

    return {"logs_url": log_url}

def auto_pipeline(owner, repo, token):
    print("starte pipeline..")
    result = run_pipeline(owner, repo, token)

    if "error" in result:
        return result
    print("pipeline überwachen..")

    while True:
        status = get_pipeline_status(owner, repo, token)

        if status.get("conclusion") == "success":
            return "Pipeline erfolgreich"

        if status.get("conclusion") == "failure":
            logs = get_pipeline_logs(owner, repo, token)
            return f"Pipeline fehlgeschlagen\n\nLogs:\n{logs}"

        time.sleep(10)


def create_pipeline(path: str, owner: str = None, repo: str = None, token: str = None):
    workflow_dir = os.path.join(path, ".github", "workflows")
    os.makedirs(workflow_dir, exist_ok=True)

    workflow_file = os.path.join(workflow_dir, "ci.yml")

    workflow_content = """
name: Python CI

on:
  push:
    branches: [ master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Tests
        run: |
          pytest
"""

    with open(workflow_file, "w") as f:
        f.write(workflow_content.strip())

    # Git Befehle
    try:
        subprocess.run(["git", "add", workflow_file], cwd=path, check=True)
        subprocess.run(["git", "commit", "-m", "Add CI/CD pipeline via SIA"], cwd=path, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=path, check=True)
    except subprocess.CalledProcessError as e:
        return f"Fehler beim Pushen der Pipeline: {e}"

    # Optional: GitHub Actions Status prüfen
    if owner and repo and token:
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            runs = response.json().get("workflow_runs", [])
            if not runs:
                return "Pipeline erstellt und gepusht, Workflow noch nicht gestartet."
            latest = runs[0]
            status = latest.get("status")
            conclusion = latest.get("conclusion")
            html_url = latest.get("html_url")
            return f"Pipeline gepusht!\nWorkflow Status: {status}, Conclusion: {conclusion}\n{html_url}"
        except Exception as e:
            return f"Pipeline gepusht, aber Fehler beim Abrufen des Workflow-Status: {e}"

    return "Pipeline erfolgreich erstellt und gepusht!"
    