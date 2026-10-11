import { authFetch } from './auth.js';

// Ошибка ответа API: текст из {"error": ...} и HTTP-статус (0 — сеть недоступна)
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

// Единая точка запросов к API: авторизация, JSON в обе стороны, ошибки как ApiError
export async function requestJson(url, { method = 'GET', body, headers = {} } = {}) {
  const options = { method, headers: { Accept: 'application/json', ...headers } };
  if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await authFetch(url, options);
  } catch {
    throw new ApiError('Сетевая ошибка. Проверьте подключение', 0);
  }

  if (response.status === 204) return null;

  const isJson = (response.headers.get('content-type') || '').includes('application/json');
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new ApiError(data?.error || `HTTP error: ${response.status}`, response.status);
  }

  return data;
}
