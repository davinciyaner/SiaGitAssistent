import {useState} from "react";

function App() {
    const [command, setCommand] = useState("");
    const [output, setOutput] = useState("");

    const [projectName, setProjectName] = useState("");
    const [projectPath, setProjectPath] = useState("");

    const [branchProject, setBranchProject] = useState("");
    const [branchName, setBranchName] = useState("");
    const [pushBranch, setPushBranch] = useState(false);

    const sendCommand = async (cmd) => {
        if (!cmd) return;

        try {
            const res = await fetch("http://localhost:8001/command", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({command: cmd}),
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
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({name: projectName, path: projectPath}),
            });

            const data = await res.json();
            setOutput(data.message);
        } catch (err) {
            console.error(err);
            setOutput("Projekt konnte nicht gespeichert werden");
        }
    };

    const createBranch = () => {
        if (!branchProject || !branchName) {
            setOutput("Projektname und Branchname müssen angegeben werden");
            return;
        }

        let branchCommand = `branch ${branchProject} ${branchName}`;
        if (pushBranch) branchCommand += " --push";

        sendCommand(branchCommand);
    };

    const login = () => {
        window.location.href = "http://localhost:8001/auth/github/login";
    };

    return (
        <div className="p-10">
            <h1 className="text-3xl font-bold mb-6">AISIA Git Assistant</h1>

            <button
                onClick={login}
                className="bg-black text-white px-4 py-2 rounded mb-6"
            >
                Login with GitHub
            </button>

            <h2 className="text-xl font-bold mt-6 mb-2">Projekt registrieren</h2>
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
                className="border p-2 w-full mb-2"
            />
            <button
                onClick={registerProject}
                className="bg-green-600 text-white px-4 py-2 mt-1 rounded"
            >
                Projekt speichern
            </button>

            <h2 className="text-xl font-bold mt-10 mb-2">Branch erstellen</h2>
            <input
                value={branchProject}
                onChange={(e) => setBranchProject(e.target.value)}
                placeholder="Projektname"
                className="border p-2 w-full mb-2"
            />
            <input
                value={branchName}
                onChange={(e) => setBranchName(e.target.value)}
                placeholder="Branchname"
                className="border p-2 w-full mb-2"
            />
            <label className="flex items-center mb-2">
                <input
                    type="checkbox"
                    checked={pushBranch}
                    onChange={(e) => setPushBranch(e.target.checked)}
                    className="mr-2"
                />
                Branch direkt zu GitHub pushen
            </label>
            <button
                onClick={createBranch}
                className="bg-blue-500 text-white px-4 py-2 mt-1 rounded"
            >
                Branch erstellen
            </button>

            <h2 className="text-xl font-bold mt-10 mb-2">Git Command</h2>
            <input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                className="border p-2 w-full"
                placeholder="z.B. push backend"
            />
            <button
                onClick={() => sendCommand(command)}
                className="bg-blue-500 text-white px-4 py-2 mt-1 rounded"
            >
                Ausführen
            </button>

            <pre className="mt-6 bg-black text-green-400 p-4 whitespace-pre-wrap">
                {output}
            </pre>
        </div>
    );
}

export default App;