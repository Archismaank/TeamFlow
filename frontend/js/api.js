const API_BASE = '/api';

export function getToken() {
    return localStorage.getItem('teamflow_token');
}

export function setToken(token) {
    localStorage.setItem('teamflow_token', token);
}

export function clearToken() {
    localStorage.removeItem('teamflow_token');
}

export async function apiFetch(endpoint, options = {}) {
    const token = getToken();
    const isFormData = options.body instanceof URLSearchParams || options.body instanceof FormData;

    const headers = {
        ...(!isFormData ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearToken();
        window.dispatchEvent(new Event('auth:logout'));
        throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(errorData.detail || 'Something went wrong');
    }

    return response.status === 204 ? null : response.json();
}