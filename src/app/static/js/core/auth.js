import { showToast } from './toast.js';

// Вход через initData Telegram. Модуль подключается на каждой странице (base.html),
// поэтому вход начинается сразу при загрузке, а authFetch ждёт его завершения.

const tg = window.Telegram?.WebApp;

async function authUser() {
  try {
    const response = await fetch('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        initData: tg?.initData || '',
        platform: tg?.platform || '',
        version: tg?.version || ''
      })
    });

    if (response.ok) return true;

    const result = await response.json().catch(() => null);
    const message = result?.error || `HTTP error: ${response.status}`;
    console.error('Auth failed:', message);
    showToast(`Ошибка: ${message}`, 'error');
    return false;
  } catch (error) {
    console.error(error);
    showToast('Сетевая ошибка при попытке аутентификации.', 'error');
    return false;
  }
}

let authPromise = authUser();

// Ждёт входа перед запросом; если сессия потерялась (401) — входит заново и повторяет запрос один раз
export async function authFetch(url, options = {}) {
  const awaitedAuth = authPromise;
  await awaitedAuth;

  const response = await fetch(url, options);
  if (response.status !== 401) return response;

  // Параллельные запросы делят одну повторную авторизацию
  if (authPromise === awaitedAuth) {
    authPromise = authUser();
  }
  if (!(await authPromise)) return response;

  return fetch(url, options);
}
