import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState, useRef } from "react";
import { isLoggedIn, logout, getMe, getViewMode, setViewMode, getMyAssignedIncidents } from "../api";

export default function Header() {
    const navigate = useNavigate();
    const location = useLocation();
    const [orgName, setOrgName] = useState("");
    const [realRole, setRealRole] = useState(null);
    const [viewMode, setViewModeState] = useState(getViewMode());
    const [menuOpen, setMenuOpen] = useState(false);
    const [assignedIncidents, setAssignedIncidents] = useState([]);
    const [assignedMenuOpen, setAssignedMenuOpen] = useState(false);
    const menuRef = useRef(null);
    const assignedRef = useRef(null);

    useEffect(() => {
        if (isLoggedIn()) {
            getMe()
                .then((data) => {
                    setOrgName(data.organization_name);
                    setRealRole(data.role);
                })
                .catch(() => {
                    setOrgName("");
                    setRealRole(null);
                });
            getMyAssignedIncidents()
                .then(setAssignedIncidents)
                .catch(() => setAssignedIncidents([]));
        } else {
            setOrgName("");
            setRealRole(null);
            setAssignedIncidents([]);
        }
    }, [location.pathname]);

    useEffect(() => {
        function handleClickOutside(e) {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setMenuOpen(false);
            }
            if (assignedRef.current && !assignedRef.current.contains(e.target)) {
                setAssignedMenuOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    function handleLogout() {
        logout();
        navigate("/login");
    }

    function selectViewMode(mode) {
        setViewMode(mode);
        setViewModeState(mode);
        setMenuOpen(false);
        window.location.reload();
    }

    const showAssignedBadge =
        (realRole === "OWNER" && viewMode === "member" && assignedIncidents.length > 0) ||
        (realRole === "MEMBER" && assignedIncidents.length > 0);

    return (
        <header style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "16px 32px",
            background: "#111a3a",
            borderBottom: "1px solid #1e293b",
            position: "relative",
        }}>
            <Link to={isLoggedIn() ? "/dashboard" : "/"} style={{
                color: "#f1f5f9",
                fontSize: "18px",
                fontWeight: 700,
                textDecoration: "none",
            }}>
                Relay.io
            </Link>

            {isLoggedIn() && (
                <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                    {orgName && <span style={{ color: "#94a3b8", fontSize: 14 }}>{orgName}</span>}

                    {showAssignedBadge && (
                        <div ref={assignedRef} style={{ position: "relative" }}>
                            <button
                                onClick={() => setAssignedMenuOpen(!assignedMenuOpen)}
                                style={{
                                    background: "#7c3aed", color: "white", fontSize: 12,
                                    padding: "6px 12px", borderRadius: 999, fontWeight: 600,
                                    border: "none", cursor: "pointer",
                                }}
                            >
                                Assigned to you: {assignedIncidents.length}
                            </button>
                            {assignedMenuOpen && (
                                <div style={{
                                    position: "absolute", top: "calc(100% + 8px)", right: 0,
                                    background: "#151a33", border: "1px solid #232945", borderRadius: 8,
                                    minWidth: 240, boxShadow: "0 8px 24px rgba(0,0,0,0.3)", zIndex: 10, overflow: "hidden",
                                }}>
                                    {assignedIncidents.map((inc) => (
                                        <Link
                                            key={inc.id}
                                            to={`/incidents/${inc.id}`}
                                            onClick={() => setAssignedMenuOpen(false)}
                                            style={{
                                                display: "block", padding: "10px 14px", color: "#e2e5f1",
                                                fontSize: 13, textDecoration: "none", borderBottom: "1px solid #232945",
                                            }}
                                        >
                                            {inc.title}
                                        </Link>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {realRole === "OWNER" && (
                        <div ref={menuRef} style={{ position: "relative" }}>
                            <button
                                onClick={() => setMenuOpen(!menuOpen)}
                                style={{
                                    background: "#1e293b",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 8,
                                    fontSize: 13,
                                }}
                            >
                                <span style={{
                                    width: 24, height: 24, borderRadius: "50%",
                                    background: "#6366f1", display: "inline-flex",
                                    alignItems: "center", justifyContent: "center",
                                    fontSize: 12, fontWeight: 700,
                                }}>
                                    {viewMode === "owner" ? "O" : "M"}
                                </span>
                                {viewMode === "owner" ? "Admin" : "Member"}
                            </button>

                            {menuOpen && (
                                <div style={{
                                    position: "absolute",
                                    top: "calc(100% + 8px)",
                                    right: 0,
                                    background: "#151a33",
                                    border: "1px solid #232945",
                                    borderRadius: 8,
                                    minWidth: 180,
                                    boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
                                    zIndex: 10,
                                    overflow: "hidden",
                                }}>
                                    <button
                                        onClick={() => selectViewMode("owner")}
                                        style={{
                                            display: "block", width: "100%", textAlign: "left",
                                            padding: "10px 14px", background: viewMode === "owner" ? "#1e293b" : "transparent",
                                            border: "none", color: "#e2e5f1", fontSize: 13,
                                        }}
                                    >
                                        View as Admin
                                    </button>
                                    <button
                                        onClick={() => selectViewMode("member")}
                                        style={{
                                            display: "block", width: "100%", textAlign: "left",
                                            padding: "10px 14px", background: viewMode === "member" ? "#1e293b" : "transparent",
                                            border: "none", color: "#e2e5f1", fontSize: 13,
                                        }}
                                    >
                                        View as Member
                                    </button>
                                </div>
                            )}
                        </div>
                    )}

                    {realRole === "MEMBER" && (
                        <span style={{
                            background: "#1e293b", color: "#94a3b8", fontSize: 13,
                            padding: "8px 14px", borderRadius: 8,
                        }}>
                            Member
                        </span>
                    )}

                    <button onClick={handleLogout} style={{ background: "#1e293b" }}>
                        Log out
                    </button>
                </div>
            )}
        </header>
    );
}