const TOAST_DURATION_MS = 2000;
let hideTimeout;

// Короткое уведомление сверху экрана; type: 'success' | 'error' | 'info'
export function showToast(message, type = '') {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.className = type ? `toast show ${type}` : 'toast show';

  clearTimeout(hideTimeout);
  hideTimeout = setTimeout(() => toast.classList.remove('show'), TOAST_DURATION_MS);
}
