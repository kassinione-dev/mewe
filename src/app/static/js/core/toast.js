import { h, icon } from './dom.js';

// Уведомление над нижним меню. Закрывается само или тапом; новое заменяет текущее.
// type: 'success' | 'error' | 'info'

const DURATION_MS = { success: 2500, info: 2500, error: 4000 };
const ICONS = { success: 'check_circle', error: 'error', info: 'info' };

let hideTimeout;

function hide() {
  clearTimeout(hideTimeout);
  document.getElementById('toast')?.classList.remove('show');
}

// Отклик телефона через Telegram — как у нативных приложений (Bot API 6.1+)
function vibrate(type) {
  const tg = window.Telegram?.WebApp;
  if (!tg?.isVersionAtLeast?.('6.1') || type === 'info') return;
  tg.HapticFeedback.notificationOccurred(type);
}

export function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.className = `toast toast-${type}`;
  toast.replaceChildren(
    icon(ICONS[type] || ICONS.info, 'toast-icon'),
    h('span', { className: 'toast-text', text: message })
  );
  // перезапуск анимации появления, если предыдущее уведомление ещё на экране
  void toast.offsetWidth;
  toast.classList.add('show');
  vibrate(type);

  clearTimeout(hideTimeout);
  hideTimeout = setTimeout(hide, DURATION_MS[type] || DURATION_MS.info);
}

document.getElementById('toast')?.addEventListener('click', hide);
