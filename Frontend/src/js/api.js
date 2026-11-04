
console.log("API.js loaded successfully");

const API_HOST = window.location.hostname || "127.0.0.1";
const API_BASE_URL = `${window.location.protocol === "https:" ? "https" : "http"}://${API_HOST}:8000`;

async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem("access_token");

    const headers = {
        ...options.headers,
    };

    if (options.body && !(options.body instanceof FormData)) {
        headers["Content-Type"] = "application/json";
    }

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail;
        const message = Array.isArray(detail)
            ? detail.map((item) => item.msg).filter(Boolean).join("; ")
            : (typeof detail === "string" ? detail : `Request failed (${response.status})`);
        const error = new Error(message);
        error.status = response.status;
        throw error;
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}
