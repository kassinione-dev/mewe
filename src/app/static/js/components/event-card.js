import { h, icon } from '../core/dom.js';
import { formatDuration, formatEventDate, isEventPast, spotsLeftLabel } from '../core/format.js';

// Строительные блоки карточки мероприятия; окно подробностей собирается из них же

export function createCategoryBadge(event) {
  return h('div', { className: 'event-category' },
    icon(event.category_icon || 'label'),
    h('span', { className: 'event-category-name', text: event.category_name || 'Без категории' })
  );
}

export function createMetaItem(iconName, text) {
  return h('div', { className: 'meta-item' }, icon(iconName, 'icon'), text);
}

export function createLocationItem(event) {
  return createMetaItem('location_on', event.location);
}

export function createDurationItem(event) {
  return createMetaItem('schedule', formatDuration(event.duration_minutes));
}

// Счётчик «1 / 2», статус («еще 1 место» / «мест нет» / «завершено») и полоса заполненности
export function createParticipants(event) {
  const registered = event.registered_count || 0;
  const max = event.max_participants;
  const left = Math.max(max - registered, 0);
  const full = left === 0;
  const past = isEventPast(event);

  let statusClass = '';
  if (past) statusClass = ' past';
  else if (full) statusClass = ' full';

  let statusText = spotsLeftLabel(left);
  if (past) statusText = 'завершено';
  else if (full) statusText = 'мест нет';

  return h('div', { className: 'event-participants' },
    h('div', { className: 'meta-item' },
      icon('group', 'icon'),
      `${registered} / ${max}`,
      h('span', { className: `participants-status${statusClass}`, text: statusText })
    ),
    h('div', { className: 'participants-bar' },
      h('div', {
        className: `participants-bar-fill${full ? ' full' : ''}`,
        style: { width: `${max ? Math.min(registered / max, 1) * 100 : 0}%` }
      })
    )
  );
}

function createOrganizerLine(event) {
  if (!event.creator_username && !event.creator_name) return null;

  return h('div', { className: 'event-organizer' },
    icon('person', 'icon'),
    h('span', { text: event.creator_username ? `@${event.creator_username}` : event.creator_name })
  );
}

// showOrganizer: false — для «Я организую», где организатор всегда сам пользователь
export function createEventCard(event, { showOrganizer = true } = {}) {
  return h('div', { className: 'event-card', dataset: { eventId: event.id }, tabindex: '0' },
    h('div', { className: 'event-header' },
      createCategoryBadge(event),
      h('div', { className: 'event-date', text: formatEventDate(event) })
    ),
    h('h3', { className: 'event-title', text: event.title }),
    h('div', { className: 'event-meta' },
      createLocationItem(event),
      createDurationItem(event),
      createParticipants(event)
    ),
    showOrganizer && createOrganizerLine(event)
  );
}
