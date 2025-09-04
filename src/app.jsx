import React, { useEffect, useState } from "react";
import Login from "./pages/Login";
import AskAI from "./pages/AskAI";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(()=> {
    // optional: check /api/session or rely on cookie + backend endpoint
  },[]);

  return (
    <div style={{padding:20}}>
      {!user ? <Login onLogin={setUser}/> : <AskAI user={user} onLogout={()=>setUser(null)}/>}
    </div>
  )
}