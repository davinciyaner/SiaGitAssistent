import subprocess


def handle_add(path):
    subprocess.run(["git", "add", "."], cwd=path)
    return "Alle Änderungen wurden zum Commit vorgemerkt."
