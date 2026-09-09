import { Link } from "react-router-dom";

const FEATURES = [
    {
        title: "Services",
        desc: "Track every application your team runs in one place.",
    },
    {
        title: "Releases",
        desc: "Log deployments and connect them to incidents when things break.",
    },
    {
        title: "Incidents",
        desc: "Open, assign, and resolve incidents with a live timeline.",
    },
    {
        title: "Status Pages",
        desc: "Share real-time status with your customers, publicly.",
    },
];

export default function LandingPage() {
    return (
        <div style={{ position: "relative", overflow: "hidden" }}>
            <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(24px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .fade-in-1 { animation: fadeInUp 0.6s ease-out both; }
        .fade-in-2 { animation: fadeInUp 0.6s ease-out 0.15s both; }
        .fade-in-3 { animation: fadeInUp 0.6s ease-out 0.3s both; }
        .fade-in-4 { animation: fadeInUp 0.6s ease-out 0.45s both; }
        .fade-in-5 { animation: fadeInUp 0.6s ease-out 0.6s both; }
        .fade-in-6 { animation: fadeInUp 0.6s ease-out 0.75s both; }
      `}</style>

            <div style={{
                position: "absolute", top: "-200px", left: "50%", transform: "translateX(-50%)",
                width: "800px", height: "500px",
                background: "radial-gradient(circle, rgba(99,102,241,0.35) 0%, rgba(99,102,241,0) 70%)",
                filter: "blur(40px)", pointerEvents: "none",
            }} />

            <div style={{ position: "relative", textAlign: "center", padding: "100px 20px 60px" }}>
                <h1 className="fade-in-1" style={{ fontSize: 40, marginBottom: 16 }}>
                    Track incidents. Manage releases.<br />Ship with confidence.
                </h1>
                <p className="fade-in-2" style={{ color: "#94a3b8", fontSize: 16, marginBottom: 30 }}>
                    Relay.io helps engineering teams stay on top of their services
                    from deployment to resolution.
                </p>
                <div className="fade-in-3" style={{ display: "flex", gap: 12, justifyContent: "center" }}>
                    <Link to="/signup"><button>Sign up free</button></Link>
                    <Link to="/login">
                        <button style={{ background: "#1e293b" }}>Log in</button>
                    </Link>
                </div>
            </div>

            <div className="fade-in-4" style={{ maxWidth: 900, margin: "0 auto", padding: "0 20px 80px" }}>
                <h2 style={{ textAlign: "center", fontSize: 24, marginBottom: 8 }}>
                    Everything your team needs
                </h2>
                <p style={{ textAlign: "center", color: "#94a3b8", marginBottom: 40 }}>
                    One tool to track services, releases, and incidents end to end.
                </p>
                <div style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
                    gap: 20,
                }}>
                    {FEATURES.map((f) => (
                        <div key={f.title} style={{
                            background: "#111a3a", border: "1px solid #1e293b", borderRadius: 10,
                            padding: 24, textAlign: "left",
                        }}>
                            <div style={{ fontSize: 24, marginBottom: 12 }}>{f.icon}</div>
                            <h3 style={{ color: "#f1f5f9", fontSize: 16, marginBottom: 6 }}>{f.title}</h3>
                            <p style={{ color: "#94a3b8", fontSize: 14 }}>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ maxWidth: 1000, margin: "0 auto 100px", padding: "0 20px" }}>
                <div style={{
                    background: "#111a3a", border: "1px solid #232945", borderRadius: 14,
                    padding: 32, boxShadow: "0 24px 70px rgba(0,0,0,0.45)", textAlign: "left",
                }}>
                    <div className="fade-in-4" style={{ display: "flex", gap: 6, marginBottom: 20 }}>
                        <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#ef4444" }} />
                        <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#eab308" }} />
                        <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#22c55e" }} />
                    </div>

                    <h3 className="fade-in-4" style={{ fontSize: 20, marginBottom: 16, color: "#f1f5f9" }}>Dashboard</h3>

                    <div className="fade-in-4" style={{ display: "flex", gap: 16, marginBottom: 24 }}>
                        <div style={{ flex: 1, background: "#151a33", borderRadius: 10, padding: 18 }}>
                            <div style={{ fontSize: 26, fontWeight: 700 }}>3</div>
                            <div style={{ fontSize: 13, color: "#94a3b8" }}>Open incidents</div>
                        </div>
                        <div style={{ flex: 1, background: "#151a33", borderRadius: 10, padding: 18 }}>
                            <div style={{ fontSize: 26, fontWeight: 700 }}>12</div>
                            <div style={{ fontSize: 13, color: "#94a3b8" }}>Resolved (30d)</div>
                        </div>
                    </div>

                    <div className="fade-in-5">
                        <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                            Open incidents by severity
                        </div>
                        <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
                            <SevPreview label="SEV1" value={1} color="#ef4444" />
                            <SevPreview label="SEV2" value={1} color="#f97316" />
                            <SevPreview label="SEV3" value={1} color="#eab308" />
                            <SevPreview label="SEV4" value={0} color="#64748b" />
                        </div>
                    </div>

                    <div className="fade-in-6">
                        <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 10, textTransform: "uppercase", letterSpacing: "0.04em" }}>
                            Recent incidents
                        </div>
                        {[
                            { title: "Checkout failing for some users", service: "payments-api", severity: "SEV1", status: "OPEN", time: "open for 3m" },
                            { title: "Search results returning stale data", service: "search-api", severity: "SEV3", status: "OPEN", time: "open for 5h" },
                            { title: "Password reset emails delayed", service: "auth-service", severity: "SEV2", status: "RESOLVED", time: "resolved in 45m" },
                        ].map((item) => (
                            <div key={item.title} style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "flex-start",
                                background: "#151a33",
                                padding: "12px 16px",
                                borderRadius: 8,
                                marginBottom: 8,
                            }}>
                                <div>
                                    <div style={{ fontWeight: 600, color: "#60a5fa", fontSize: 14 }}>{item.title}</div>
                                    <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>
                                        {item.service} · {item.severity}
                                    </div>
                                </div>
                                <div style={{ fontSize: 13, color: "#94a3b8", textAlign: "right", whiteSpace: "nowrap", marginLeft: 12 }}>
                                    {item.status}
                                    <div style={{ fontSize: 12, marginTop: 4 }}>{item.time}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function SevPreview({ label, value, color }) {
    return (
        <div style={{
            flex: 1, background: "#151a33", borderRadius: 8, padding: "10px 12px",
            borderLeft: `3px solid ${color}`,
        }}>
            <div style={{ fontSize: 18, fontWeight: 700 }}>{value}</div>
            <div style={{ fontSize: 11, color: "#94a3b8" }}>{label}</div>
        </div>
    );
}