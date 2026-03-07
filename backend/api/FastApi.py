from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
import httpx
import os

from backend.process.ProcessInput import process_input

from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

ACCESS_TOKEN = None

app = FastAPI()

@app.get("/auth/github/login")
def github_login():

    url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"

    return RedirectResponse(url)


@app.get("/auth/github/callback")
async def github_callback(code: str):

    global ACCESS_TOKEN

    async with httpx.AsyncClient() as client:

        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code
            }
        )

    ACCESS_TOKEN = token_res.json()["access_token"]
    print(ACCESS_TOKEN)

    return RedirectResponse("http://localhost:5173/login-success")

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


