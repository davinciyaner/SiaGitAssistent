import subprocess


def handle_merge(path, target_branch):
    # Aktuellen Branch ermitteln
    current_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if not target_branch:
        return "Dein Branch fehlt für Merge"

    try:
        subprocess.run(["git", "merge", target_branch], cwd=path, check=True, text=True)
        return f"Branch '{target_branch}' erfolgreich in '{current_branch}' gemerged"
    except subprocess.CalledProcessError as e:
        return f"Merge fehlgeschlagen: {e.stderr}"
