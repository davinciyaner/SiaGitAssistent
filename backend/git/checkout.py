import subprocess


def handle_checkout(path, branch_name):
    try:
        subprocess.run(["git", "checkout", branch_name], cwd=path, check=True)
        return f"Ich habe deinen Branch '{branch_name}' ausgecheckt"
    except subprocess.CalledProcessError as e:
        return f"Checkout fehlgeschlagen: {e.stderr}"
