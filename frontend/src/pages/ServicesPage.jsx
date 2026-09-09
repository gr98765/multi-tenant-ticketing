import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listServices, createService, deleteService, getViewMode } from "../api";

export default function ServicesPage() {
    const [services, setServices] = useState([]);
    const [name, setName] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    async function loadServices() {
        try {
            const data = await listServices();
            setServices(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadServices();
    }, []);

    async function handleCreate(e) {
        e.preventDefault();
        setError("");
        try {
            await createService(name);
            setName("");
            loadServices();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleDelete(e, serviceId) {
        e.preventDefault();
        e.stopPropagation();
        try {
            await deleteService(serviceId);
            loadServices();
        } catch (err) {
            setError(err.message);
        }
    }

    function timeElapsed(createdAt, resolvedAt) {
        const start = new Date(createdAt);
        const end = resolvedAt ? new Date(resolvedAt) : new Date();
        const minutes = Math.round((end - start) / 60000);
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.round(minutes / 60);
        if (hours < 24) return `${hours}h`;
        const days = Math.round(hours / 24);
        return `${days}d`;
    }
    const isOwnerView = getViewMode() === "owner";

    return (
        <div style={{ maxWidth: 600, margin: "40px auto", padding: "0 20px" }}>
            <h2>Services</h2>

            {isOwnerView && (
                <form onSubmit={handleCreate} style={{ marginBottom: 30 }}>
                    <label>New service name</label>
                    <input
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="e.g. payments-api"
                        required
                    />
                    <button type="submit">Add service</button>
                </form>
            )}

            {error && <p style={{ color: "#f87171" }}>{error}</p>}

            {loading ? (
                <p>Loading...</p>
            ) : services.length === 0 ? (
                <p>No services yet. Add one above.</p>
            ) : (
                <ul style={{ listStyle: "none", padding: 0 }}>
                    {services.map((s) => (
                        <li key={s.id} style={{ marginBottom: 8, display: "flex", alignItems: "center", gap: 8 }}>
                            <Link
                                to={`/services/${s.id}`}
                                style={{
                                    flex: 1,
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    background: "#111a3a",
                                    padding: "12px 16px",
                                    borderRadius: 8,
                                    color: "#f1f5f9",
                                    textDecoration: "none",
                                }}
                            >
                                <span>{s.name}</span>
                                <span style={{ color: "#94a3b8", fontSize: 18 }}>›</span>
                            </Link>
                            {isOwnerView && (
                                <button onClick={(e) => handleDelete(e, s.id)} style={{ background: "#7f1d1d", fontSize: 12, padding: "6px 10px" }}>
                                    Delete
                                </button>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}