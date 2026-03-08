import os
import subprocess


def handle_checkout(text, path):
    words = text.split()
    if "checkout" in words:
        index = words.index("checkout") + 1
        branch = words[index] if index < len(words) else ""
        os.chdir(path)
        result = subprocess.run(["git", "checkout", branch], capture_output=True, text=True)
        if result.returncode == 0:
            return f"Branch gewechselt zu {branch}"
        return "Fehler beim Checkout\n" + result.stderr
    return "Branch nicht angegeben"
