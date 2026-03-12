import subprocess


def handle_commit(path):
    result = subprocess.run(["git", "commit", "-m", "Auto commit by SIA"], cwd=path,
                            capture_output=True, text=True)
    if result.returncode == 0:
        return "Commit erfolgreich"
    return f"Commit fehlgeschlagen: {result.stderr}"
