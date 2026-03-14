import httpx
import subprocess
import os

from fastapi import HTTPException
from github import Github


class GitHubService:
    def __init__(self, token):
        self.token = token
        self.client = Github(token)
        self.headers = {"Authorization": f"token {self.token}"}

    def create_repo(self, name):
        headers = {"Authorization": f"token: {self.token}"}

        data = {"name": name, "private": False}

        res = httpx.post(
            "https://api.github.com/user/repos", headers=headers, json=data
        )

        return res.json()

    def get_repo(self, full_name: str):
        """Liefert ein Repository-Objekt"""
        return self.client.get_repo(full_name)

    def list_issues(self, repo_full_name: str, state="open", limit=10):
        repo = self.get_repo(repo_full_name)
        issues = repo.get_issues(state=state)
        return [
            {"number": i.number, "title": i.title, "state": i.state, "url": i.html_url}
            for i in list(issues)[:limit]
        ]

    def list_pull_requests(self, repo_full_name: str, state="open", limit=10):
        repo = self.get_repo(repo_full_name)
        prs = repo.get_pulls(state=state)
        return [
            {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "url": pr.html_url,
            }
            for pr in list(prs)[:limit]
        ]

    def list_commits(self, repo_full_name: str, limit=10):
        repo = self.get_repo(repo_full_name)
        commits = repo.get_commits()
        return [
            {"sha": c.sha, "author": c.commit.author.name, "message": c.commit.message}
            for c in list(commits)[:limit]
        ]

    def repo_stats(self, repo_full_name: str):
        repo = self.get_repo(repo_full_name)
        return {
            "name": repo.name,
            "full_name": repo.full_name,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.watchers_count,
            "open_issues": repo.open_issues_count,
        }

    def list_workflows(self, repo_full_name: str):
        url = f"https://api.github.com/repos/{repo_full_name}/actions/workflows"
        res = httpx.get(url, headers=self.headers, timeout=10)

        if res.status_code == 404:
            raise HTTPException(
                status_code=404, detail="Repo oder Workflows nicht gefunden"
            )
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        data = res.json()
        return [
            {
                "id": wf["id"],
                "name": wf["name"],
                "path": wf["path"],
                "state": wf["state"],
            }
            for wf in data.get("workflows", [])
        ]

    def latest_workflow_runs(
        self, repo_full_name: str, workflow_id: int = None, limit: int = 5
    ):
        url = f"https://api.github.com/repos/{repo_full_name}/actions/runs?per_page={limit}"
        if workflow_id:
            url = f"https://api.github.com/repos/{repo_full_name}/actions/workflows/{workflow_id}/runs?per_page={limit}"

        res = httpx.get(url, headers=self.headers, timeout=10)
        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        data = res.json()
        return data.get("workflow_runs", [])

    def get_run_logs(self, repo_full_name: str, run_id: int):
        url = (
            f"https://api.github.com/repos/{repo_full_name}/actions/runs/{run_id}/logs"
        )
        res = httpx.get(url, headers=self.headers, timeout=20)
        if res.status_code != 200:
            raise HTTPException(
                status_code=res.status_code,
                detail="Logs konnten nicht abgerufen werden",
            )
        # GitHub liefert ZIP-Datei; hier nur URL zurück
        return {"logs_url": url}


def get_run_logs(self, repo_full_name: str, run_id: int):
    repo = self.get_repo(repo_full_name)
    # Download logs (GitHub liefert ZIP, hier nur Platzhalter)
    run = repo.get_workflow_run(run_id)
    logs_url = run.logs_url
    return {"logs_url": logs_url}


def clone_repo(repo_url: str, target_dir: str = "repos"):
    os.makedirs(target_dir, exist_ok=True)

    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_path = os.path.join(target_dir, repo_name)

    if os.path.exists(repo_path):
        return repo_path

    subprocess.run(["git", "clone", repo_url, repo_path], check=True)

    return repo_path
