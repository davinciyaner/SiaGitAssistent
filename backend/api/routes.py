import io
import os
import zipfile
import requests

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException

from backend.agent.repo_analyzer import ai_explain_log
from backend.auth import token_store
from backend.services.git_service import GitHubService

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

router = APIRouter(prefix="/github")


def get_github_service():
    token = token_store.ACCESS_TOKEN
    if not token:
        raise HTTPException(status_code=401, detail="GitHub Token fehlt")
    return GitHubService(token)


@router.get("/issues")
def list_issues(repo_full_name: str, limit: int = 10):
    github = get_github_service()
    return github.list_issues(repo_full_name, limit=limit)


@router.get("/pulls")
def list_pulls(repo_full_name: str, limit: int = 10):
    github = get_github_service()
    return github.list_pull_requests(repo_full_name, limit=limit)


@router.get("/commits")
def list_commits(repo_full_name: str, limit: int = 10):
    github = get_github_service()
    return github.list_commits(repo_full_name, limit=limit)


@router.get("/stats")
def repo_stats(repo_full_name: str):
    github = get_github_service()
    return github.repo_stats(repo_full_name)


@router.get("/ci/workflows")
def workflows(repo_full_name: str):
    github = get_github_service()
    return github.list_workflows(repo_full_name)


@router.get("/ci/runs")
def workflow_runs(repo_full_name: str, workflow_id: int = None, limit: int = 5):
    github = get_github_service()
    return github.latest_workflow_runs(repo_full_name, workflow_id, limit)


@router.get("/ci/logs")
def workflow_logs(repo_full_name: str, run_id: int):
    github = get_github_service()
    return github.get_run_logs(repo_full_name, run_id)


@router.get("/ci/monitor")
def ci_monitor(repo_full_name: str):
    """
    1️⃣ Prüft den letzten Workflow-Run
    2️⃣ Gibt Status zurück
    3️⃣ Liefert die Logs-URL
    4️⃣ Optional: AI-Analyse (wenn Logs lokal verfügbar)
    """
    github = get_github_service()

    # --- Letzten Run abrufen ---
    runs = github.latest_workflow_runs(repo_full_name, limit=1)
    if not runs:
        return {"message": "Keine Workflow-Runs gefunden."}

    last_run = runs[0]
    run_id = last_run["id"]
    conclusion = last_run.get("conclusion")
    status = last_run.get("status")

    result = {
        "run_id": run_id,
        "workflow_name": last_run.get("name"),
        "status": status,
        "conclusion": conclusion,
        "html_url": last_run.get("html_url")
    }

    if status != "completed":
        result["message"] = "Workflow läuft noch..."
        return result

    if conclusion == "success":
        result["message"] = "Workflow erfolgreich abgeschlossen."
    else:
        result["message"] = "Workflow fehlgeschlagen."

    # --- Logs-URL zurückgeben (kein Download) ---
    logs_info = github.get_run_logs(repo_full_name, run_id)
    result["logs_url"] = logs_info["logs_url"]

    # Optional: AI-Analyse nur, wenn du Logs lokal herunterladen willst
    # logs_text = download_logs_somehow()  # NICHT nötig, wenn nur URL
    # ai_result = ai_explain_log(logs_text)
    # result["ai_analysis"] = ai_result

    return result
