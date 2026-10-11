// Переключатель темы: группа радиокнопок [data-theme-mode] внутри root.
// Сама тема живёт в boot/theme.js (window.MeWeTheme) — здесь только интерфейс к ней.
export function initThemeSwitcher(root) {
  const theme = window.MeWeTheme;
  if (!root || !theme) return;

  const options = [...root.querySelectorAll('[data-theme-mode]')];

  function render(mode) {
    options.forEach(option => {
      const checked = option.dataset.themeMode === mode;
      option.setAttribute('aria-checked', String(checked));
      option.tabIndex = checked ? 0 : -1;
    });
  }

  options.forEach((option, index) => {
    option.addEventListener('click', () => theme.setMode(option.dataset.themeMode));

    // Стрелки переключают вариант, как в обычной группе радиокнопок
    option.addEventListener('keydown', event => {
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      event.preventDefault();
      const step = event.key === 'ArrowRight' ? 1 : -1;
      const next = options[(index + step + options.length) % options.length];
      theme.setMode(next.dataset.themeMode);
      next.focus();
    });
  });

  theme.onChange(render);
  render(theme.mode);
}
