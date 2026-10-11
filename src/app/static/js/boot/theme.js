// Тема оформления. Классический скрипт в <head>: data-theme ставится до отрисовки, без мигания.
// Режим: 'auto' (как в Telegram) | 'light' | 'dark'.
// Хранится в localStorage (синхронно, для первой отрисовки) и в CloudStorage Telegram
// (общий для всех устройств пользователя; читается асинхронно и при расхождении побеждает).
// Страницы работают с темой через window.MeWeTheme (static/js/components/theme-switcher.js).
(function () {
  var STORAGE_KEY = 'theme';
  var MODES = ['auto', 'light', 'dark'];
  var tg = window.Telegram && window.Telegram.WebApp;
  var systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  var listeners = [];

  function isMode(value) {
    return MODES.indexOf(value) !== -1;
  }

  function supports(version) {
    return Boolean(tg && tg.isVersionAtLeast && tg.isVersionAtLeast(version));
  }

  function readLocal() {
    try {
      var value = window.localStorage.getItem(STORAGE_KEY);
      return isMode(value) ? value : null;
    } catch (error) {
      return null;
    }
  }

  function writeLocal(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (error) {
      // без хранилища выбор просто не запомнится на этом устройстве
    }
  }

  var mode = readLocal() || 'auto';

  function systemScheme() {
    if (tg && tg.colorScheme) return tg.colorScheme;
    return systemDark.matches ? 'dark' : 'light';
  }

  function resolvedScheme() {
    return mode === 'auto' ? systemScheme() : mode;
  }

  // Шапка и фон самого Telegram — в цвет страницы, иначе при «светлой» теме
  // в тёмном Telegram сверху останется тёмная полоса
  function syncTelegramColors() {
    if (!tg) return;
    var styles = window.getComputedStyle(document.documentElement);
    var page = styles.getPropertyValue('--bg-page').trim();
    var card = styles.getPropertyValue('--bg-card').trim();
    if (!page) return; // стили ещё не загружены — повторим по событию load

    if (supports('6.1')) {
      tg.setHeaderColor(page);
      tg.setBackgroundColor(page);
    }
    if (supports('7.10') && tg.setBottomBarColor) {
      tg.setBottomBarColor(card);
    }
  }

  function apply() {
    document.documentElement.setAttribute('data-theme', resolvedScheme());
    syncTelegramColors();
    listeners.forEach(function (listener) {
      listener(mode);
    });
  }

  function setMode(next, options) {
    if (!isMode(next)) return;
    mode = next;
    writeLocal(next);
    if (!(options && options.fromCloud) && supports('6.9')) {
      tg.CloudStorage.setItem(STORAGE_KEY, next);
    }
    apply();
  }

  window.MeWeTheme = {
    get mode() {
      return mode;
    },
    setMode: setMode,
    onChange: function (listener) {
      listeners.push(listener);
    }
  };

  apply();
  window.addEventListener('load', syncTelegramColors);

  // В режиме «Авто» следуем за сменой темы в Telegram (или в системе вне Telegram)
  if (tg) {
    tg.onEvent('themeChanged', function () {
      if (mode === 'auto') apply();
    });
  } else {
    systemDark.addEventListener('change', function () {
      if (mode === 'auto') apply();
    });
  }

  if (supports('6.9')) {
    tg.CloudStorage.getItem(STORAGE_KEY, function (error, value) {
      if (!error && isMode(value) && value !== mode) {
        setMode(value, { fromCloud: true });
      }
    });
  }
})();
