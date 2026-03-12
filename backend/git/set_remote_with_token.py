import subprocess


def set_remote_with_token(path, remote_url, token):
    token_url = remote_url.replace("https://", f"https://{token}@")
    subprocess.run(["git", "remote", "add", "origin", token_url], cwd=path, check=False)
    subprocess.run(["git", "remote", "set-url", "origin", token_url], cwd=path, check=True)
    return f"Remote mit Token gesetzt: {remote_url}"
