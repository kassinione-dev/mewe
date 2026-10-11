// Форматирование для человека. Сервер отдаёт время в ISO (UTC), показываем в поясе пользователя.

const DAY_MS = 86400000;
const TIME_FORMAT = { hour: '2-digit', minute: '2-digit' };

// pluralize(5, 'место', 'места', 'мест') → 'мест'
export function pluralize(n, one, few, many) {
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
}

export function formatDuration(durationMinutes) {
  const hours = Math.floor(durationMinutes / 60);
  const minutes = durationMinutes % 60;
  const parts = [];
  if (hours) parts.push(`${hours} ${pluralize(hours, 'час', 'часа', 'часов')}`);
  if (minutes) parts.push(`${minutes} ${pluralize(minutes, 'минута', 'минуты', 'минут')}`);
  return parts.join(' ');
}

export function spotsLeftLabel(n) {
  return `еще ${n} ${pluralize(n, 'место', 'места', 'мест')}`;
}

function eventTime(event) {
  if (!event.event_date) return NaN;
  return new Date(event.event_date).getTime();
}

export function isEventUpcoming(event, now = Date.now()) {
  const time = eventTime(event);
  return Number.isFinite(time) && time > now;
}

export function isEventPast(event, now = Date.now()) {
  const time = eventTime(event);
  return Number.isFinite(time) && time <= now;
}

// «Сегодня, 18:00–19:30», «Завтра, 10:00», «вс, 11 окт., 13:00–17:00»
export function formatEventDate(event) {
  const start = new Date(eventTime(event));
  if (Number.isNaN(start.getTime())) return '';

  const now = new Date();
  const dayDiff = Math.round(
    (new Date(start.getFullYear(), start.getMonth(), start.getDate()) -
      new Date(now.getFullYear(), now.getMonth(), now.getDate())) / DAY_MS
  );

  let time = start.toLocaleTimeString('ru-RU', TIME_FORMAT);

  // Диапазон показываем, только если мероприятие заканчивается в тот же день
  if (Number.isFinite(event.duration_minutes) && event.duration_minutes > 0) {
    const end = new Date(start.getTime() + event.duration_minutes * 60000);
    if (end.toDateString() === start.toDateString()) {
      time = `${time}–${end.toLocaleTimeString('ru-RU', TIME_FORMAT)}`;
    }
  }

  if (dayDiff === 0) return `Сегодня, ${time}`;
  if (dayDiff === 1) return `Завтра, ${time}`;

  const options = { day: 'numeric', month: 'short', weekday: 'short' };
  if (start.getFullYear() !== now.getFullYear()) options.year = 'numeric';
  return `${start.toLocaleDateString('ru-RU', options)}, ${time}`;
}

// Дата для <input type="date"> по часам пользователя (toISOString дал бы дату в UTC)
export function toDateInputValue(date) {
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, '0'),
    String(date.getDate()).padStart(2, '0'),
  ].join('-');
}
