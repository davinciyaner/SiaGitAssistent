
def process_input(text, project_path=None):
    from backend.api.FastApi import projects, save_projects
    from backend.git.init_full import handle_init_full

    text = text.strip()
    words = text.split()

    if len(words) == 0:
        return "Kein Befehl angegeben"

    command = words[0].lower()
    project_name = words[1] if len(words) > 1 else None
    remote_url = words[2] if len(words) > 2 else None

    # Wenn Projektname leer, versuchen wir, aus Projekten zu holen
    if not project_name and command in projects:
        project_name = command

    if command == "init":
        # Projekt existiert schon → Pfad aus projects.json
        if project_name in projects:
            path = projects[project_name]["path"]
        else:
            # Pfad muss vom Frontend übergeben werden
            if not project_path:
                return "Bitte Pfad für das neue Projekt angeben"
            path = project_path

        result = handle_init_full(path, remote_url)

        # Projekt speichern, falls neu
        if project_name not in projects:
            projects[project_name] = {"path": path}
            save_projects(projects)

        return f"{result}\nProjekt '{project_name}' gespeichert!"

    # Andere Git-Befehle für bestehende Projekte
    if project_name not in projects:
        return f"Projekt '{project_name}' nicht gefunden"

    path = projects[project_name]["path"]

    if command == "push":
        from backend.git.push import handle_push
        return handle_push(path)
    elif command == "commit":
        from backend.git.commit import handle_commit
        return handle_commit(path)
    elif command == "add":
        from backend.git.add import handle_add
        return handle_add(path)
    elif command == "status":
        from backend.git.status import handle_status
        return handle_status(path)
    elif command == "branch":
        from backend.git.branch import handle_branch
        return handle_branch(path)
    elif command == "checkout":
        from backend.git.checkout import handle_checkout
        return handle_checkout(text, path)
    elif command in ["pr", "pull"]:
        from backend.git.pullrequest import handle_pull_request
        return handle_pull_request(text, path)
    elif command == "merge":
        if "pr" in words:
            from backend.git.merge_pullrequest import handle_merge_pr
            return handle_merge_pr(text, path)
        else:
            from backend.git.merge import handle_merge
            return handle_merge(text, path)
    elif command == "remote":
        from backend.git.remote import handle_remote_add
        return handle_remote_add(path)
    elif ".gitignore" in text:
        from backend.git.gitignore import handle_gitignore
        return handle_gitignore(path)
    else:
        return "Diesen Befehl kenne ich nicht"