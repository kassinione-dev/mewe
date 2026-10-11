import { requestJson } from '../core/http.js';

// Все пути API мероприятий — здесь, страницы и компоненты их не знают

const EVENTS_URL = '/api/events';

const eventUrl = id => `${EVENTS_URL}/${encodeURIComponent(id)}`;
const participantUrl = id => `${eventUrl(id)}/participants/me`;

export function fetchEvents({ search = '', categoryIds = [], page = 1 } = {}) {
  const url = new URL(EVENTS_URL, window.location.origin);
  if (search) url.searchParams.set('search', search);
  if (page > 1) url.searchParams.set('page', String(page));
  categoryIds.forEach(id => url.searchParams.append('category', id));
  return requestJson(url);
}

export function fetchCreatedEvents() {
  return requestJson('/api/users/me/events');
}

export function fetchParticipatingEvents() {
  return requestJson('/api/users/me/participations');
}

export function createEvent(payload) {
  return requestJson(EVENTS_URL, { method: 'POST', body: payload });
}

export function deleteEvent(id) {
  return requestJson(eventUrl(id), { method: 'DELETE' });
}

export function fetchParticipantStatus(id) {
  return requestJson(participantUrl(id));
}

export function joinEvent(id) {
  return requestJson(participantUrl(id), { method: 'PUT' });
}

export function leaveEvent(id) {
  return requestJson(participantUrl(id), { method: 'DELETE' });
}
