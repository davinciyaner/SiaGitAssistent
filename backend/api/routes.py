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
    print("COMMAND RECEIVED:", cmd.command)

    projects = load_projects()

    result = process_input(cmd.command)
    print(result)

    return {"output": result}
