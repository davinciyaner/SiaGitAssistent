import httpx


def create_github_repo(name, private=True):
    import backend.auth.token_store as token_store

    token = token_store.ACCESS_TOKEN
    if not token:
        return "Kein GitHub Token gefunden"

    headers = {"Authorization": f"token {token}"}
    data = {"name": name, "private": private}

    res = httpx.post("https://api.github.com/user/repos", headers=headers, json=data)
    if res.status_code == 201:
        return f"GitHub Repo '{name}' erfolgreich erstellt"
    else:
        return f"Fehler beim Erstellen des Repos: {res.status_code} {res.text}"
