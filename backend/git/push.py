import subprocess

from backend.auth import token_store


def handle_push(path, remote_url=None):
    branch_res = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
    )
    branch = branch_res.stdout.strip()
    if not branch:
        return "Aktueller Branch konnte nicht ermittelt werden"

    msg = ""

    if remote_url and token_store.ACCESS_TOKEN:
        if "@" not in remote_url.split("https://")[-1]:
            token_url = remote_url.replace(
                "https://", f"https://{token_store.ACCESS_TOKEN}@"
            )
            subprocess.run(
                ["git", "remote", "set-url", "origin", token_url], cwd=path, check=True
            )

    try:
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            cwd=path,
            check=True,
            capture_output=True,
            text=True,
        )
        msg = f"Push erfolgreich auf {branch}"
    except subprocess.CalledProcessError as e:
        msg = f"Push zu GitHub fehlgeschlagen: {e.stderr.strip()}"

    return msg
