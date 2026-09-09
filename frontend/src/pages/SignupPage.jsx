import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signup } from "../api";

export default function SignupPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [orgName, setOrgName] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        try {
            await signup(email, password, orgName);
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
            <h2>Sign up</h2>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Organization name</label>
                    <input value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
                </div>
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
                <button type="submit">Sign up</button>
            </form>
            <p>
                Already have an account? <Link to="/login">Log in</Link>
            </p>
        </div>
    );
}