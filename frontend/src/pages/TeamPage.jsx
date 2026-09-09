import { useState } from "react";
import { apiFetch } from "../api";

export default function TeamPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [result, setResult] = useState("");
    const [error, setError] = useState("");

    async function handleInvite(e) {
        e.preventDefault();
        setError("");
        setResult("");
        try {
            await apiFetch("/auth/invite", {
                method: "POST",
                body: JSON.stringify({ email, password }),
            });
            setResult(`Member created. They can log in with ${email}.`);
            setEmail("");
            setPassword("");
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <div style={{ maxWidth: 500, margin: "40px auto", padding: "0 20px" }}>
            <h2>Team</h2>
            <p style={{ color: "#94a3b8", marginBottom: 20 }}>
                Invite a teammate as a member. Members can view services and manage
                incidents, but can't add or remove services.
            </p>
            <form onSubmit={handleInvite}>
                <label>Email</label>
                <input value={email} onChange={(e) => setEmail(e.target.value)} required />
                <label>Temporary password</label>
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button type="submit">Add member</button>
            </form>
            {result && <p style={{ color: "#22c55e", marginTop: 16 }}>{result}</p>}
            {error && <p style={{ color: "#f87171", marginTop: 16 }}>{error}</p>}
        </div>
    );
}