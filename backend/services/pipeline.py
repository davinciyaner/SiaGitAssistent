import time

import requests

from backend.git.add import handle_add
from backend.git.commit import handle_commit
from backend.git.push import handle_push
from backend.services.pipeline_detector import detect_project_type
from backend.services.pipeline_generator import generate_pipeline
from backend.services.pipeline_writer import write_pipeline


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


def create_pipeline(path):
    project_type = detect_project_type(path)
    pipeline = generate_pipeline(project_type)

    if not pipeline:
        return "Ich konnte keinen Projekttyp finden"

    file = write_pipeline(path, pipeline)

    handle_add(path)
    handle_commit(path)
    handle_push(path)

    return f"Ich habe eine Pipeline erstellt und gepusht: {file}"
    