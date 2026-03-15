import io
import os
import re
import subprocess
import textwrap
import traceback
import zipfile

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.agent.repo_analyzer import ai_analyze_repo, ai_explain_log
from backend.auth import token_store
from backend.services.git_service import GitHubService, clone_repo

load_dotenv()

router = APIRouter(prefix="/github")


def get_github_service():
    token = token_store.ACCESS_TOKEN
    if not token:
        raise HTTPException(status_code=401, detail="GitHub Token fehlt")
    return GitHubService(token)


# ---------------------------------------------------------------------------
# Basis-Endpunkte
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# CI / Workflow-Endpunkte
# ---------------------------------------------------------------------------


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
        "logs_url": github.get_run_logs(repo_full_name, run_id)["logs_url"],
    }

    if result["status"] != "completed":
        result["message"] = "Workflow läuft noch..."
    elif result["conclusion"] == "success":
        result["message"] = "Workflow erfolgreich abgeschlossen."
    else:
        result["message"] = "Workflow fehlgeschlagen."

    return result


# ---------------------------------------------------------------------------
# Hilfsfunktionen: Logs laden
# ---------------------------------------------------------------------------


def _download_logs(repo_full_name: str, run_id: int) -> str:
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
    logs_url = (
        f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/logs"
    )
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
    return logs_text


# ---------------------------------------------------------------------------
# Auto-Fix Endpunkte
# ---------------------------------------------------------------------------


@router.get("/ci/auto-fix")
def ci_auto_fix(repo_full_name: str, repo_local_path: str = None):
    """Letzten fehlgeschlagenen Run analysieren und fehlende Module installieren."""
    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=10)

    failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)
    if not failed_run:
        return {"message": "Keine fehlgeschlagenen Runs gefunden."}

    run_id = failed_run["id"]
    logs_text = _download_logs(repo_full_name, run_id)
    ai_result = ai_explain_log(logs_text)

    if repo_local_path:
        os.chdir(repo_local_path)
        missing_modules = ai_result.get("missing_modules", [])
        for module in missing_modules:
            subprocess.run(["pip", "install", module], check=False)
        with open("requirements.txt", "a") as f:
            for module in missing_modules:
                f.write(f"{module}\n")

    return {
        "failed_run_id": run_id,
        "workflow_name": failed_run["name"],
        "html_url": failed_run["html_url"],
        "ai_analysis": ai_result,
        "fix": f"{len(ai_result.get('missing_modules', []))} Module ggf. automatisch installiert",
    }


@router.get("/ci/last-run")
def ci_last_run(repo_full_name: str, repo_local_path: str = None):
    """Letzten Run prüfen, bei Fehler optional AI-Analyse + Modul-Fix."""
    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=1)
    if not runs:
        return {"message": "Keine Workflow-Runs gefunden."}

    last_run = runs[0]
    run_id = last_run["id"]
    status = last_run.get("status")
    conclusion = last_run.get("conclusion")

    result = {
        "run_id": run_id,
        "workflow_name": last_run.get("name"),
        "status": status,
        "conclusion": conclusion,
        "html_url": last_run.get("html_url"),
        "logs_url": github.get_run_logs(repo_full_name, run_id)["logs_url"],
    }

    if status != "completed":
        result["message"] = "Workflow läuft noch..."
        return result
    elif conclusion == "success":
        result["message"] = "Workflow erfolgreich abgeschlossen."
        return result

    result["message"] = "Workflow fehlgeschlagen."

    if repo_local_path:
        logs_text = _download_logs(repo_full_name, run_id)
        ai_result = ai_explain_log(logs_text)
        result["ai_analysis"] = ai_result

        os.chdir(repo_local_path)
        missing = ai_result.get("missing_modules", [])
        for module in missing:
            subprocess.run(["pip", "install", module], check=False)
        with open("requirements.txt", "a") as f:
            for module in missing:
                f.write(f"{module}\n")
        result["fix"] = f"{len(missing)} Module ggf. installiert"

    return result


@router.get("/ci/fix-last-run")
def fix_last_run(repo_full_name: str, repo_local_path: str = None):
    """Letzten fehlgeschlagenen Run finden, Logs analysieren, Module installieren."""
    github = get_github_service()
    runs = github.latest_workflow_runs(repo_full_name, limit=10)

    failed_run = next((r for r in runs if r.get("conclusion") == "failure"), None)
    if not failed_run:
        return {"message": "Keine fehlgeschlagenen Runs gefunden."}

    run_id = failed_run["id"]
    logs_text = _download_logs(repo_full_name, run_id)
    ai_result = ai_explain_log(logs_text)

    fix_summary = "Keine automatischen Fixes durchgeführt."
    if repo_local_path and os.path.exists(repo_local_path):
        os.chdir(repo_local_path)
        missing_modules = ai_result.get("missing_modules", [])
        for module in missing_modules:
            subprocess.run(["pip", "install", module], check=False)
        with open("requirements.txt", "a") as f:
            for module in missing_modules:
                f.write(f"{module}\n")
        fix_summary = f"{len(missing_modules)} Module ggf. automatisch installiert"

    return {
        "failed_run_id": run_id,
        "workflow_name": failed_run["name"],
        "html_url": failed_run["html_url"],
        "ai_analysis": ai_result,
        "fix_summary": fix_summary,
    }


# ---------------------------------------------------------------------------
# Flake8-Fix Hilfsfunktionen
# ---------------------------------------------------------------------------


def fix_e401(line: str, imports_seen: set):
    stripped = line.strip()
    match = re.match(r"import\s+(.+)", stripped)
    if match:
        modules = [m.strip() for m in match.group(1).split(",")]
        fixed = []
        for mod in modules:
            if mod not in imports_seen:
                fixed.append(f"import {mod}\n")
                imports_seen.add(mod)
        return fixed
    return [line]


def fix_flake8_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    imports_seen = set()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import ") and "," in stripped:
            fixed_lines.extend(fix_e401(line, imports_seen))
            continue
        if stripped.startswith(("def ", "class ")):
            if fixed_lines and fixed_lines[-1].strip() != "":
                fixed_lines.append("\n")
        if len(line) > 100:
            for w in textwrap.wrap(line, width=88):
                fixed_lines.append(w + "\n")
            continue
        fixed_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)


def fix_flake8_dir(directory: str, pattern: str = ".py"):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(pattern):
                fix_flake8_file(os.path.join(root, file))


@router.get("/fix-flake8")
def fix_flake8_repo(repo_path: str):
    if not os.path.exists(repo_path):
        return {"error": f"Pfad {repo_path} existiert nicht."}

    fixed_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_flake8_file(file_path)
                fixed_files.append(file_path)

    return fixed_files


# ---------------------------------------------------------------------------
# Full Auto-Fix
# ---------------------------------------------------------------------------


@router.get("/ci/full-auto-fix")
def ci_full_auto_fix(
    repo_full_name: str,
    run_id: int,
    repo_local_path: str,
    branch: str = "master",
):
    """
    1️⃣ Run Details abrufen
    2️⃣ Logs herunterladen
    3️⃣ AI Analyse
    4️⃣ Problemdateien extrahieren
    5️⃣ Lokales Repo prüfen
    6️⃣ Auto-Fix durchführen (black, isort, flake8)
    7️⃣ Git push + Workflow erneut starten
    """
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}

    try:
        run_url = f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}"
        res = requests.get(run_url, headers=headers)
        res.raise_for_status()
        run = res.json()

        if run.get("conclusion") != "failure":
            return {"message": "Dieser Run ist nicht fehlgeschlagen"}

        workflow_name = run.get("name")
        workflow_id = run.get("workflow_id")
        html_url = run.get("html_url")

        logs_text = _download_logs(repo_full_name, run_id)
        ai_result = ai_explain_log(logs_text)

        # Problemdateien aus AI-Ergebnis extrahieren
        py_files = []
        for p in ai_result.get("problem", []):
            match = re.search(r"([\w/]+\.py)", p)
            if match:
                py_files.append(match.group(1))
        py_files = list(set(py_files))

        # Black-Fehler direkt aus Log erkennen
        needs_black = ai_result.get("needs_black_format", False)
        files_to_format = ai_result.get("files_to_format", [])
        if not needs_black and "would reformat" in logs_text:
            needs_black = True
            files_to_format = re.findall(r"would reformat (.+\.py)", logs_text)

        if not os.path.exists(repo_local_path):
            return {
                "error": f"repo_local_path '{repo_local_path}' existiert nicht.",
                "detected_problem_files": py_files,
            }

        os.chdir(repo_local_path)
        fixed_files = []

        for file in list(set(py_files + files_to_format)):
            file = file.strip()
            if not os.path.exists(file):
                continue
            try:
                if needs_black or file in files_to_format:
                    subprocess.run(["black", file], check=False)
                subprocess.run(["isort", file], check=False)
                fixed_files.append(file)
            except Exception as e:
                print(f"Fehler beim Fixen von {file}: {e}")

        if fixed_files:
            subprocess.run(["git", "add"] + fixed_files, check=False)
            subprocess.run(
                ["git", "commit", "-m", f"Auto Fix für CI Run {run_id}"], check=False
            )
            subprocess.run(["git", "push"], check=False)

        # Workflow neu starten
        workflow_dispatch_msg = "Workflow Restart nicht durchgeführt"
        if workflow_id:
            dispatch_url = (
                f"https://api.github.com/repos/{repo_full_name}/actions/workflows/"
                f"{workflow_id}/dispatches"
            )
            resp = requests.post(dispatch_url, headers=headers, json={"ref": branch})
            if resp.status_code in (201, 204):
                workflow_dispatch_msg = "Workflow erfolgreich erneut gestartet"
            else:
                workflow_dispatch_msg = (
                    f"Workflow Restart nicht möglich: {resp.status_code} {resp.text}"
                )

        return {
            "run_id": run_id,
            "workflow_name": workflow_name,
            "html_url": html_url,
            "ai_analysis": ai_result,
            "detected_problem_files": py_files,
            "fixed_files": fixed_files,
            "git_push": (
                f"{len(fixed_files)} Dateien automatisch gefixt"
                if fixed_files
                else "Keine Änderungen notwendig"
            ),
            "workflow_restart": workflow_dispatch_msg,
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Natürliche Sprachbefehle
# ---------------------------------------------------------------------------


class CommandRequest(BaseModel):
    command: str


@router.post("/command")
def handle_command(req: CommandRequest):
    command_text = req.command.lower()

    url_match = re.search(r"(https://github\.com/[\w\-/]+)", command_text)
    repo_url = url_match.group(1) if url_match else None

    github = GitHubService(token_store.ACCESS_TOKEN)

    if "überwache mein repo" in command_text and repo_url:
        repo_local_path = clone_repo(repo_url)
        analysis = ai_analyze_repo(repo_url)

        match = re.match(r"https://github\.com/([^/]+)/([^/]+)(?:\.git)?", repo_url)
        if not match:
            raise HTTPException(status_code=400, detail="Ungültige GitHub URL")

        owner, repo = match.groups()
        full_name = f"{owner}/{repo}"

        runs = github.latest_workflow_runs(full_name, limit=1)
        workflow_info = {}
        if runs:
            last_run = runs[0]
            run_id = last_run["id"]
            logs_text = _download_logs(full_name, run_id)
            workflow_info = {
                "last_run": last_run,
                "logs_ai_analysis": ai_explain_log(logs_text),
            }

        return {
            "message": f"Repo {repo_url} überwacht.",
            "analysis": analysis,
            "workflow": workflow_info,
            "local_path": repo_local_path,
        }

    elif "fix letzte ci" in command_text and repo_url:
        repo_local_path = clone_repo(repo_url)
        full_name = "/".join(repo_url.split("/")[-2:])
        runs = github.latest_workflow_runs(full_name, limit=1)
        if not runs:
            return {"message": "Keine Workflow-Runs gefunden"}
        result = ci_full_auto_fix(
            repo_full_name=full_name,
            run_id=runs[0]["id"],
            repo_local_path=repo_local_path,
        )
        return {"message": "Auto-Fix durchgeführt", "result": result}

    else:
        return {
            "message": "Befehl nicht erkannt. Beispiele: 'Überwache mein Repo <URL>'"
        }
