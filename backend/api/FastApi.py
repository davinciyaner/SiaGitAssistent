import httpx
import os
import subprocess
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.api.routes import router, Command
from backend.auth import token_store
from backend.config.project_manager import load_projects, save_projects
from backend.core.process_input import process_input

# -----------------------------
# .env laden
# -----------------------------
from backend.process.ProcessInput import projects

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
loaded = load_dotenv(dotenv_path)
print("load_dotenv erfolgreich?", loaded)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ACCESS_TOKEN = None

assert CLIENT_ID is not None, "CLIENT_ID ist None – überprüfe die .env-Datei!"
assert CLIENT_SECRET is not None, "CLIENT_SECRET ist None – überprüfe die .env-Datei!"

# -----------------------------
# FastAPI Setup
# -----------------------------
app = FastAPI()

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# GitHub Login Endpoint
# -----------------------------
@app.get("/auth/github/login")
def github_login():
    # Login URL mit Scope
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return RedirectResponse(url)

# -----------------------------
# GitHub Callback Endpoint
# -----------------------------
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
            },
            timeout=10.0
        )

    data = res.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail=f"GitHub Token konnte nicht abgerufen werden: {data}")

    # ✅ Speichern in deinem zentralen Modul
    token_store.ACCESS_TOKEN = token
    print("✅ GitHub OAuth Token:", token)
    return RedirectResponse("http://localhost:5173/login-success")


class Project(BaseModel):
    name: str
    path: str

@app.post("/project")
def register_project(project: Project):
    if not project.path:
        return {"error": "Pfad darf nicht leer sein"}

    projects[project.name] = {"path": project.path}

    save_projects(projects)

    return {"message": f"Projekt '{project.name}' gespeichert!"}

@app.get("/projects")
def get_projects():
    # Liefert alle registrierten Projekte zurück
    return {"projects": projects}
