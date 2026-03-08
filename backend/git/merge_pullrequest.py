import os
import subprocess


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