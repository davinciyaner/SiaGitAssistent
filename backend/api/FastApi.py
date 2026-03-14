import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.agent.repo_analyzer import ai_analyze_repo
from backend.api.routes import router
from backend.auth import token_store
from backend.config.project_manager import save_projects
from backend.process.ProcessInput import projects
from backend.services.git_service import GitHubService

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
loaded = load_dotenv(dotenv_path)

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ACCESS_TOKEN = None


app = FastAPI()

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/auth/github/login")
def github_login():
    # Login URL mit Scope
    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return RedirectResponse(url)


@app.get("/auth/github/callback")
async def github_callback(code: str):
    global ACCESS_TOKEN
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
            timeout=10.0,
        )

    data = res.json()
    token = data.get("access_token")
    if not token:
        raise HTTPException(
            status_code=400,
            detail=f"GitHub Token konnte nicht abgerufen werden: {data}",
        )

    token_store.ACCESS_TOKEN = token
    print("GitHub OAuth Token:", token)
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
    return {"projects": projects}


@app.get("/ai-analyze")
def ai_analyze(repo_url: str):
    return ai_analyze_repo(repo_url)


def get_github_service():
    token = token_store.ACCESS_TOKEN
    if not token:
        raise HTTPException(status_code=401, detail="GitHub Token fehlt")
    return GitHubService(token)


@router.get("/ci/runs")
def workflow_runs(repo_full_name: str, workflow_name: str = None, limit: int = 5):
    github = get_github_service()
    return github.latest_workflow_runs(repo_full_name, workflow_name, limit)


@router.get("/ci/logs")
def workflow_logs(repo_full_name: str, run_id: int):
    github = get_github_service()
    return github.get_run_logs(repo_full_name, run_id)
