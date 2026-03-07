export default function TerminalOutput({ logs }) {

    return (
        <div style={terminal}>
            {logs.map((log,i)=>(
                <pre key={i}>{log}</pre>
            ))}
        </div>
    );
}

const terminal = {
    background:"#0f0f0f",
    color:"#00ff9c",
    padding:20,
    height:"400px",
    overflow:"auto",
    fontFamily:"monospace"
};