import { Link, useLocation } from "react-router-dom";
import { getViewMode } from "../api";

export default function Sidebar() {
    const location = useLocation();
    const isOwnerView = getViewMode() === "owner";

    const links = [
        { to: "/dashboard", label: "Dashboard" },
        { to: "/services", label: "Services" },
        ...(isOwnerView ? [{ to: "/team", label: "Team" }] : []),
    ];

    return (
        <nav style={{
            width: 200,
            background: "#0d1330",
            minHeight: "calc(100vh - 65px)",
            padding: "24px 0",
            borderRight: "1px solid #1e293b",
        }}>
            {links.map((link) => {
                const active = location.pathname.startsWith(link.to);
                return (
                    <Link
                        key={link.to}
                        to={link.to}
                        style={{
                            display: "block",
                            padding: "10px 24px",
                            color: active ? "#f1f5f9" : "#94a3b8",
                            background: active ? "#1e293b" : "transparent",
                            textDecoration: "none",
                            fontSize: 14,
                            fontWeight: active ? 600 : 400,
                        }}
                    >
                        {link.label}
                    </Link>
                );
            })}
        </nav>
    );
}