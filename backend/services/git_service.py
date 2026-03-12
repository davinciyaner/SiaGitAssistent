import httpx


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
