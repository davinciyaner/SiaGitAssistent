from fastapi import FastAPI
from pydantic import BaseModel

from backend.process.ProcessInput import process_input

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Command(BaseModel):
    command: str


@app.post("/command")
def run_command(cmd: Command):
    result = process_input(cmd.command, auto_confirm=True)
    return {"output": result}
