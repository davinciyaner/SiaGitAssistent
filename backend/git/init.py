import subprocess


def handle_init(path):
    result = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
    if result.returncode == 0:
        return "Git-Repo erfolgreich initialisiert"
    return f"Fehler beim Initialisieren: {result.stderr}"