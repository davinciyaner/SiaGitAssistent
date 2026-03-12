import httpx
from starlette.responses import RedirectResponse

from backend.git.github_login import CLIENT_SECRET, CLIENT_ID


@app.get("/auth/github/callback")
async def github_callback(code: str):
    global ACCESS_TOKEN
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
        )
    ACCESS_TOKEN = res.json()["access_token"]
    print("GitHub OAuth Token:", ACCESS_TOKEN)
    return RedirectResponse("http://localhost:5173/login-success")
