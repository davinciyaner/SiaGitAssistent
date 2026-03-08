import os
import subprocess


def handle_branch(path):
    os.chdir(path)
    result = subprocess.run(["git", "branch"], capture_output=True, text=True)
    return result.stdout + result.stderr
