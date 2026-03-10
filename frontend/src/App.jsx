import { useState } from "react";

function App() {

    const [command, setCommand] = useState("");
    const [output, setOutput] = useState("");
    const [loading, setLoading] = useState(false);

    const sendCommand = async () => {

        if (!command) return;

        setLoading(true);

        try {

            const res = await fetch("http://localhost:8001/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ command }),
            });

            const data = await res.json();
            setOutput(data.output);

        } catch (err) {

            console.error(err);
            setOutput("❌ Fehler beim Ausführen");

        }

        setLoading(false);
        setCommand("");
    };

    const login = () => {
        window.location.href = "http://localhost:8001/auth/github/login";
    };

    return (

        <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-10">

            <h1 className="text-4xl font-bold mb-2">
                AISIA
            </h1>

            <p className="text-gray-600 mb-8">
                Your AI DevOps Assistant
            </p>


            <button
                onClick={login}
                className="bg-black text-white px-4 py-2 rounded mb-8"
            >
                Login with GitHub
            </button>


            {/* COMMAND BOX */}

            <div className="w-full max-w-2xl bg-white p-6 rounded-xl shadow">

                <input
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    placeholder="Type a command... (e.g. push backend)"
                    className="border p-3 w-full rounded mb-4"
                />

                <button
                    onClick={sendCommand}
                    className="bg-blue-600 text-white w-full py-3 rounded"
                >
                    {loading ? "Running..." : "Execute"}
                </button>

            </div>


            {/* SUGGESTIONS */}

            <div className="mt-6 text-sm text-gray-600">

                <p>Examples:</p>

                <ul className="list-disc ml-5 mt-2">

                    <li>register project backend /Users/dev/backend</li>
                    <li>create branch backend feature-login</li>
                    <li>push backend</li>
                    <li>run pipeline username repo</li>

                </ul>

            </div>


            {/* TERMINAL */}

            <div className="w-full max-w-2xl mt-8 bg-black text-green-400 p-6 rounded-xl font-mono">

                {output || "Terminal Output..."}

            </div>

        </div>

    );
}

export default App;