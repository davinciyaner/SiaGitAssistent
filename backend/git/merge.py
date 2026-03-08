import os
import subprocess


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