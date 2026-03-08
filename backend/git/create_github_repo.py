import httpx

from backend.auth.token_store import ACCESS_TOKEN


def create_github_repo(repo_name, private=True):
    if not ACCESS_TOKEN:
        return "Kein GitHub Token vorhanden"

    headers = {"Authorization": f"token {ACCESS_TOKEN}"}
    data = {"name": repo_name, "private": private}

    with httpx.Client() as client:
        res = client.post("https://api.github.com/user/repos", headers=headers, json=data)

    if res.status_code in [201, 202]:
        return f"GitHub Repo '{repo_name}' erfolgreich erstellt"
    elif res.status_code == 422:
        return f"Repo '{repo_name}' existiert bereits"
    else:
        return f"Fehler beim Erstellen des Repos: {res.text}"