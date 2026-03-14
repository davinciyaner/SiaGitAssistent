import io
import os
import subprocess
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
    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=1)
    if not runs:
        return {"message": "Keine Workflow-Runs gefunden."}

    last_run = runs[0]
    run_id = last_run["id"]

    result = {
        "run_id": run_id,
        "workflow_name": last_run.get("name"),
        "status": last_run.get("status"),
        "conclusion": last_run.get("conclusion"),
        "html_url": last_run.get("html_url"),
        "logs_url": github.get_run_logs(repo_full_name, run_id)["logs_url"],  # nur URL
    }

    if result["status"] != "completed":
        result["message"] = "Workflow läuft noch..."
    elif result["conclusion"] == "success":
        result["message"] = "Workflow erfolgreich abgeschlossen."
    else:
        result["message"] = "Workflow fehlgeschlagen."

    return result


@router.get("/ci/auto-fix")
def ci_auto_fix(repo_full_name: str, repo_local_path: str = None):
    """
    1️⃣ Findet den letzten fehlgeschlagenen Workflow-Run
    2️⃣ Lädt Logs herunter
    3️⃣ Analysiert Fehler via AI
    4️⃣ Optional: behebt fehlende Module
    """

    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=10)

    failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)
    if not failed_run:
        return {"message": "Keine fehlgeschlagenen Runs gefunden."}

    run_id = failed_run["id"]
    logs_url = (
        f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/logs"
    )

    # --- Logs herunterladen ---
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
    r = requests.get(logs_url, headers=headers, stream=True)
    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Logs konnten nicht heruntergeladen werden: {r.text}",
        )

    z = zipfile.ZipFile(io.BytesIO(r.content))
    logs_text = ""
    for file_name in z.namelist():
        logs_text += z.read(file_name).decode("utf-8") + "\n---\n"

    # --- AI-Analyse ---
    ai_result = ai_explain_log(logs_text)

    # --- Automatische Behebung (nur fehlende Python-Module) ---
    if repo_local_path:
        os.chdir(repo_local_path)  # in lokales Repo wechseln
        missing_modules = ai_result.get("missing_modules", [])
        for module in missing_modules:
            subprocess.run(["pip", "install", module], check=False)
        # requirements.txt aktualisieren
        with open("requirements.txt", "a") as f:
            for module in missing_modules:
                f.write(f"{module}\n")

    return {
        "failed_run_id": run_id,
        "workflow_name": failed_run["name"],
        "html_url": failed_run["html_url"],
        "logs_url": logs_url,
        "ai_analysis": ai_result,
        "fix": f"{len(ai_result.get('missing_modules', []))} Module ggf. automatisch installiert",
    }


@router.get("/ci/last-run")
def ci_last_run(repo_full_name: str, repo_local_path: str = None):
    """
    1️⃣ Nimmt den letzten Workflow-Run
    2️⃣ Prüft Status/Conclusion
    3️⃣ Gibt Logs-URL zurück
    4️⃣ Optional: AI-Analyse + automatische Behebung
    """

    github = get_github_service()

    # --- letzten Run abrufen ---
    runs = github.latest_workflow_runs(repo_full_name, limit=1)
    if not runs:
        return {"message": "Keine Workflow-Runs gefunden."}

    last_run = runs[0]
    run_id = last_run["id"]
    status = last_run.get("status")
    conclusion = last_run.get("conclusion")
    workflow_name = last_run.get("name")

    result = {
        "run_id": run_id,
        "workflow_name": workflow_name,
        "status": status,
        "conclusion": conclusion,
        "html_url": last_run.get("html_url"),
        "logs_url": github.get_run_logs(repo_full_name, run_id)["logs_url"],
    }

    # --- Status prüfen ---
    if status != "completed":
        result["message"] = "Workflow läuft noch..."
        return result
    elif conclusion == "success":
        result["message"] = "Workflow erfolgreich abgeschlossen."
        return result
    else:
        result["message"] = "Workflow fehlgeschlagen."

    # --- Optional: Logs herunterladen & AI-Analyse ---
    if repo_local_path:
        # Wenn du lokal geclont hast, AI-Analyse möglich
        import requests, zipfile, io, os, subprocess

        logs_url = github.get_run_logs(repo_full_name, run_id)["logs_url"]

        headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
        r = requests.get(logs_url, headers=headers, stream=True)
        if r.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(r.content))
            logs_text = ""
            for file_name in z.namelist():
                logs_text += z.read(file_name).decode("utf-8") + "\n---\n"

            ai_result = ai_explain_log(logs_text)
            result["ai_analysis"] = ai_result

            # --- Automatisches Fixen von fehlenden Python-Modulen ---
            os.chdir(repo_local_path)
            for module in ai_result.get("missing_modules", []):
                subprocess.run(["pip", "install", module], check=False)
            with open("requirements.txt", "a") as f:
                for module in ai_result.get("missing_modules", []):
                    f.write(f"{module}\n")
            result["fix"] = (
                f"{len(ai_result.get('missing_modules', []))} Module ggf. installiert"
            )

    return result


@router.get("/ci/fix-last-run")
def fix_last_run(repo_full_name: str, repo_local_path: str = None):
    """
    1️⃣ Nimmt den letzten Workflow-Run
    2️⃣ Prüft, ob er fehlgeschlagen ist
    3️⃣ Lädt Logs herunter
    4️⃣ Analysiert Fehler via AI
    5️⃣ Installiert fehlende Python-Module automatisch (falls repo_local_path angegeben)
    """

    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=10)

    # --- letzten fehlgeschlagenen Run finden ---
    failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)
    if not failed_run:
        return {"message": "Keine fehlgeschlagenen Runs gefunden."}

    run_id = failed_run["id"]
    logs_url = (
        f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/logs"
    )

    # --- Logs herunterladen ---
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
    r = requests.get(logs_url, headers=headers, stream=True)
    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Logs konnten nicht heruntergeladen werden: {r.text}",
        )

    z = zipfile.ZipFile(io.BytesIO(r.content))
    logs_text = ""
    for file_name in z.namelist():
        try:
            logs_text += z.read(file_name).decode("utf-8") + "\n---\n"
        except Exception:
            continue

    # --- AI-Analyse ---
    ai_result = ai_explain_log(logs_text)

    fix_summary = "Keine automatische Fixes durchgeführt."
    # --- Automatisches Fixen von fehlenden Python-Modulen ---
    if repo_local_path and os.path.exists(repo_local_path):
        os.chdir(repo_local_path)
        missing_modules = ai_result.get("missing_modules", [])
        for module in missing_modules:
            subprocess.run(["pip", "install", module], check=False)
        # requirements.txt aktualisieren
        with open("requirements.txt", "a") as f:
            for module in missing_modules:
                f.write(f"{module}\n")
        fix_summary = f"{len(missing_modules)} Module ggf. automatisch installiert"

    return {
        "failed_run_id": run_id,
        "workflow_name": failed_run["name"],
        "html_url": failed_run["html_url"],
        "logs_url": logs_url,
        "ai_analysis": ai_result,
        "fix_summary": fix_summary,
    }


@router.get("/ci/full-auto-fix")
def ci_full_auto_fix(
    repo_full_name: str,
    repo_local_path: str,
    git_user_name: str = "SiaAgent",
    git_user_email: str = "sia@local.dev",
):
    """
    1️⃣ Nimmt den letzten fehlgeschlagenen Workflow-Run
    2️⃣ Lädt Logs herunter
    3️⃣ Analysiert Fehler via AI
    4️⃣ Fix: fehlende Python-Module installieren + Black-Formatierung
    5️⃣ Commit & Push der Korrekturen
    """
    github = get_github_service()

    # --- Letzten fehlgeschlagenen Run abrufen ---
    runs = github.latest_workflow_runs(repo_full_name, limit=10)
    failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)

    if not failed_run:
        return {"message": "Keine fehlgeschlagenen Runs gefunden."}

    run_id = failed_run["id"]
    workflow_name = failed_run["name"]
    html_url = failed_run["html_url"]

    # --- Logs herunterladen ---
    logs_url = (
        f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/logs"
    )
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
    r = requests.get(logs_url, headers=headers, stream=True)
    if r.status_code != 200:
        raise HTTPException(
            status_code=r.status_code,
            detail=f"Logs konnten nicht heruntergeladen werden: {r.text}",
        )

    z = zipfile.ZipFile(io.BytesIO(r.content))
    logs_text = ""
    for file_name in z.namelist():
        try:
            logs_text += z.read(file_name).decode("utf-8") + "\n---\n"
        except Exception:
            continue

    # --- AI-Analyse ---
    ai_result = ai_explain_log(logs_text)

    # --- Lokaler Fix ---
    fixed_files = []
    os.chdir(repo_local_path)

    # 1️⃣ Fehlende Python-Module installieren
    for module in ai_result.get("missing_modules", []):
        if "keine Python-Module" not in module.lower():
            subprocess.run(["pip", "install", module], check=False)

    # 2️⃣ Black-Formatierung bei Fehlern
    problem_texts = ai_result.get("problem", [])
    black_files = []

    for line in problem_texts:
        if ".py" in line:
            # Zeile kann mehrere Dateien enthalten, getrennt durch Komma
            parts = [p.strip().replace("`", "").lstrip("-") for p in line.split(",")]
            for p in parts:
                if os.path.exists(p):
                    black_files.append(p)

    if black_files:
        subprocess.run(["black"] + black_files, check=False)
        fixed_files = black_files

    # 3️⃣ Git commit & push der Änderungen
    if fixed_files:
        subprocess.run(["git", "config", "user.name", git_user_name], check=False)
        subprocess.run(["git", "config", "user.email", git_user_email], check=False)
        subprocess.run(["git", "add"] + fixed_files, check=False)
        subprocess.run(
            ["git", "commit", "-m", f"Auto-formatierung: {', '.join(fixed_files)}"],
            check=False,
        )
        subprocess.run(["git", "push"], check=False)

    return {
        "failed_run_id": run_id,
        "workflow_name": workflow_name,
        "html_url": html_url,
        "logs_url": logs_url,
        "ai_analysis": ai_result,
        "fixed_files": fixed_files,
        "message": f"{len(fixed_files)} Dateien automatisch formatiert; fehlende Module ggf. installiert und Änderungen gepusht",
    }
