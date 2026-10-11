import { updateAbout } from '../api/users.js';
import { formatLocalDate } from '../core/format.js';
import { showToast } from '../core/toast.js';
import { initThemeSwitcher } from '../components/theme-switcher.js';

// Профиль: запасной аватар, если фото Telegram не загрузилось, и редактирование «О себе»

const EMPTY_ABOUT_TEXT = 'Расскажите о себе';

function initAvatarFallback() {
  const image = document.querySelector('.profile-avatar-image');
  if (!image) return;

  const hide = () => {
    image.hidden = true;
  };
  image.addEventListener('error', hide);
  if (image.complete && image.naturalWidth === 0) hide();
}

function initAboutEditor() {
  const form = document.getElementById('about-form');
  // Чужой профиль — формы нет
  if (!form) return;

  const text = document.getElementById('aboutText');
  const editButton = document.getElementById('aboutEdit');
  const cancelButton = document.getElementById('aboutCancel');
  const counter = document.getElementById('aboutCounter');
  const textarea = form.elements.about;
  const submitButton = form.querySelector('[type="submit"]');

  function updateCounter() {
    counter.textContent = `${textarea.value.length} / ${textarea.maxLength}`;
  }

  function setEditing(editing) {
    form.hidden = !editing;
    text.hidden = editing;
    editButton.hidden = editing;
    if (editing) textarea.focus();
  }

  function renderAbout(about) {
    text.textContent = about || EMPTY_ABOUT_TEXT;
    text.classList.toggle('is-empty', !about);
    textarea.value = about || '';
    updateCounter();
  }

  textarea.addEventListener('input', updateCounter);
  editButton.addEventListener('click', () => setEditing(true));

  cancelButton.addEventListener('click', () => {
    textarea.value = text.classList.contains('is-empty') ? '' : text.textContent;
    updateCounter();
    setEditing(false);
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    submitButton.disabled = true;

    try {
      const data = await updateAbout(textarea.value.trim());
      renderAbout(data.about);
      setEditing(false);
      showToast('Профиль обновлён', 'success');
    } catch (error) {
      showToast(`Ошибка: ${error.message}`, 'error');
    } finally {
      submitButton.disabled = false;
    }
  });

  updateCounter();
}

// Сервер отдаёт даты в UTC: во Владивостоке до 10:00 это ещё «вчера»
function localizeDates() {
  document.querySelectorAll('time[data-local-date]').forEach(element => {
    const formatted = formatLocalDate(element.dateTime);
    if (formatted) element.textContent = formatted;
  });
}

initAvatarFallback();
initAboutEditor();
localizeDates();
initThemeSwitcher(document.querySelector('[data-theme-switcher]'));
