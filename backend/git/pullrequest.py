import os
import subprocess

from backend.git.confirm_action import confirm_action


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
