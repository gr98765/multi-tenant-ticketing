import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        try {
            await login(email, password);
            navigate("/dashboard");
        } catch (err) {
            setError(err.message);
        }
    }

    return (
        <div style={{
            maxWidth: 400,
            margin: "80px auto",
            padding: 30,
            background: "#111a3a",
            borderRadius: 10,
            boxShadow: "0 4px 20px rgba(0,0,0,0.3)"
        }}>
            <h2>Log in</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Email</label>
                    <input value={email} onChange={(e) => setEmail(e.target.value)} required />
                </div>
                <div>
                    <label>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                {error && <p style={{ color: "red" }}>{error}</p>}
                <button type="submit">Log in</button>
            </form>
            <p>
                No account? <Link to="/signup">Sign up</Link>
            </p>
        </div>
    );
}