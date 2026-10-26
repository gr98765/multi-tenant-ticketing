import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { demoLogin } from "../api";

export default function DemoButton({ style }) {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleClick() {
        setError("");
        setLoading(true);
        try {
            await demoLogin();
            navigate("/dashboard");
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div>
            <button
                type="button"
                onClick={handleClick}
                disabled={loading}
                style={{ background: "#7c3aed", ...style }}
            >
                {loading ? "Opening demo…" : "Try the live demo"}
            </button>
            {loading && (
                <p style={{ color: "#94a3b8", fontSize: 12, marginTop: 8 }}>
                    The free server can take up to a minute to wake up.
                </p>
            )}
            {error && <p style={{ color: "#f87171", fontSize: 13, marginTop: 8 }}>{error}</p>}
        </div>
    );
}