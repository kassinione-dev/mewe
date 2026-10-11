import { createEvent } from '../api/events.js';
import { toDateInputValue } from '../core/format.js';
import { showToast } from '../core/toast.js';

// Форма создания мероприятия: счётчики символов, проверка полей, отправка.
// Лимиты приходят из разметки (maxlength, min/max, data-min-duration/data-max-duration),
// а их источник — field_limits.py на бэкенде.
export function initEventForm(form, { onCreated }) {
  const counters = [...form.querySelectorAll('[data-counter-for]')];
  const requiredFields = [...form.querySelectorAll('[required]')];
  const limitedFields = [...form.querySelectorAll('input[maxlength], textarea[maxlength]')];
  const submitButton = form.querySelector('[type="submit"]');

  function updateCounters() {
    counters.forEach(counter => {
      const field = form.elements[counter.dataset.counterFor];
      counter.textContent = `${field.value.length} / ${field.maxLength}`;
    });
  }

  function markInvalid(field, invalid) {
    field.classList.toggle('invalid', invalid);
    return !invalid;
  }

  function validate() {
    const lengthsValid = limitedFields
      .map(field => markInvalid(field, field.value.length > field.maxLength))
      .every(Boolean);
    if (!lengthsValid) {
      showToast('Превышена допустимая длина текстового поля', 'error');
      return null;
    }

    const filled = requiredFields
      .map(field => markInvalid(field, !field.value))
      .every(Boolean);
    if (!filled) return null;

    const startsAt = new Date(`${form.elements.date.value}T${form.elements.time.value}`);
    if (startsAt <= new Date()) {
      showToast('Дата и время мероприятия должны быть в будущем', 'error');
      return null;
    }

    const durationMinutes = Number(form.elements.duration_hours.value) * 60
      + Number(form.elements.duration_minutes.value);
    if (
      durationMinutes < Number(form.dataset.minDuration)
      || durationMinutes > Number(form.dataset.maxDuration)
    ) {
      const range = form.querySelector('[data-duration-range]').textContent;
      showToast(`Продолжительность должна быть ${range}`, 'error');
      return null;
    }

    return {
      title: form.elements.title.value.trim(),
      location: form.elements.location.value.trim(),
      description: form.elements.description.value.trim(),
      category: Number(form.elements.category.value),
      max_participants: Number(form.elements.participants.value),
      duration_minutes: durationMinutes,
      event_date: startsAt.toISOString()
    };
  }

  form.elements.date.min = toDateInputValue(new Date());

  form.addEventListener('input', event => {
    updateCounters();
    if (event.target.required) markInvalid(event.target, !event.target.value);
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    const payload = validate();
    if (!payload) return;

    submitButton.disabled = true;
    try {
      const created = await createEvent(payload);
      showToast('Мероприятие создано!', 'success');
      form.reset();
      updateCounters();
      onCreated(created);
    } catch (error) {
      showToast(`Ошибка: ${error.message}`, 'error');
    } finally {
      submitButton.disabled = false;
    }
  });

  updateCounters();
}
