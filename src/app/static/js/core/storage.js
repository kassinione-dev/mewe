// Хранилище может быть недоступно (приватный режим, запрет cookie) — тогда работаем без него

function safeStorage(getStorage) {
  return {
    get(key) {
      try {
        return getStorage().getItem(key);
      } catch {
        return null;
      }
    },
    set(key, value) {
      try {
        getStorage().setItem(key, value);
      } catch {
        // не критично: значение просто не запомнится
      }
    }
  };
}

export const local = safeStorage(() => window.localStorage);
export const session = safeStorage(() => window.sessionStorage);
