import httpx
import os
import subprocess
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.api.routes import router
from backend.config.project_manager import load_projects, save_projects
from backend.core.process_input import process_input
from backend.git.init_full import handle_init_full

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
ACCESS_TOKEN = None

app = FastAPI()

projects = load_projects()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


class Command(BaseModel):
    command: str

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


class Project(BaseModel):
    name: str
    path: str

@app.post("/project")
def register_project(project: Project):
    projects[project.name] = {"path": project.path}
    save_projects(projects)
    return {"message": f"Projekt '{project.name}' gespeichert!"}

@app.get("/projects")
def get_projects():
    # Liefert alle registrierten Projekte zurück
    return {"projects": projects}

@router.post("/command")
def run_command(cmd: Command):
    text = cmd.command.strip()
    path = cmd.path

    result = process_input(cmd.command, projects, text, path)
    return {"output": result}