import httpx
import subprocess
import os


class GitHubService:
    def __init__(self, token):
        self.token = token

    def create_repo(self, name):
        headers = {"Authorization": f"token: {self.token}"}

        data = {"name": name, "private": False}

        res = httpx.post(
            "https://api.github.com/user/repos", headers=headers, json=data
        )

        return res.json()


def clone_repo(repo_url: str, target_dir: str = "repos"):
    os.makedirs(target_dir, exist_ok=True)

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(target_dir, repo_name)

    if os.path.exists(repo_path):
        return repo_path

    subprocess.run(["git", "clone", repo_url, repo_path], check=True)

    return repo_path
