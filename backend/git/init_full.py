from backend.auth.token_store import ACCESS_TOKEN
from backend.git.add import handle_add
from backend.git.commit import handle_commit
from backend.git.create_github_repo import create_github_repo
from backend.git.gitignore import handle_gitignore
from backend.git.init import handle_init
from backend.git.push import handle_push
from backend.git.set_remote_with_token import set_remote_with_token


def handle_init_full(path, remote_url=None):
    init_result = handle_init(path)
    gi_result = handle_gitignore(path)
    add_result = handle_add(path)
    commit_result = handle_commit(path)

    push_result = ""

    if remote_url and ACCESS_TOKEN:
        # Repo auf GitHub erstellen
        repo_name = remote_url.split("/")[-1].replace(".git","")
        create_result = create_github_repo(repo_name)
        print(create_result)

        # Remote mit Token setzen
        set_remote_with_token(path, remote_url, ACCESS_TOKEN)
        push_result = handle_push(path)

    return "\n".join(filter(None, [init_result, gi_result, add_result, commit_result, push_result]))