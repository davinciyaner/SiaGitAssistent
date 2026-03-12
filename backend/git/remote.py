import os
import subprocess


def handle_remote_add(path, url):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    os.chdir(path)
    result = subprocess.run(
        ["git", "remote", "add", "origin", url], capture_output=True, text=True
    )
    if result.returncode == 0:
        return "Remote erfolgreich hinzugefügt"
    return "Fehler beim Hinzufügen des Remote: " + result.stderr
