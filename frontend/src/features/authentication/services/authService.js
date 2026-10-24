
import { apiGet, apiPost } from '../../../services/apiClient.js';
import { API_ENDPOINTS } from '../../../services/endpointConfig.js';

export const getCurrentUser = () => apiGet(API_ENDPOINTS.me);
export const loginRequest = (credentials) => apiPost(API_ENDPOINTS.login, credentials);
export const registerRequest = (details) => apiPost(API_ENDPOINTS.register, details);
export const logoutRequest = () => apiPost(API_ENDPOINTS.logout, {});
