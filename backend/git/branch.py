import subprocess
from backend.auth import token_store

def handle_branch(path, branch_name=None, push_to_github=False):
    if not branch_name:
        return "Bitte gib einen Branchnamen an."

    msg = ""

    try:
        # Prüfen ob Branch bereits existiert
        existing_branches = subprocess.run(
            ["git", "branch", "--list", branch_name],
            cwd=path,
            capture_output=True,
            text=True
        ).stdout.strip()

        if existing_branches:
            msg += f"Dieser Branch '{branch_name}' existiert bereits lokal."
        else:
            subprocess.run(["git", "branch", branch_name], cwd=path, check=True)
            msg += f"Ich habe den Branch '{branch_name}' lokal erstellt."
    except subprocess.CalledProcessError as e:
        return f"Fehler beim Erstellen des Branches: {e.stderr.strip()}"

    if push_to_github:
        if not token_store.ACCESS_TOKEN:
            return msg + "Kein GitHub-Token verfügbar – Ich konnte deinen Branch nicht pushen."

        remote_url_res = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=path,
            capture_output=True,
            text=True
        )
        remote_url = remote_url_res.stdout.strip()
        if not remote_url:
            return msg + "Ich habe kein Remote-Repository gefunden"

        if remote_url.startswith("https://"):
            remote_url_clean = remote_url.split("@")[-1]
            token_url = f"https://{token_store.ACCESS_TOKEN}@{remote_url_clean}"
            subprocess.run(["git", "remote", "set-url", "origin", token_url], cwd=path, check=True)

        try:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=path,
                check=True,
                capture_output=True,
                text=True
            )
            msg += f"Ich habe deinen Branch '{branch_name}' erfolgreich zu GitHub gepushed"
        except subprocess.CalledProcessError as e:
            stderr_msg = e.stderr.strip() if e.stderr else "Unbekannter Fehler"
            msg += f"Der Push zu GitHub ist fehlgeschlagen: {stderr_msg}"

    return msg