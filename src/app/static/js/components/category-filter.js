import { h, icon } from '../core/dom.js';
import { createModal } from './modal.js';

// Фильтр по категориям на странице поиска: кнопка «Категории» со счётчиком,
// окно выбора и чипы выбранных категорий под поиском.
// onChange вызывается при каждом изменении выбора.
export function createCategoryFilter({ tab, count, chips, modalRoot, onChange }) {
  const selected = new Map();
  const options = [...modalRoot.querySelectorAll('[data-category-id]')];
  const resetButton = modalRoot.querySelector('[data-categories-reset]');

  const modal = createModal(modalRoot, {
    initialFocus: () => options[0],
    onOpen: () => tab.setAttribute('aria-expanded', 'true'),
    onClose: () => tab.setAttribute('aria-expanded', 'false')
  });

  function render() {
    const size = selected.size;

    tab.classList.toggle('active', size > 0);
    tab.setAttribute('aria-label', size ? `Выбор категории, выбрано: ${size}` : 'Выбор категории');
    count.textContent = String(size);
    count.hidden = size === 0;
    resetButton.disabled = size === 0;

    chips.hidden = size === 0;
    chips.replaceChildren(...[...selected].map(([id, name]) => h('button', {
      className: 'selected-category-chip',
      type: 'button',
      'aria-label': `Убрать категорию: ${name}`,
      onClick: () => {
        selected.delete(id);
        changed();
      }
    }, icon('sell'), h('span', { text: name }), icon('close'))));

    options.forEach(option => {
      option.setAttribute('aria-pressed', String(selected.has(option.dataset.categoryId)));
    });
  }

  function changed() {
    render();
    onChange();
  }

  function toggle(option) {
    const id = option.dataset.categoryId;
    if (selected.has(id)) selected.delete(id);
    else selected.set(id, option.dataset.categoryName);
    changed();
  }

  options.forEach(option => option.addEventListener('click', () => toggle(option)));

  tab.addEventListener('click', modal.open);

  resetButton.addEventListener('click', () => {
    selected.clear();
    changed();
  });

  render();

  return {
    get ids() {
      return [...selected.keys()];
    },
    // Сброс без onChange: вызывающий сам перезагрузит список
    clear() {
      selected.clear();
      render();
    }
  };
}
