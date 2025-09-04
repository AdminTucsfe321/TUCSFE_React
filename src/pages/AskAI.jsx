import React, { useState } from "react";

export default function AskAI({ user }) {
  const [prompt, setPrompt] = useState("");
  const [resp, setResp] = useState(null);

  async function submit() {
    const r = await fetch("/api/ask", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      credentials: "include",
      body: JSON.stringify({ prompt })
    });
    if (r.ok) {
      const j = await r.json();
      setResp(j.response);
    } else {
      const err = await r.json();
      alert("Error: " + (err.detail || "unknown"));
    }
  }

  return (
    <div>
      <h3>Ask AI — {user.email}</h3>
      <textarea value={prompt} onChange={e=>setPrompt(e.target.value)} rows={6} cols={80} />
      <div><button onClick={submit}>Ask</button></div>
      {resp && <div><h4>Response</h4><pre>{resp}</pre></div>}
    </div>
  )
}