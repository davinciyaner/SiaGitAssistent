import subprocess
from backend.auth import token_store


def handle_pull_request(path, target_branch):
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if not token_store.ACCESS_TOKEN:
        return "Kein GitHub-Token verfügbar – PR nicht erstellt"

    if not target_branch:
        return "Ziel-Branch fehlt für PR"

    remote_url_res = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    remote_url = remote_url_res.stdout.strip()
    if not remote_url:
        return "Kein Remote-Repository gefunden"

    import re

    match = re.search(r"github.com[:/](.+)/(.+)\.git", remote_url)
    if not match:
        return "Repo URL konnte nicht geparst werden"
    owner, repo = match.groups()

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {token_store.ACCESS_TOKEN}"}
    data = {
        "title": f"PR: {current_branch} → {target_branch}",
        "head": current_branch,
        "base": target_branch,
        "body": f"Automatisch erstellter PR von Branch {current_branch} in {target_branch}",
    }

    try:
        import requests

        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 201:
            return f"Pull Request erfolgreich erstellt: {res.json().get('html_url')}"
        else:
            return f"PR konnte nicht erstellt werden: {res.text}"
    except Exception as e:
        return f"Fehler beim Erstellen des PR: {str(e)}"
