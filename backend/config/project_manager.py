import json
import os

PROJECT_FILE = "backend/config/projects.json"


def load_projects():
    if not os.path.exists(PROJECT_FILE):
        return {}

    with open(PROJECT_FILE, "r") as f:
        data = json.load(f)

    projects = data.get("projects", {})

    # 🧹 Leere oder kaputte Einträge entfernen
    clean_projects = {}

    for name, value in projects.items():

        # Fall 1: {"path": "..."}
        if isinstance(value, dict) and value.get("path"):
            clean_projects[name] = value

        # Fall 2: leerer String -> ignorieren
        elif value == "" or value is None:
            continue

    return clean_projects


def save_projects(projects):

    # Sicherheitsfilter gegen leere Projekte
    clean_projects = {}

    for name, value in projects.items():
        if isinstance(value, dict) and value.get("path"):
            clean_projects[name] = value

    data = {
        "projects": clean_projects
    }

    with open(PROJECT_FILE, "w") as f:
        json.dump(data, f, indent=4)