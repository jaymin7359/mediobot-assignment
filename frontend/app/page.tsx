"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Loader } from "./loader";

const API = "http://localhost:8000";

const DEMO_ACCOUNTS = [
  { username: "dr.mehta", password: "doctor", role: "doctor" },
  { username: "nurse.priya", password: "nurse", role: "nurse" },
  { username: "billing.ravi", password: "billing_executive", role: "billing_executive" },
  { username: "tech.anand", password: "technician", role: "technician" },
  { username: "admin.sys", password: "admin", role: "admin" },
];

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("dr.mehta");
  const [password, setPassword] = useState("doctor");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const maxAttempts = 4;
      for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
          const res = await fetch(`${API}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
          });
          if (!res.ok) {
            setError("Login failed. Check username and password.");
            return;
          }
          const data = await res.json();
          localStorage.setItem("medibot_token", data.token);
          localStorage.setItem("medibot_role", data.role);
          localStorage.setItem("medibot_username", data.username);
          router.push("/chat");
          return;
        } catch {
          if (attempt < maxAttempts) {
            await new Promise((r) => setTimeout(r, 2000));
            continue;
          }
          setError(
            "Could not reach the server. Start the backend with: uvicorn backend.main:app --reload --port 8000"
          );
        }
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 480, margin: "80px auto", padding: 24 }}>
      <h1>MediBot Login</h1>
      <p>MediAssist Health Network — internal knowledge assistant</p>

      <form onSubmit={handleLogin} style={{ display: "grid", gap: 12, marginTop: 24 }}>
        <label>
          Username
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            style={{ width: "100%", padding: 8, marginTop: 4 }}
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            style={{ width: "100%", padding: 8, marginTop: 4 }}
          />
        </label>
        {error && <p style={{ color: "crimson" }}>{error}</p>}
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? (
            <>
              <Loader size="sm" inline />
              Signing in...
            </>
          ) : (
            "Sign in"
          )}
        </button>
      </form>

      <h3 style={{ marginTop: 32 }}>Demo accounts</h3>
      <ul>
        {DEMO_ACCOUNTS.map((a) => (
          <li key={a.username}>
            <button
              type="button"
              disabled={loading}
              onClick={() => { setUsername(a.username); setPassword(a.password); }}
              style={{ background: "none", border: 0, color: "#1e88e5", padding: 0 }}
            >
              {a.username}
            </button>
            {" / "}{a.password} ({a.role})
          </li>
        ))}
      </ul>
    </main>
  );
}
