import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
    getIncident, listIncidentUpdates, addIncidentUpdate, updateIncidentStatus,
    listMembers, assignIncident, getViewMode,
} from "../api";

const STATUSES = ["OPEN", "INVESTIGATING", "RESOLVED"];

export default function IncidentDetailPage() {
    const { id } = useParams();
    const [incident, setIncident] = useState(null);
    const [updates, setUpdates] = useState([]);
    const [members, setMembers] = useState([]);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [assignMessage, setAssignMessage] = useState("");

    const isOwnerView = getViewMode() === "owner";

    async function loadData() {
        try {
            const [incidentData, updatesData, membersData] = await Promise.all([
                getIncident(id),
                listIncidentUpdates(id),
                listMembers(),
            ]);
            setIncident(incidentData);
            setUpdates(updatesData);
            setMembers(membersData);
        } catch (err) {
            setError(err.message);
        }
    }

    useEffect(() => {
        loadData();
    }, [id]);

    async function handleAddUpdate(e) {
        e.preventDefault();
        try {
            await addIncidentUpdate(id, message);
            setMessage("");
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleStatusChange(newStatus) {
        try {
            await updateIncidentStatus(id, newStatus);
            loadData();
        } catch (err) {
            setError(err.message);
        }
    }

    async function handleAssign(userId) {
        try {
            await assignIncident(id, userId);
            setAssignMessage("Assigned successfully.");
            loadData();
            setTimeout(() => setAssignMessage(""), 2000);
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

    if (!incident) return <div style={{ padding: 40 }}>Loading...</div>;

    const assignedMember = members.find((m) => m.id === incident.assigned_to_id);

    return (
        <div style={{ maxWidth: 700, margin: "40px auto", padding: "0 20px" }}>
            <Link
                to={`/services/${incident.service_id}`}
                style={{ display: "inline-block", marginBottom: 20, color: "#94a3b8", fontSize: 14 }}
            >
                ← Back to Incident
            </Link>

            <h2>{incident.title}</h2>
            <p style={{ color: "#94a3b8" }}>
                Severity: {incident.severity} · Status: {incident.status} ·{" "}
                {incident.status === "RESOLVED"
                    ? `resolved in ${timeElapsed(incident.created_at, incident.resolved_at)}`
                    : `open for ${timeElapsed(incident.created_at)}`}
            </p>

            {isOwnerView ? (
                <div style={{ marginBottom: 20 }}>
                    <label>Assign to</label>
                    <select
                        value={incident.assigned_to_id || ""}
                        onChange={(e) => handleAssign(e.target.value)}
                        style={{ width: "100%", padding: 8 }}
                    >
                        <option value="">Unassigned</option>
                        {members.map((m) => (
                            <option key={m.id} value={m.id}>{m.email}</option>
                        ))}
                    </select>
                    {assignMessage && (
                        <p style={{ color: "#22c55e", fontSize: 13, marginTop: 6 }}>{assignMessage}</p>
                    )}
                </div>
            ) : (
                <p style={{ color: "#94a3b8", marginBottom: 20 }}>
                    Assigned to: {assignedMember ? assignedMember.email : "Unassigned"}
                </p>
            )}

            {incident.status !== "RESOLVED" && (
                <div style={{ marginBottom: 20 }}>
                    <label>Change status</label>
                    <select
                        value={incident.status}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        style={{ width: "100%", padding: 8 }}
                    >
                        {STATUSES.map((s) => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                </div>
            )}

            {error && <p style={{ color: "#f87171" }}>{error}</p>}

            <h3>Timeline</h3>

            {incident.status !== "RESOLVED" ? (
                <form onSubmit={handleAddUpdate} style={{ marginBottom: 20 }}>
                    <input
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Add an update..."
                        required
                    />
                    <button type="submit">Post update</button>
                </form>
            ) : (
                <p style={{ color: "#94a3b8", marginBottom: 20 }}>
                    This incident is resolved and closed for further updates.
                </p>
            )}

            <ul style={{ listStyle: "none", padding: 0 }}>
                {updates.map((u) => (
                    <li key={u.id} style={{
                        background: "#111a3a",
                        padding: "10px 14px",
                        borderRadius: 8,
                        marginBottom: 8,
                        textAlign: "left",
                    }}>
                        {u.message}
                    </li>
                ))}
            </ul>
        </div>
    );
}