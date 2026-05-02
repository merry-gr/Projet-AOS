async function login(credentials) {
    // users-service exposes JWT at /api/login/ (TokenObtainPairView) and /api/token/
    const response = await fetch(`${CONFIG.API_USERS_URL}/api/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials)
    });
    const data = await response.json();
    
    if (data.access) {
        localStorage.setItem('access_token', data.access);
    }
    if (data.refresh) {
        localStorage.setItem('refresh_token', data.refresh);
    }

    if (data.access) {
        // Simple redirect (the API doesn't return role/status fields)
        window.location.href = 'dashboard.html';
        return;
    }

    throw new Error(data?.detail || 'Login failed');
}