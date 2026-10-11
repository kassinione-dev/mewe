// Создание элементов без россыпи createElement/append:
//   h('div', { className: 'card', dataset: { id: 1 } }, h('h3', { text: 'Заголовок' }))
// Свойства: className, text, dataset, style, on<Event> — обработчик; остальное — атрибуты.
// null, undefined и false среди детей и значений свойств пропускаются.
export function h(tag, props = {}, ...children) {
  const element = document.createElement(tag);

  for (const [key, value] of Object.entries(props)) {
    if (value === null || value === undefined || value === false) continue;

    if (key === 'className') element.className = value;
    else if (key === 'text') element.textContent = value;
    else if (key === 'dataset') Object.assign(element.dataset, value);
    else if (key === 'style') Object.assign(element.style, value);
    else if (/^on[A-Z]/.test(key)) element.addEventListener(key.slice(2).toLowerCase(), value);
    else element.setAttribute(key, value === true ? '' : value);
  }

  element.append(...children.flat().filter(child => child !== null && child !== undefined && child !== false));
  return element;
}

// Иконка Font Awesome: icon('fa-clock', 'icon') → <i class="fas fa-clock icon">
export function icon(name, className = '') {
  return h('i', { className: `fas ${name}${className ? ` ${className}` : ''}`, 'aria-hidden': 'true' });
}
