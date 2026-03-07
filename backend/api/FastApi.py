# backend/api/FastApi.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx, os, subprocess

from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ACCESS_TOKEN = None

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Git Projects ---
projects = {
    "backend": r"C:\Users\paust\PycharmProjects\DevOpsAgent"
}

# --- Models ---
class Command(BaseModel):
    command: str

# --- OAuth Routes ---
@app.get("/auth/github/login")
def github_login():
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return RedirectResponse(url)

@app.get("/auth/github/callback")
async def github_callback(code: str):
    global ACCESS_TOKEN
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            }
        )
    ACCESS_TOKEN = res.json()["access_token"]
    print("GitHub OAuth Token:", ACCESS_TOKEN)
    return RedirectResponse("http://localhost:5173/login-success")

# --- Git Helper Functions ---
def handle_gitignore(path):
    content = "__pycache__/\n*.pyc\n*.env\n.venv/\n.idea/\n.vscode/\n"
    with open(os.path.join(path, ".gitignore"), "w") as f:
        f.write(content)
    return ".gitignore erstellt"

def handle_init(path):
    result = subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True)
    if result.returncode == 0:
        return "Git-Repo erfolgreich initialisiert"
    return f"Fehler beim Initialisieren: {result.stderr}"

def handle_add(path):
    subprocess.run(["git", "add", "."], cwd=path)
    return "Alle Änderungen wurden zum Commit vorgemerkt."

def handle_commit(path):
    result = subprocess.run(["git", "commit", "-m", "Auto commit by SIA"], cwd=path,
                            capture_output=True, text=True)
    if result.returncode == 0:
        return "Commit erfolgreich"
    return f"Commit fehlgeschlagen: {result.stderr}"

def set_remote_with_token(path, remote_url, token):
    token_url = remote_url.replace("https://", f"https://{token}@")
    subprocess.run(["git", "remote", "set-url", "origin", token_url], cwd=path, check=True)
    return f"Remote mit Token gesetzt: {remote_url}"

def handle_push(path):
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=path, capture_output=True, text=True
    ).stdout.strip()
    result = subprocess.run(["git", "push", "-u", "origin", branch],
                            cwd=path, capture_output=True, text=True)
    if result.returncode == 0:
        return f"Push erfolgreich auf {branch}"
    return f"Push fehlgeschlagen: {result.stderr}"

# --- Init Full Function ---
def handle_init_full(path, remote_url=None):
    global ACCESS_TOKEN
    init_result = handle_init(path)
    gi_result = handle_gitignore(path)
    add_result = handle_add(path)
    commit_result = handle_commit(path)

    push_result = ""
    if remote_url and ACCESS_TOKEN:
        set_remote_with_token(path, remote_url, ACCESS_TOKEN)
        push_result = handle_push(path)

    return "\n".join(filter(None, [init_result, gi_result, add_result, commit_result, push_result]))

# --- Command Endpoint ---
@app.post("/command")
def run_command(cmd: Command):
    text = cmd.command.lower()
    default_path = list(projects.values())[0]

    if text.startswith("init"):
        parts = text.split()
        path = parts[1] if len(parts) > 1 else default_path
        remote_url = parts[2] if len(parts) > 2 else None
        return {"output": handle_init_full(path, remote_url)}

    return {"output": "Nur 'init <path> <optional remote_url>' unterstützt momentan"}