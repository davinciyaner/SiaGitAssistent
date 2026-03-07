




export async function sendCommand(command, token=null) {
    const res = await fetch("http://localhost:8000/command", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            command: command,
            github_token: token
        })
    })
    return await res.json()
}