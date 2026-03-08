import backend.auth.token_store as token_store
from backend.git.add import handle_add
from backend.git.commit import handle_commit
from backend.git.create_github_repo import create_github_repo
from backend.git.gitignore import handle_gitignore
from backend.git.init import handle_init
from backend.git.push import handle_push
from backend.git.set_remote_with_token import set_remote_with_token

def handle_init_full(path, remote_url=None):
    # 1. Init, gitignore, add, commit lokal
    init_result = handle_init(path)
    gi_result = handle_gitignore(path)
    add_result = handle_add(path)
    commit_result = handle_commit(path)

    push_result = ""

    # 2. Nur wenn Remote-URL und Token vorhanden
    if remote_url and token_store.ACCESS_TOKEN:
        # Name des Repos aus URL
        repo_name = remote_url.rstrip(".git").split("/")[-1]

        # 2a. Repo auf GitHub erstellen (private)
        create_result = create_github_repo(repo_name, private=True)
        print("GitHub Repo creation:", create_result)

        # 2b. Remote mit Token setzen
        set_remote_with_token(path, remote_url, token_store.ACCESS_TOKEN)

        # 2c. Push zum Remote
        push_result = handle_push(path)

    return "\n".join(filter(None, [init_result, gi_result, add_result, commit_result, push_result]))