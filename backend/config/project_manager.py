import json
FILE = "backend/config/projects.json"

def load_projects():
    try:
        with open(FILE) as f:
            return json.load(f).get("projects", {})
    except:
        return {}

def save_projects(projects):
    # Immer im Format {"projects": {...}} speichern
    with open(FILE, "w") as f:
        json.dump({"projects": projects}, f, indent=4)