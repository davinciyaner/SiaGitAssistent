import {useState} from "react";

function App() {

    const [command, setCommand] = useState("");
    const [output, setOutput] = useState("");

    const [projectName, setProjectName] = useState("");
    const [projectPath, setProjectPath] = useState("");

    const sendCommand = async () => {

        try {

            const res = await fetch("http://localhost:8001/command", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({command}),
            });

            const data = await res.json();
            setOutput(data.output);

        } catch (err) {

            console.error(err);
            setOutput("Fehler beim Ausführen des Befehls");

        }
    };

    const registerProject = async () => {
        if (!projectName || !projectPath) {
            setOutput("Name und Pfad müssen ausgefüllt sein");
            return;
        }

        try {
            const res = await fetch("http://localhost:8001/project", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name: projectName,
                    path: projectPath
                }),
            });

            const data = await res.json();
            setOutput(data.message);

        } catch (err) {
            console.error(err);
            setOutput("Projekt konnte nicht gespeichert werden");
        }
    };

    function login() {

        window.location.href = "http://localhost:8001/auth/github/login"

    }

    return (

        <div className="p-10">

            <h1 className="text-3xl font-bold mb-6">
                AISIA Git Assistant
            </h1>

            <button
                onClick={login}
                className="bg-black text-white px-4 py-2 rounded mb-6"
            >
                Login with GitHub
            </button>

            {/* PROJECT REGISTER */}

            <h2 className="text-xl font-bold mt-6 mb-2">
                Projekt registrieren
            </h2>

            <input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Projektname (z.B backend)"
                className="border p-2 w-full mb-2"
            />

            <input
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
                placeholder="/Users/max/dev/backend"
                className="border p-2 w-full"
            />

            <button
                onClick={registerProject}
                className="bg-green-600 text-white px-4 py-2 mt-3 rounded"
            >
                Projekt speichern
            </button>

            {/* COMMAND */}

            <h2 className="text-xl font-bold mt-10 mb-2">
                Git Command
            </h2>

            <input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                className="border p-2 w-full"
                placeholder="push backend"
            />

            <button
                onClick={sendCommand}
                className="bg-blue-500 text-white px-4 py-2 mt-3 rounded"
            >
                Ausführen
            </button>

            <pre className="mt-6 bg-black text-green-400 p-4">
                {output}
            </pre>

        </div>

    );
}

export default App;