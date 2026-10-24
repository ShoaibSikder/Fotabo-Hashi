
import { API_ENDPOINTS } from './endpointConfig.js';

export async function getCsrfToken() {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch(API_ENDPOINTS.csrf, {
      credentials: 'include',
      signal: controller.signal,
    });
    const body = await response.json();
    if (!response.ok) throw new Error('Could not start a secure session. Please try again.');
    return body?.data?.csrfToken || '';
  } finally {
    window.clearTimeout(timeout);
  }
}

export function readCsrfCookie() {
  const entry = document.cookie.split('; ').find((part) => part.startsWith('csrftoken='));
  return entry ? decodeURIComponent(entry.split('=').slice(1).join('=')) : '';
}
