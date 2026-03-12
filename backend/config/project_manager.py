import json
import os

PROJECT_FILE = "backend/config/projects.json"


def load_projects():
    if not os.path.exists(PROJECT_FILE):
        return {}

    with open(PROJECT_FILE, "r") as f:
        data = json.load(f)

    projects = data.get("projects", {})
    clean_projects = {}
    for name, value in projects.items():

        if isinstance(value, dict) and value.get("path"):
            clean_projects[name] = value

        elif value == "" or value is None:
            continue

    return clean_projects


def save_projects(projects):
    clean_projects = {}

    for name, value in projects.items():
        if isinstance(value, dict) and value.get("path"):
            clean_projects[name] = value

    data = {"projects": clean_projects}

    with open(PROJECT_FILE, "w") as f:
        json.dump(data, f, indent=4)
