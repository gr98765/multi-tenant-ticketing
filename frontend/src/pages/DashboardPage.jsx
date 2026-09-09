import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDashboard, listServices } from "../api";

export default function DashboardPage() {
    const [data, setData] = useState(null);
    const [hasServices, setHasServices] = useState(null);
    const [error, setError] = useState("");

    useEffect(() => {
        Promise.all([getDashboard(), listServices()])
            .then(([dashboardData, services]) => {
                setData(dashboardData);
                setHasServices(services.length > 0);
            })
            .catch((err) => setError(err.message));
    }, []);

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

    if (error) return <p style={{ color: "#f87171", padding: 40 }}>{error}</p>;
    if (!data || hasServices === null) return <p style={{ padding: 40 }}>Loading...</p>;

    if (!hasServices) {
        return (
            <div style={{ maxWidth: 600, margin: "80px auto", textAlign: "center", padding: "0 20px" }}>
                <h2>Welcome to Relay 👋</h2>
                <p style={{ color: "#94a3b8", marginBottom: 24 }}>
                    You haven't added any services yet. Add your first service to start
                    tracking releases and incidents.
                </p>
                <Link to="/services"><button>Add your first service</button></Link>
            </div>
        );
    }

    return (
        <div style={{ maxWidth: 900, margin: "40px auto", padding: "0 20px" }}>
            <h2>Dashboard</h2>

            <div style={{ display: "flex", gap: 16, marginBottom: 30 }}>
                <StatCard label="Open incidents" value={data.open_incidents} />
                <StatCard label="Resolved (last 30 days)" value={data.resolved_last_30_days} />
            </div>

            <h3>Open incidents by severity</h3>
            <div style={{ display: "flex", gap: 16, marginBottom: 30 }}>
                <SeverityCard label="SEV1" value={data.severity_breakdown.SEV1} color="#ef4444" />
                <SeverityCard label="SEV2" value={data.severity_breakdown.SEV2} color="#f97316" />
                <SeverityCard label="SEV3" value={data.severity_breakdown.SEV3} color="#eab308" />
                <SeverityCard label="SEV4" value={data.severity_breakdown.SEV4} color="#64748b" />
            </div>

            <h3>Needs attention (oldest open incidents)</h3>
            {data.needs_attention.length === 0 ? (
                <p style={{ color: "#94a3b8" }}>No open incidents 🎉</p>
            ) : (
                <ul style={{ listStyle: "none", padding: 0, marginBottom: 30 }}>
                    {data.needs_attention.map((i) => (
                        <li key={i.id} style={{
                            background: "#111a3a",
                            padding: "12px 16px",
                            borderRadius: 8,
                            marginBottom: 8,
                            textAlign: "left",
                        }}>
                            <Link to={`/incidents/${i.id}`} style={{ fontWeight: 600 }}>
                                {i.title}
                            </Link>
                            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
                                {i.service_name} · {i.severity} · open for {timeElapsed(i.created_at)}
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            <h3>Recent releases</h3>
            {data.recent_releases.length === 0 ? (
                <p style={{ color: "#94a3b8" }}>No releases logged yet.</p>
            ) : (
                <ul style={{ listStyle: "none", padding: 0, marginBottom: 30 }}>
                    {data.recent_releases.map((r, idx) => (
                        <li key={idx} style={{
                            background: "#111a3a",
                            padding: "10px 16px",
                            borderRadius: 8,
                            marginBottom: 8,
                            textAlign: "left",
                        }}>
                            <strong>{r.service_name}</strong> — {r.version}
                            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 4 }}>
                                {new Date(r.deployed_at).toLocaleString()}
                            </div>
                        </li>
                    ))}
                </ul>
            )}

            <h3>Incidents by service (last 30 days)</h3>
            {data.service_stats.length === 0 ? (
                <p>No data yet.</p>
            ) : (
                <table style={{ width: "100%", borderCollapse: "collapse", textAlign: "left" }}>
                    <thead>
                        <tr style={{ borderBottom: "1px solid #334155" }}>
                            <th style={{ padding: "8px 4px" }}>Service</th>
                            <th style={{ padding: "8px 4px" }}>Incidents</th>
                            <th style={{ padding: "8px 4px" }}>Avg resolution time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.service_stats.map((s) => (
                            <tr key={s.service_name} style={{ borderBottom: "1px solid #1e293b" }}>
                                <td style={{ padding: "8px 4px" }}>{s.service_name}</td>
                                <td style={{ padding: "8px 4px" }}>{s.incident_count}</td>
                                <td style={{ padding: "8px 4px" }}>
                                    {s.avg_resolution_seconds ? formatDuration(s.avg_resolution_seconds) : "—"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
}

function StatCard({ label, value }) {
    return (
        <div style={{ background: "#111a3a", padding: "20px", borderRadius: 10, flex: 1, textAlign: "left" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
            <div style={{ fontSize: 13, color: "#94a3b8" }}>{label}</div>
        </div>
    );
}

function SeverityCard({ label, value, color }) {
    return (
        <div style={{
            background: "#111a3a",
            padding: "14px",
            borderRadius: 10,
            flex: 1,
            textAlign: "left",
            borderLeft: `4px solid ${color}`,
        }}>
            <div style={{ fontSize: 22, fontWeight: 700 }}>{value}</div>
            <div style={{ fontSize: 12, color: "#94a3b8" }}>{label}</div>
        </div>
    );
}

function formatDuration(seconds) {
    const minutes = Math.round(seconds / 60);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.round(minutes / 60);
    return `${hours}h`;
}