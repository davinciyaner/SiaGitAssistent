import os
import subprocess

projects = {
    "backend": r""
}

DEFAULT_CONFIRM = True


def process_input(text, auto_confirm=True):
    text = text.lower()

    if "push" in text:
        return handle_project_action("push", text, auto_confirm)
    elif "commit" in text:
        return handle_project_action("commit", text, auto_confirm)
    elif "init" in text:
        return handle_project_action("init", text, auto_confirm)
    elif "status" in text:
        return handle_project_action("status", text, auto_confirm)
    elif "add" in text:
        return handle_project_action("add", text, auto_confirm)
    elif "branch" in text:
        return handle_project_action("check_branch", text, auto_confirm)
    elif "checkout" in text:
        return handle_project_action("checkout", text, auto_confirm)
    elif "pr" in text or "pull request" in text:
        return handle_project_action("pull_request", text, auto_confirm)
    elif "merge pr" in text:
        return handle_project_action("merge_pr", text, auto_confirm)
    elif "merge" in text:
        return handle_project_action("merge", text, auto_confirm)
    elif "remote" in text:
        return handle_project_action("remote", text, auto_confirm)
    elif ".gitignore" in text:
        return handle_project_action("gitignore", text, auto_confirm)
    else:
        return "Diesen Befehl kenne ich nicht"


def confirm_action(message, auto_confirm=True):
    if auto_confirm:
        return True
    return True

def set_remote_with_token(path, repo_url, token):
    # repo_url ohne https:// prefix
    url = repo_url.replace("https://", f"https://{token}@")
    subprocess.run(["git", "remote", "set-url", "origin", url], cwd=path)

def handle_init(path, auto_confirm=True):
    result = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
    if result.returncode == 0:
        return "Git-Repo erfolgreich initialisiert"
    return "Fehler beim Initialisieren: " + result.stderr

def handle_init_full(path, remote_url=None, auto_confirm=True):
    init_result = handle_init(path, auto_confirm)
    gitignore_result = handle_gitignore(path)
    add_result = handle_add(path)
    commit_result = handle_commit(path)

    push_result = ""
    if remote_url:
        remote_add_result = handle_remote_add(path, remote_url)
        push_result = handle_push(path, auto_confirm)
        return "\n".join([init_result, gitignore_result, add_result, commit_result, remote_add_result, push_result])
    else:
        return "\n".join([init_result, gitignore_result, add_result, commit_result])

def handle_gitignore(path):
    content = """
__pycache__/
*.pyc
*.pyo
*.pyd
*.env
*.venv
.idea/
.vscode/
    """
    with open(os.path.join(path, ".gitignore"), "w") as f:
        f.write(content)
    return ".gitignore erstellt"

def handle_remote_add(path, url):
    os.chdir(path)
    result = subprocess.run(["git", "remote", "add", "origin", url], capture_output=True, text=True)
    if result.returncode == 0:
        return "Remote erfolgreich hinzugefügt"
    return "Fehler beim Hinzufügen des Remote: " + result.stderr


def handle_push(path, auto_confirm=True):
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True
    )
    branch = result.stdout.strip()

    result = subprocess.run(
        ["git", "push", "-u", "origin", branch],
        cwd=path,
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        return f"Push erfolgreich auf {branch}\n" + result.stdout
    return "Push fehlgeschlagen\n" + result.stderr


def handle_commit(path):
    os.chdir(path)
    subprocess.run(["git", "add", "."])
    result = subprocess.run(["git", "commit", "-m", "Auto commit by SIA"], capture_output=True, text=True)
    if result.returncode == 0:
        return "Commit erfolgreich\n" + result.stdout
    return "Commit fehlgeschlagen\n" + result.stderr


def handle_add(path, text=None):
    os.chdir(path)
    if text:
        words = text.split()
        try:
            index = words.index("add") + 1
            if index < len(words):
                file_to_add = words[index]
                subprocess.run(["git", "add", file_to_add])
                return f"{file_to_add} wurde zum Commit vorgemerkt."
        except ValueError:
            pass
    subprocess.run(["git", "add", "."])
    return "Alle Änderungen wurden zum Commit vorgemerkt."


def handle_status(path):
    os.chdir(path)
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    return result.stdout + result.stderr


def handle_branch(path):
    os.chdir(path)
    result = subprocess.run(["git", "branch"], capture_output=True, text=True)
    return result.stdout + result.stderr


def handle_checkout(text, path):
    words = text.split()
    if "checkout" in words:
        index = words.index("checkout") + 1
        branch = words[index] if index < len(words) else ""
        os.chdir(path)
        result = subprocess.run(["git", "checkout", branch], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Branch gewechselt zu {branch}"
        return "Fehler beim Checkout\n" + result.stderr
    return "Branch nicht angegeben"


def handle_merge_pr(text, path, auto_confirm=True):
    words = text.split()
    try:
        pr_index = words.index("pr")
        source_branch = words[pr_index + 1]
        in_index = words.index("in")
        target_branch = words[in_index + 1]
    except:
        return "Format: merge pr <source_branch> in <target_branch> (projekt)"
    if not confirm_action(f"Merge PR {source_branch} -> {target_branch}", auto_confirm):
        return "Merge abgebrochen"
    os.chdir(path)
    result = subprocess.run(
        ["gh", "pr", "merge", "--head", source_branch, "--base", target_branch, "--merge", "--delete-branch"],
        capture_output=True, text=True)
    return result.stdout + result.stderr if result.returncode != 0 else f"PR gemerged: {source_branch} -> {target_branch}"


def handle_merge(text, path, auto_confirm=True):
    words = text.split()
    try:
        source_branch = words[words.index("merge") + 1]
        target_branch = words[words.index("in") + 1]
    except:
        return "Format: merge <source_branch> in <target_branch>"
    os.chdir(path)
    subprocess.run(["git", "checkout", target_branch])
    subprocess.run(["git", "merge", source_branch])
    subprocess.run(["git", "push", "origin", target_branch])
    return f"{source_branch} wurde in {target_branch} gemerged."


def handle_pull_request(text, path, auto_confirm=True):
    words = text.split()
    try:
        pr_index = words.index("pr")
        source_branch = words[pr_index + 1]
        in_index = words.index("in")
        target_branch = words[in_index + 1]
    except:
        return "Format: pr <source_branch> in <target_branch> (projekt)"
    if not confirm_action(f"PR erstellen {source_branch} -> {target_branch}", auto_confirm):
        return "PR abgebrochen"
    os.chdir(path)
    result = subprocess.run(["gh", "pr", "create",
                             "--base", target_branch,
                             "--head", source_branch,
                             "--title", f"Merge {source_branch} in {target_branch}",
                             "--body", "PR created by SIA"], capture_output=True, text=True)
    output = result.stdout + result.stderr
    if "already exists" in output:
        return f"PR existiert bereits: {source_branch} -> {target_branch}"
    if result.returncode == 0:
        return f"PR erfolgreich erstellt: {source_branch} -> {target_branch}"
    return f"Fehler beim Erstellen des PR: {output}"


def run_git_command(action, path, text=None):
    if action == "status":
        return handle_status(path)
    elif action == "check_branch":
        return handle_branch(path)
    elif action == "commit":
        return handle_commit(path)
    elif action == "push":
        return handle_push(path)
    elif action == "add":
        return handle_add(path, text)
    return f"Unbekannter Befehl: {action}"


def handle_project_action(action, text, auto_confirm=True):
    default_name, default_path = list(projects.items())[0]

    if action == "init":
        try:
            args = text.split("init", 1)[1].strip().split()
            path = args[0]  # erstes Argument = Pfad
            remote_url = args[1] if len(args) > 1 else None  # optionales zweites Argument = Remote
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            return f"Fehler beim Verarbeiten des Pfads: {e}"

        # Git init + .gitignore + Add + Commit
        init_result = handle_init(path, auto_confirm)
        gitignore_result = handle_gitignore(path)
        add_result = handle_add(path)
        commit_result = handle_commit(path)

        push_result = ""
        if remote_url:
            remote_add_result = handle_remote_add(path, remote_url)
            push_result = handle_push(path, auto_confirm)

        return "\n".join(filter(None, [init_result, gitignore_result, add_result, commit_result, push_result]))

    for name, path in projects.items():
        if name in text.lower():
            if action == "push":
                return handle_push(path, auto_confirm)
            elif action == "commit":
                return handle_commit(path)
            elif action == "add":
                return handle_add(path, text)
            elif action == "status":
                return handle_status(path)
            elif action == "checkout":
                return handle_checkout(text, path)
            elif action == "merge_pr":
                return handle_merge_pr(text, path, auto_confirm)
            elif action == "merge":
                return handle_merge(text, path, auto_confirm)
            elif action == "pull_request":
                return handle_pull_request(text, path, auto_confirm)
            else:
                return run_git_command(action, path, text)

    if action == "push":
        return handle_push(default_path, auto_confirm)
    elif action == "commit":
        return handle_commit(default_path)
    elif action == "add":
        return handle_add(default_path, text)
    elif action == "status":
        return handle_status(default_path)

    return "Projekt nicht gefunden"
