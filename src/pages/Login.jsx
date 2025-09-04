import React, { useEffect } from "react";

const CLIENT_ID = "252980470679-crb5fdt79f0g68paajs3q9oqr8d5dav7.apps.googleusercontent.com";

export default function Login({ onLogin }) {
  useEffect(() => {
    /* global google */
    if (!window.google) return;
    google.accounts.id.initialize({
      client_id: CLIENT_ID,
      callback: handleCredentialResponse
    });
    google.accounts.id.renderButton(document.getElementById("g_id_signin"), {
      theme: "outline", size: "large"
    });
  }, []);

  async function handleCredentialResponse(response) {
    // response.credential is the id_token
    const res = await fetch("/api/login", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({ id_token: response.credential }),
      credentials: "include"
    });
    if (res.ok) {
      const data = await res.json();
      onLogin(data);
    } else {
      alert("Login failed");
    }
  }

  return <div>
    <h3>Login with Google</h3>
    <div id="g_id_signin"></div>
  </div>
}