import os


def handle_gitignore(path):
    content = "__pycache__/\n*.pyc\n*.env\n.venv/\n.idea/\n.vscode/\n"
    with open(os.path.join(path, ".gitignore"), "w") as f:
        f.write(content)
    return ".gitignore erstellt"
