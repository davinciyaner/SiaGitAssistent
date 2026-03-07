import { useState } from "react";

export default function CommandInput({ onCommand }) {

    const [command,setCommand] = useState("");

    function submit(e){
        e.preventDefault();
        onCommand(command);
        setCommand("");
    }

    return (
        <form onSubmit={submit} style={{display:"flex",gap:10}}>
            <input
                value={command}
                onChange={(e)=>setCommand(e.target.value)}
                placeholder="init C:\project https://github.com/user/repo.git"
                style={{flex:1,padding:10}}
            />
            <button type="submit">Run</button>
        </form>
    );
}