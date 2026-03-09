import subprocess


def handle_add(path):
    subprocess.run(["git", "add", "."], cwd=path)
    return "Ich habe alle Änderungen zum Commit vorgemerkt."
