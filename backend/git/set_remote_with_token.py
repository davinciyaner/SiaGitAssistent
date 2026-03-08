import subprocess


def set_remote_with_token(path, remote_url, token):

    token_url = remote_url.replace("https://", f"https://{token}@")

    result = subprocess.run(
        ["git", "remote"],
        cwd=path,
        capture_output=True,
        text=True
    )

    if "origin" in result.stdout:
        subprocess.run(
            ["git", "remote", "set-url", "origin", token_url],
            cwd=path,
            check=True
        )
    else:
        subprocess.run(
            ["git", "remote", "add", "origin", token_url],
            cwd=path,
            check=True
        )

    return "Remote erfolgreich gesetzt"