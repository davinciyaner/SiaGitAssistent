
from fastapi import APIRouter
from pydantic import BaseModel

from backend.config.project_manager import load_projects
from backend.core.process_input import process_input
from backend.git.init import handle_init


router = APIRouter()

@router.post("/init")
def init_repo(path: str):
    result = handle_init(path)

    return {"output": result}


class Command(BaseModel):
    command: str

@router.post("/command")
def run_command(cmd: Command):
    parts = cmd.command.strip().split()
    if len(parts) < 2:
        return {"output": "Bitte Projektname angeben, z.B. 'push backend'"}

    action = parts[0].lower()
    project_name = parts[1]

    projects = load_projects()

    if project_name not in projects:
        return {"output": f"Projekt '{project_name}' nicht registriert"}

    path = projects[project_name]["path"]

    result = process_input(action, path)

    return {"output": result}