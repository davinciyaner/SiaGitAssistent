import { useState } from "react";

export default function GitHubAuthModal({ visible, onSubmit }) {

    const [token, setToken] = useState("");

    if (!visible) return null;

    return (
        <div style={overlay}>
            <div style={modal}>
                <h2>GitHub Authorization</h2>

                <p>Enter your GitHub Personal Access Token</p>

                <input
                    type="password"
                    placeholder="ghp_..."
                    value={token}
                    onChange={(e)=>setToken(e.target.value)}
                    style={input}
                />

                <button onClick={()=>onSubmit(token)} style={button}>
                    Authorize
                </button>
            </div>
        </div>
    );
}

const overlay = {
    position:"fixed",
    top:0,
    left:0,
    right:0,
    bottom:0,
    background:"rgba(0,0,0,0.6)",
    display:"flex",
    alignItems:"center",
    justifyContent:"center"
};

const modal = {
    background:"#1e1e1e",
    padding:30,
    borderRadius:10,
    color:"white",
    width:400
};

const input = {
    width:"100%",
    padding:10,
    marginTop:10
};

const button = {
    marginTop:20,
    padding:10,
    width:"100%"
};