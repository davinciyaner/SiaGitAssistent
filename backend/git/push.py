import subprocess


def handle_push(path):
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path, capture_output=True, text=True
    ).stdout.strip()
    result = subprocess.run(["git", "push", "-u", "origin", branch],
                            cwd=path, capture_output=True, text=True)
    if result.returncode == 0:
        return f"Push erfolgreich auf {branch}"
    return f"Push fehlgeschlagen: {result.stderr}"