from backend.config.project_manager import load_projects, save_projects
from backend.git.init_full import handle_init_full


def process_input(command_text: str, project_path: str = None):

    projects = load_projects()

    command_text = command_text.strip()

    if not command_text:
        return "Kein Befehl angegeben"

    words = command_text.split()

    command = words[0].lower()
    project_name = words[1] if len(words) > 1 else None
    remote_url = words[2] if len(words) > 2 else None

    if command == "init":

        if project_name in projects:
            path = projects[project_name]["path"]

        else:
            if not project_path:
                return "Projekt nicht registriert"

            path = project_path

        result = handle_init_full(path, remote_url)

        projects[project_name] = {"path": path}
        save_projects(projects)

        return result

    if project_name not in projects:
        return f"Projekt '{project_name}' nicht gefunden"

    path = projects[project_name]["path"]

    from backend.git.push import handle_push
    from backend.git.commit import handle_commit
    from backend.git.add import handle_add
    from backend.git.status import handle_status

    if command == "push":
        return handle_push(path)

    elif command == "commit":
        return handle_commit(path)

    elif command == "add":
        return handle_add(path)

    elif command == "status":
        return handle_status(path)

    else:
        return "Unbekannter Befehl"