import { deleteEvent, fetchParticipantStatus, joinEvent, leaveEvent } from '../api/events.js';
import { h, icon } from '../core/dom.js';
import { formatEventDate, isEventUpcoming } from '../core/format.js';
import { showToast } from '../core/toast.js';
import {
  createCategoryBadge,
  createDurationItem,
  createLocationItem,
  createParticipants
} from './event-card.js';
import { createModal } from './modal.js';

// Окно с подробностями мероприятия: описание, организатор, запись/отмена/удаление.
// Разметка окна — templates/partials/event_detail_modal.html.
// Колбэки сообщают странице об изменениях, чтобы она обновила свои списки.

function createOrganizer(event) {
  if (!event.creator_name && !event.creator_username) return null;

  const content = [
    event.creator_name && h('span', { className: 'organizer-name', text: event.creator_name }),
    event.creator_username && h('span', { className: 'organizer-username', text: `@${event.creator_username}` })
  ];

  const hasProfile = event.creator_id !== null && event.creator_id !== undefined;
  return h('div', { className: 'meta-item event-organizer-meta' },
    icon('person', 'icon'),
    hasProfile
      ? h('a', {
        className: 'event-organizer-profile-link',
        href: `/${encodeURIComponent(String(event.creator_id))}/profile`
      }, content)
      : h('span', { className: 'event-organizer-text' }, content)
  );
}

// Блок участников с классом-хуком: его заменяем после записи/отмены
function createDetailParticipants(event) {
  const block = createParticipants(event);
  block.classList.add('event-participants-count');
  return block;
}

export function createEventDetail(root, {
  onEventUpdated = () => {},
  onEventDeleted = () => {},
  onParticipationChanged = () => {}
} = {}) {
  const body = root.querySelector('.event-detail-body');
  let activeEvent = null;
  let currentStatus = null;
  let actions = null;
  let requestVersion = 0;

  const modal = createModal(root, {
    onClose: () => {
      activeEvent = null;
      currentStatus = null;
      requestVersion += 1;
    }
  });

  const isActive = event => activeEvent === event;

  function showActionButton(label, variant, onClick, disabled = false) {
    actions.replaceChildren(h('button', {
      className: `btn event-detail-action event-detail-action-${variant}`,
      type: 'button',
      text: label,
      disabled,
      onClick
    }));
  }

  function showNotice(message) {
    actions.replaceChildren(h('p', { className: 'event-detail-notice event-detail-error', text: message }));
  }

  function setBusy(label) {
    const button = actions.querySelector('button');
    if (!button) return;
    button.disabled = true;
    button.textContent = label;
  }

  function updateRegisteredCount(event, count) {
    const changed = event.registered_count !== count;
    event.registered_count = count;
    if (isActive(event)) {
      body.querySelector('.event-participants-count')?.replaceWith(createDetailParticipants(event));
    }
    if (changed) onEventUpdated(event);
  }

  function render(event) {
    actions = h('div', { className: 'event-detail-actions' });

    body.replaceChildren(
      h('div', { className: 'event-detail-header' },
        createCategoryBadge(event),
        h('div', { className: 'event-date', text: formatEventDate(event) })
      ),
      h('h2', { id: 'eventDetailTitle', className: 'event-detail-title', text: event.title }),
      h('div', { className: 'event-meta event-detail-meta' },
        createLocationItem(event),
        createDurationItem(event),
        createDetailParticipants(event),
        createOrganizer(event)
      ),
      h('div', { className: 'event-detail-about' },
        h('div', { className: 'event-detail-section-label', text: 'Описание' }),
        h('p', { className: 'event-detail-description', text: event.description || 'Описание не указано' })
      ),
      actions
    );

    showActionButton('Загрузка статуса…', 'secondary', null, true);
  }

  function renderActions(status) {
    currentStatus = status;
    actions.replaceChildren();
    updateRegisteredCount(activeEvent, status.registered_count);
    const upcoming = isEventUpcoming(activeEvent);

    if (status.is_creator) {
      if (upcoming) showActionButton('Удалить мероприятие', 'danger', removeEvent);
      return;
    }

    if (!upcoming) {
      if (status.is_registered) {
        actions.replaceChildren(h('p', { className: 'event-detail-notice', text: 'Вы были записаны' }));
      }
      return;
    }

    if (status.is_registered) {
      showActionButton('Отменить запись', 'secondary', changeParticipation);
    } else {
      showActionButton('Записаться', 'primary', changeParticipation);
    }
  }

  // После неудачного действия перечитываем статус, чтобы кнопка соответствовала серверу
  async function refreshStatus(event) {
    try {
      const status = await fetchParticipantStatus(event.id);
      if (isActive(event)) renderActions(status);
    } catch (error) {
      if (isActive(event)) showNotice(`Не удалось обновить статус: ${error.message}`);
    }
  }

  async function loadStatus(event, version) {
    try {
      const status = await fetchParticipantStatus(event.id);
      if (version === requestVersion && isActive(event)) renderActions(status);
    } catch (error) {
      if (version === requestVersion && isActive(event)) {
        showNotice(`Не удалось загрузить статус участия: ${error.message}`);
      }
    }
  }

  async function changeParticipation() {
    if (!activeEvent || !currentStatus) return;
    const event = activeEvent;
    const wasRegistered = currentStatus.is_registered;
    setBusy(wasRegistered ? 'Отмена записи…' : 'Запись…');

    try {
      if (wasRegistered) {
        const result = await leaveEvent(event.id);
        updateRegisteredCount(event, result?.registered_count ?? Math.max((event.registered_count || 0) - 1, 0));
        showToast('Запись отменена', 'success');
      } else {
        const result = await joinEvent(event.id);
        updateRegisteredCount(event, result.registered_count);
        showToast('Вы записаны на мероприятие', 'success');
      }
      if (isActive(event)) {
        renderActions({ ...currentStatus, is_registered: !wasRegistered, registered_count: event.registered_count });
      }
      onParticipationChanged(event, !wasRegistered);
    } catch (error) {
      showToast(`Ошибка: ${error.message}`, 'error');
      if (isActive(event)) await refreshStatus(event);
    }
  }

  async function removeEvent() {
    if (!activeEvent || !window.confirm('Удалить это мероприятие? Все записи участников также будут удалены.')) {
      return;
    }

    const event = activeEvent;
    setBusy('Удаление…');
    try {
      await deleteEvent(event.id);
      modal.close();
      onEventDeleted(event);
      showToast('Мероприятие удалено', 'success');
    } catch (error) {
      showToast(`Ошибка: ${error.message}`, 'error');
      if (isActive(event)) await refreshStatus(event);
    }
  }

  function open(event) {
    activeEvent = event;
    currentStatus = null;
    const version = ++requestVersion;
    render(event);
    modal.open();
    loadStatus(event, version);
  }

  return { open, close: modal.close };
}
