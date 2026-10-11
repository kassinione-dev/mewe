import { h, icon } from '../core/dom.js';

// Пустой список: иконка, заголовок, пояснение и необязательное действие
// action: { label, href } — ссылка или { label, onClick } — кнопка
export function createEmptyState({ icon: iconName, title, text, action }) {
  return h('div', { className: 'no-events empty-state' },
    h('div', { className: 'empty-state-icon' }, icon(iconName)),
    h('div', { className: 'empty-state-title', text: title }),
    h('div', { className: 'empty-state-text', text }),
    action && createAction(action)
  );
}

function createAction({ label, href, onClick }) {
  return href
    ? h('a', { className: 'btn empty-state-btn', href, text: label })
    : h('button', { className: 'btn empty-state-btn', type: 'button', text: label, onClick });
}

// Ошибка загрузки списка с кнопкой «Повторить» (если передан onRetry)
export function createErrorState(message, onRetry) {
  if (!onRetry) return h('p', { className: 'error', text: message });

  return h('div', { className: 'error' },
    h('p', { text: message }),
    h('button', { className: 'btn empty-state-btn', type: 'button', text: 'Повторить', onClick: onRetry })
  );
}
