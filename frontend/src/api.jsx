const API_BASE = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

export async function apiFetch(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    const token = getToken();
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || "Request failed");
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}
export async function login(email, password) {
    const formBody = new URLSearchParams();
    formBody.append("username", email);
    formBody.append("password", password);

    const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formBody,
    });

    if (!response.ok) {
        throw new Error("Invalid email or password");
    }

    const data = await response.json();
    localStorage.setItem("token", data.access_token);
    return data;
}

export async function signup(email, password, organizationName) {
    const data = await apiFetch("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password, organization_name: organizationName }),
    });
    localStorage.setItem("token", data.access_token);
    return data;
}

export function logout() {
    localStorage.removeItem("token");
}

export function isLoggedIn() {
    return !!getToken();
}

export async function listServices() {
    return apiFetch("/services/");
}

export async function createService(name) {
    return apiFetch("/services/", {
        method: "POST",
        body: JSON.stringify({ name }),
    });
}

export async function listIncidents() {
    return apiFetch("/incidents/");
}

export async function createIncident(title, severity, serviceId) {
    return apiFetch("/incidents/", {
        method: "POST",
        body: JSON.stringify({ title, severity, service_id: serviceId }),
    });
}

export async function updateIncidentStatus(incidentId, status) {
    return apiFetch(`/incidents/${incidentId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
    });
}

export async function listIncidentUpdates(incidentId) {
    return apiFetch(`/incidents/${incidentId}/updates`);
}

export async function addIncidentUpdate(incidentId, message) {
    return apiFetch(`/incidents/${incidentId}/updates`, {
        method: "POST",
        body: JSON.stringify({ message }),
    });
}
export async function getIncident(incidentId) {
    return apiFetch(`/incidents/${incidentId}`);
}

export async function listReleases() {
    return apiFetch("/releases/");
}

export async function createRelease(serviceId, version) {
    return apiFetch("/releases/", {
        method: "POST",
        body: JSON.stringify({ service_id: serviceId, version }),
    });
}
export async function getDashboard() {
    return apiFetch("/dashboard/");
}
export async function getService(serviceId) {
    return apiFetch(`/services/${serviceId}`);
}

export async function getMe() {
    return apiFetch("/auth/me");
}

export async function deleteRelease(releaseId) {
    return apiFetch(`/releases/${releaseId}`, { method: "DELETE" });
}

export async function deleteService(serviceId) {
    return apiFetch(`/services/${serviceId}`, { method: "DELETE" });
}
export function getViewMode() {
    return localStorage.getItem("viewMode") || "owner";
}

export function setViewMode(mode) {
    localStorage.setItem("viewMode", mode);
}

export async function listMembers() {
    return apiFetch("/auth/members");
}

export async function assignIncident(incidentId, userId) {
    return apiFetch(`/incidents/${incidentId}/assign?user_id=${userId}`, {
        method: "PATCH",
    });
}

export async function getMyAssignedCount() {
    return apiFetch("/incidents/assigned-to-me");
}
export async function getMyAssignedIncidents() {
    return apiFetch("/incidents/assigned-to-me");
}