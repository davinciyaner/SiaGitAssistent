import { useState } from "react";

function App() {
  const [command, setCommand] = useState("");
  const [output, setOutput] = useState("");

  // async Funktion, die auf Button-Klick ausgeführt wird
  const sendCommand = async () => {
    try {
      const res = await fetch("http://localhost:8001/command", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ command }),
      });

      const data = await res.json();
      setOutput(data.output); // Ausgabe im State speichern
    } catch (err) {
      console.error(err);
      setOutput("Fehler beim Ausführen des Befehls");
    }
  };

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
    </div>
  );
}

export default App;