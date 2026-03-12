from backend.config.project_manager import load_projects, save_projects
import subprocess
import os


def handle_init(name: str, path: str, remote_url: str = None):
    """
    Initialisiert ein Projekt:
    - Wenn remote_url gegeben ist → Klont das Repo
    - Sonst → Init neues lokales Git-Repo
    """
    # Projekte laden
    projects = load_projects()

    if name in projects:
        path = projects[name]["path"]
        return f"Projekt '{name}' existiert bereits unter {path}"

    # Wenn Pfad nicht existiert, erstellen
    if not os.path.exists(path):
        os.makedirs(path)

    if remote_url:
        # Existierendes GitHub Repo klonen
        result = subprocess.run(
            ["git", "clone", remote_url, path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            return f"Fehler beim Klonen von GitHub: {result.stderr}"
        msg = f"Projekt '{name}' erfolgreich von GitHub geklont"
    else:
        # Neues lokales Repo init
        result = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
        if result.returncode != 0:
            return f"Fehler beim Initialisieren: {result.stderr}"
        msg = f"Projekt '{name}' erfolgreich initialisiert als Git-Repo"

    # Projekt in projects.json speichern
    projects[name] = {"path": path}
    save_projects(projects)

    return msg
