import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
    getService, listReleases, createRelease, deleteRelease,
    listIncidents, createIncident, getViewMode,
} from "../api";

const SEVERITIES = ["SEV1", "SEV2", "SEV3", "SEV4"];

export default function ServiceDetailPage() {
    const { id } = useParams();
    const serviceId = Number(id);

    const [service, setService] = useState(null);
    const [releases, setReleases] = useState([]);
    const [incidents, setIncidents] = useState([]);
    const [tab, setTab] = useState("incidents");

    const [version, setVersion] = useState("");
    const [incidentTitle, setIncidentTitle] = useState("");
    const [severity, setSeverity] = useState("SEV3");
    const [error, setError] = useState("");

    const isOwnerView = getViewMode() === "owner";

    async function loadData() {
        try {
            const [serviceData, releasesData, incidentsData] = await Promise.all([
                getService(serviceId),
                listReleases(),
                listIncidents(),
            ]);
            setService(serviceData);
            setReleases(releasesData.filter((r) => r.service_id === serviceId));
            setIncidents(incidentsData.filter((i) => i.service_id === serviceId));
        } catch (err) {
            setError(err.message);
        }
    }

    useEffect(() => {
        loadData();
    }, [serviceId]);

    async function handleAddRelease(e) {
        e.preventDefault();
        try {
            await createRelease(serviceId, version);
            setVersion("");
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleDeleteRelease(releaseId) {
        try {
            await deleteRelease(releaseId);
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleAddIncident(e) {
        e.preventDefault();
        try {
            await createIncident(incidentTitle, severity, serviceId);
            setIncidentTitle("");
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    function timeElapsed(createdAt, resolvedAt) {
        const start = new Date(createdAt);
        const end = resolvedAt ? new Date(resolvedAt) : new Date();
        const minutes = Math.max(0, Math.round((end - start) / 60000));
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.round(minutes / 60);
        if (hours < 24) return `${hours}h`;
        const days = Math.round(hours / 24);
        return `${days}d`;
    }

    if (!service) return <div style={{ padding: 40 }}>Loading...</div>;

    const openCount = incidents.filter((i) => i.status !== "RESOLVED").length;

    return (
        <div style={{ maxWidth: 800, margin: "40px auto", padding: "0 20px" }}>
            <Link to="/services" style={{ display: "inline-block", marginBottom: 20, color: "#94a3b8", fontSize: 14 }}>
                ← Back to services
            </Link>

            <h2>{service.name}</h2>
            {error && <p style={{ color: "#f87171" }}>{error}</p>}

            <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: "1px solid #1e293b" }}>
                <TabButton active={tab === "incidents"} onClick={() => setTab("incidents")}>
                    Incidents {openCount > 0 && `(${openCount})`}
                </TabButton>
                <TabButton active={tab === "releases"} onClick={() => setTab("releases")}>
                    Releases
                </TabButton>
            </div>

            {tab === "incidents" && (
                <div style={{ textAlign: "left" }}>
                    <form onSubmit={handleAddIncident} style={{ marginBottom: 20 }}>
                        <label>Title</label>
                        <input
                            value={incidentTitle}
                            onChange={(e) => setIncidentTitle(e.target.value)}
                            placeholder="e.g. Checkout failing for some users"
                            required
                        />
                        <label>Severity</label>
                        <select
                            value={severity}
                            onChange={(e) => setSeverity(e.target.value)}
                            style={{ width: "100%", padding: 8, marginBottom: 14 }}
                        >
                            {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
                        </select>
                        <button type="submit">Open incident</button>
                    </form>

                    {incidents.length === 0 ? (
                        <p style={{ color: "#94a3b8" }}>No incidents yet.</p>
                    ) : (
                        <ul style={{ listStyle: "none", padding: 0 }}>
                            {incidents.map((i) => (
                                <li key={i.id} style={{
                                    background: "#111a3a", padding: "12px 16px",
                                    borderRadius: 8, marginBottom: 8,
                                    display: "flex", justifyContent: "space-between", alignItems: "center",
                                }}>
                                    <Link to={`/incidents/${i.id}`} style={{ fontWeight: 600 }}>
                                        {i.title}
                                    </Link>
                                    <div style={{ fontSize: 13, color: "#94a3b8", textAlign: "right" }}>
                                        {i.severity} · {i.status}
                                        <br />
                                        {i.status === "RESOLVED"
                                            ? `resolved in ${timeElapsed(i.created_at, i.resolved_at)}`
                                            : `open for ${timeElapsed(i.created_at)}`}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}

            {tab === "releases" && (
                <div style={{ textAlign: "left" }}>
                    <form onSubmit={handleAddRelease} style={{ marginBottom: 20 }}>
                        <label>Version</label>
                        <input
                            value={version}
                            onChange={(e) => setVersion(e.target.value)}
                            placeholder="e.g. v1.2.3"
                            required
                        />
                        <button type="submit">Log release</button>
                    </form>

                    {releases.length === 0 ? (
                        <p style={{ color: "#94a3b8" }}>No releases yet.</p>
                    ) : (
                        <ul style={{ listStyle: "none", padding: 0 }}>
                            {releases.map((r) => (
                                <li key={r.id} style={{
                                    background: "#111a3a", padding: "12px 16px",
                                    borderRadius: 8, marginBottom: 8,
                                    display: "flex", justifyContent: "space-between", alignItems: "center",
                                }}>
                                    <div>
                                        {r.version}
                                        <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>
                                            {new Date(r.deployed_at).toLocaleString()}
                                        </div>
                                    </div>
                                    {isOwnerView && (
                                        <button
                                            onClick={() => handleDeleteRelease(r.id)}
                                            style={{ background: "#7f1d1d", fontSize: 12, padding: "6px 10px" }}
                                        >
                                            Delete
                                        </button>
                                    )}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
}

function TabButton({ active, onClick, children }) {
    return (
        <button
            onClick={onClick}
            style={{
                background: "none",
                color: active ? "#f1f5f9" : "#94a3b8",
                border: "none",
                borderBottom: active ? "2px solid #3b82f6" : "2px solid transparent",
                borderRadius: 0,
                padding: "10px 16px",
                fontWeight: active ? 600 : 400,
                cursor: "pointer",
            }}
        >
            {children}
        </button>
    );
}