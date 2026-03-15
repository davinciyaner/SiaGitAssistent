from backend.config.project_manager import load_projects, save_projects
from backend.git.add import handle_add
from backend.git.branch import handle_branch
from backend.git.checkout import handle_checkout
from backend.git.commit import handle_commit
from backend.git.init_full import handle_init_full
from backend.git.merge_pullrequest import handle_merge_pr
from backend.git.push import handle_push
from backend.git.status import handle_status
from backend.services.pipeline import (
    auto_pipeline,
    create_pipeline,
    get_pipeline_logs,
    get_pipeline_status,
    run_pipeline,
)


def process_input(command_text: str, project_path: str = None, token: str = None):
    projects = load_projects()
    command_text = command_text.strip()

    if not command_text:
        return "Bitte gib einen Befehl ein."

    words = command_text.split()
    command = words[0].lower()

    if command == "create":

        if len(words) < 3:
            return "Syntax: create pipeline <projekt>"

        if words[1] == "pipeline":

            project_name = words[2]

            if project_name not in projects:
                return f"Ich habe das Projekt '{project_name}' nicht gefunden."

            path = projects[project_name]["path"]

            return create_pipeline(path)

    project_name = words[1] if len(words) > 1 else None
    project_path = words[2] if len(words) > 2 else None
    remote_url = words[3] if len(words) > 3 else None

    # INIT MUSS VOR DER PROJEKT PRÜFUNG KOMMEN
    if command == "init":

        if not project_name or not project_path:
            return "Syntax: init <projektname> <pfad> <optional: repo_url>"

        from backend.git.init import handle_init

        return handle_init(project_name, project_path, remote_url)

    # ERST HIER prüfen ob Projekt existiert
    if project_name not in projects:
        return f"Ich habe das Projekt '{project_name}' nicht gefunden."

    path = projects[project_name]["path"]

    if command == "init full":
        if project_name in projects:
            path = projects[project_name]["path"]
        else:
            if not project_path:
                return "Dieses Projekt habe ich nicht, bitte füge es hinzu."
            path = project_path

        result = handle_init_full(path, remote_url)
        projects[project_name] = {"path": path}
        save_projects(projects)
        return result

    if project_name not in projects:
        return f"Ich habe das Projekt '{project_name}' nicht gefunden."
    path = projects[project_name]["path"]

    if command == "push":
        return handle_push(path, remote_url)
    elif command == "commit":
        return handle_commit(path)
    elif command == "add":
        return handle_add(path)
    elif command == "status":
        return handle_status(path)
    elif command == "create":
        if len(words) < 3:
            return "Syntaxfehler: create pipeline <projekt>"

        if words[1] == "pipeline":
            project_name = words[2]

            if project_name not in projects:
                return f"Ich habe das Projekt '{project_name}' nicht gefunden."

            path = projects[project_name]["path"]

            # Optional: GitHub owner, repo und token übergeben
            owner = "davinciyaner"
            repo = "SiaGitAssistent"
            token = None  # hier dein GitHub Token eintragen, falls nötig

            return create_pipeline(path, owner, repo, token)
    elif command == "merge":
        if "in" not in words:
            return "Syntaxfehler: 'merge <projekt> in <branch>'"

        in_index = words.index("in")
        project_name = words[1]
        target_branch = words[in_index + 1] if len(words) > in_index + 1 else None

        if project_name not in projects:
            return f"Ich habe das Projekt '{project_name}' nicht gefunden."

        path = projects[project_name]["path"]
        from backend.git.merge import handle_merge

        return handle_merge(path, target_branch)
    elif command == "pr":
        if "in" not in words:
            return "Syntaxfehler: 'pr <projekt> in <branch>'"

        in_index = words.index("in")
        project_name = words[1]
        target_branch = words[in_index + 1] if len(words) > in_index + 1 else None

        if project_name not in projects:
            return f"Ich habe das Projekt '{project_name}' nicht gefunden."

        path = projects[project_name]["path"]
        from backend.git.pullrequest import handle_pull_request

        return handle_pull_request(path, target_branch)
    elif command == "checkout":
        branch_name = words[2] if len(words) > 2 else None
        if not branch_name:
            return "Bitte gib einen Branchnamen für den Checkout an."
        return handle_checkout(path, branch_name)
    elif command == "merge pr":
        return handle_merge_pr(path)
    elif command == "branch":
        branch_name = words[2] if len(words) > 2 else None
        push_flag = "--push" in words
        return handle_branch(path, branch_name, push_to_github=push_flag)
    elif command == "pipeline":
        if len(words) < 4:
            return "Syntax: pipeline <run|status|logs> <owner> <repo>"

        action = words[1]
        owner = words[2]
        repo = words[3]

        if not token:
            return "GitHub Token fehlt."

        if action == "run":
            return run_pipeline(owner, repo, token)
        elif action == "status":
            return get_pipeline_status(owner, repo, token)
        elif action == "logs":
            return get_pipeline_logs(owner, repo, token)
        else:
            return "Unbekannte Pipeline Aktion"
    elif command == "autopipeline":

        if len(words) < 3:
            return "Syntax: autopipeline <owner> <repo>"

        owner = words[1]
        repo = words[2]

        return auto_pipeline(owner, repo, token)
    else:
        return "Unbekannter Befehl"
