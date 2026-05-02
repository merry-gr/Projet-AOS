// Central API configuration for the static front-end.
// Update ports here if you change docker-compose mappings.
window.CONFIG = {
  API_USERS_URL: 'http://localhost:8000',
  API_PRODUCTS_URL: 'http://localhost:8001',
  API_ORDERS_URL: 'http://localhost:8002',
};

window.getAccessToken = function getAccessToken() {
  return localStorage.getItem('access_token') || localStorage.getItem('token') || '';
};

window.authHeader = function authHeader() {
  const token = window.getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

window.currentUserId = function currentUserId() {
  const token = window.getAccessToken();
  if (!token) return '';

  try {
    const payload = token.split('.')[1];
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized + '='.repeat((4 - normalized.length % 4) % 4);
    const data = JSON.parse(atob(padded));
    return data.user_id || '';
  } catch (error) {
    return '';
  }
};
