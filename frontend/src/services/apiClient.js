import { API_ENDPOINTS } from './endpointConfig.js';
import { getCsrfToken, readCsrfCookie } from './csrfService.js';

const REQUEST_TIMEOUT_MS = 30_000;
const MAX_SESSION_CACHE_ENTRIES = 250;
let csrfTokenRequest = null;
let cachedCsrfToken = '';
let refreshRequest = null;
let sessionCacheGeneration = 0;
const sessionGetCache = new Map();
const pendingGetRequests = new Map();

const NEVER_CACHE_GET = [
  API_ENDPOINTS.me,
  API_ENDPOINTS.health,
  API_ENDPOINTS.notifications,
];

export function clearApiCache() {
  sessionCacheGeneration += 1;
  sessionGetCache.clear();
  pendingGetRequests.clear();
}

function canCacheGet(url) {
  return !NEVER_CACHE_GET.some((endpoint) => url === endpoint || url.startsWith(`${endpoint}?`));
}

function rememberGet(url, value) {
  sessionGetCache.delete(url);
  sessionGetCache.set(url, value);
  if (sessionGetCache.size > MAX_SESSION_CACHE_ENTRIES) {
    const oldestKey = sessionGetCache.keys().next().value;
    sessionGetCache.delete(oldestKey);
  }
}

function getCsrfTokenOnce() {
  const cookieToken = readCsrfCookie();
  if (cookieToken) {
    cachedCsrfToken = cookieToken;
    return Promise.resolve(cookieToken);
  }
  if (cachedCsrfToken) return Promise.resolve(cachedCsrfToken);
  if (!csrfTokenRequest) {
    csrfTokenRequest = getCsrfToken()
      .then((token) => {
        cachedCsrfToken = token;
        return token;
      })
      .finally(() => {
        csrfTokenRequest = null;
      });
  }
  return csrfTokenRequest;
}

export function warmCsrfToken() {
  void getCsrfTokenOnce().catch(() => {});
}

function refreshSessionOnce(timeoutMs) {
  if (!refreshRequest) {
    refreshRequest = apiRequest(API_ENDPOINTS.refresh, {
      method: 'POST',
      retry: false,
      timeoutMs,
    }).finally(() => {
      refreshRequest = null;
    });
  }
  return refreshRequest;
}

const STATUS_MESSAGES = {
  400: 'Please review the information and try again.',
  401: 'Your session has expired. Please sign in again.',
  403: 'You do not have permission to do that.',
  404: 'The requested information could not be found.',
  408: 'The request took too long. Please try again.',
  409: 'This change conflicts with the latest data. Refresh and try again.',
  429: 'Too many attempts. Please wait a moment and try again.',
  500: 'A server error occurred. Please try again shortly.',
  502: 'The service is temporarily unavailable. Please try again shortly.',
  503: 'The service is temporarily unavailable. Please try again shortly.',
  504: 'The service took too long to respond. Please try again.',
};

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'NETWORK_ERROR', details = {}, requestId = '' } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
    this.requestId = requestId;
  }
}

function firstMessage(value) {
  if (typeof value === 'string' && value.trim()) return value.trim();
  if (Array.isArray(value)) {
    for (const item of value) {
      const message = firstMessage(item);
      if (message) return message;
    }
  } else if (value && typeof value === 'object') {
    for (const item of Object.values(value)) {
      const message = firstMessage(item);
      if (message) return message;
    }
  }
  return '';
}

function apiErrorFromResponse(body, response) {
  const error = body?.error || {};
  const details = error.details ?? body?.details ?? {};
  const status = response.status;
  const baseMessage = status >= 500
    ? STATUS_MESSAGES[status] || 'A server error occurred. Please try again shortly.'
    : firstMessage(details) || error.message || body?.detail || STATUS_MESSAGES[status] || 'The request could not be completed.';
  const requestId = error.request_id || response.headers.get('X-Request-ID') || '';
  const message = status >= 500 && requestId
    ? `${baseMessage} Reference ID: ${requestId}`
    : baseMessage;

  return new ApiError(message, {
    status,
    code: error.code || `HTTP_${status}`,
    details,
    requestId,
  });
}

export function apiRequest(url, options = {}) {
  const method = (options.method || 'GET').toUpperCase();
  const shouldCache = method === 'GET' && canCacheGet(url);
  if (shouldCache && sessionGetCache.has(url)) {
    const cached = sessionGetCache.get(url);
    // Refresh insertion order so frequently revisited pages stay in the cache.
    rememberGet(url, cached);
    return Promise.resolve(cached);
  }
  const cacheGeneration = sessionCacheGeneration;
  const pendingKey = `${cacheGeneration}:${url}`;
  if (shouldCache && pendingGetRequests.has(pendingKey)) return pendingGetRequests.get(pendingKey);

  const request = performApiRequest(url, options);
  if (!shouldCache) return request;

  const sharedRequest = request
    .then((value) => {
      if (cacheGeneration === sessionCacheGeneration) rememberGet(url, value);
      return value;
    })
    .finally(() => {
      if (pendingGetRequests.get(pendingKey) === sharedRequest) {
        pendingGetRequests.delete(pendingKey);
      }
    });
  pendingGetRequests.set(pendingKey, sharedRequest);
  return sharedRequest;
}

async function performApiRequest(url, {
  method = 'GET',
  body,
  headers = {},
  retry = true,
  signal,
  timeoutMs = REQUEST_TIMEOUT_MS,
} = {}) {
  const requestHeaders = new Headers(headers);
  requestHeaders.set('Accept', 'application/json');
  let payload = body;
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  if (body !== undefined && body !== null && !isFormData) {
    requestHeaders.set('Content-Type', 'application/json');
    payload = JSON.stringify(body);
  }

  const normalizedMethod = method.toUpperCase();

  if (!['GET', 'HEAD', 'OPTIONS'].includes(normalizedMethod)) {
    let csrf;
    try {
      csrf = readCsrfCookie() || await getCsrfTokenOnce();
    } catch {
      throw new ApiError('Could not establish a secure connection. Please refresh and try again.', {
        code: 'CSRF_SETUP_FAILED',
      });
    }
    if (csrf) requestHeaders.set('X-CSRFToken', csrf);
  }

  const controller = new AbortController();
  const abortRequest = () => controller.abort();
  if (signal?.aborted) abortRequest();
  else signal?.addEventListener('abort', abortRequest, { once: true });
  const timeout = setTimeout(abortRequest, timeoutMs);

  let response;
  try {
    response = await fetch(url, {
      method: normalizedMethod,
      body: payload,
      headers: requestHeaders,
      credentials: 'include',
      signal: controller.signal,
    });
  } catch {
    if (signal?.aborted) {
      throw new ApiError('The request was cancelled.', { code: 'REQUEST_CANCELLED' });
    }
    if (controller.signal.aborted) {
      throw new ApiError(STATUS_MESSAGES[408], { code: 'REQUEST_TIMEOUT', status: 408 });
    }
    throw new ApiError('We could not reach the server. Check your connection and try again.');
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener('abort', abortRequest);
  }

  if (response.status === 401 && retry && url !== API_ENDPOINTS.login && url !== API_ENDPOINTS.refresh) {
    try {
      await refreshSessionOnce(timeoutMs);
      return apiRequest(url, { method, body, headers, retry: false, signal, timeoutMs });
    } catch {
      // Keep the original 401 response; callers can clear the session or show it inline.
    }
  }

  const bodyData = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) throw apiErrorFromResponse(bodyData, response);
  const result = bodyData?.data ?? bodyData;
  if (
    !['GET', 'HEAD', 'OPTIONS'].includes(normalizedMethod)
    && url !== API_ENDPOINTS.refresh
    && url !== API_ENDPOINTS.csrf
  ) clearApiCache();
  return result;
}

export function apiGet(url, options) { return apiRequest(url, options); }
export function apiPost(url, body, options = {}) { return apiRequest(url, { ...options, method: 'POST', body }); }
export function apiPatch(url, body, options = {}) { return apiRequest(url, { ...options, method: 'PATCH', body }); }
export function apiPut(url, body, options = {}) { return apiRequest(url, { ...options, method: 'PUT', body }); }
export function apiDelete(url, options = {}) { return apiRequest(url, { ...options, method: 'DELETE' }); }
