import os
import subprocess


def handle_status(path):
    os.chdir(path)
    result = subprocess.run(["git", "status"], capture_output=True, text=True)
    return result.stdout + result.stderr
