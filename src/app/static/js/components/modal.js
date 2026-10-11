// Модальное окно поверх страницы. Разметка:
//   <div class="modal" aria-hidden="true" role="dialog">
//     <div class="modal-overlay" data-modal-close></div>
//     <div class="modal-content">… <button data-modal-close>…</div>
//   </div>
// Закрывается по [data-modal-close], клику мимо окна и Escape (только верхнее из открытых).

const openModals = [];

document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && openModals.length) {
    openModals[openModals.length - 1].close();
  }
});

export function createModal(root, { onOpen, onClose, initialFocus } = {}) {
  let returnFocus = null;

  const modal = {
    root,

    get isOpen() {
      return root.classList.contains('is-open');
    },

    open() {
      if (modal.isOpen) return;
      // Фокус возвращаем только при работе с клавиатуры: после тапа подсвеченная карточка лишняя
      const active = document.activeElement;
      returnFocus = active?.matches?.(':focus-visible') ? active : null;
      root.classList.add('is-open');
      root.setAttribute('aria-hidden', 'false');
      openModals.push(modal);
      onOpen?.();
      initialFocus?.()?.focus();
    },

    close() {
      if (!modal.isOpen) return;
      root.classList.remove('is-open');
      root.setAttribute('aria-hidden', 'true');
      openModals.splice(openModals.indexOf(modal), 1);
      onClose?.();
      returnFocus?.focus?.();
    }
  };

  root.addEventListener('click', event => {
    if (event.target === root || event.target.closest('[data-modal-close]')) modal.close();
  });

  return modal;
}
