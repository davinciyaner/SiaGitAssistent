import {useState} from "react";
import CommandInput from "./components/CommandInput";
import TerminalOutput from "./components/TerminalOutput";
import GitHubAuthModal from "./components/GitHubAuthModel";

function App() {
    const [command, setCommand] = useState("");
    const [output, setOutput] = useState("");

    const [logs, setLogs] = useState([]);
    const [showAuth, setShowAuth] = useState(false);
    const [pendingCommand, setPendingCommand] = useState(null);

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

    async function runCommand(command, token = null) {

        const res = await sendCommand(command, token);

        if (res.requires_auth) {
            setPendingCommand(command);
            setShowAuth(true);
            return;
        }

        setLogs(l => [...l, res.output]);
    }

    async function handleCommand(command) {
        runCommand(command);
    }

    async function handleAuth(token) {

        setShowAuth(false);

        const res = await sendCommand(pendingCommand, token);

        setLogs(l => [...l, res.output]);
    }

    return (
        <div className="p-10">
            <h1 className="text-3xl font-bold mb-4">AISIA Git Assistant</h1>

            <input
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                className="border p-2 w-full"
                placeholder="push mein backend"
            />

            <button
                onClick={sendCommand}
                className="bg-blue-500 text-white px-4 py-2 mt-3 rounded"
            >
                Ausführen
            </button>

            <pre className="mt-6 bg-black text-green-400 p-4">{output}</pre>

            <CommandInput onCommand={handleCommand}/>

            <TerminalOutput logs={logs}/>

            <GitHubAuthModal
                visible={showAuth}
                onSubmit={handleAuth}
            />
        </div>
    );
}

export default App;