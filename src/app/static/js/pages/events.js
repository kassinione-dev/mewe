import { fetchEvents } from '../api/events.js';
import { h } from '../core/dom.js';
import { isEventUpcoming } from '../core/format.js';
import { showToast } from '../core/toast.js';
import { createCategoryFilter } from '../components/category-filter.js';
import { createEmptyState, createErrorState } from '../components/empty-state.js';
import { createEventCard } from '../components/event-card.js';
import { createEventDetail } from '../components/event-detail.js';

// Страница поиска: строка поиска, фильтр категорий, список с подгрузкой страниц

const SEARCH_DEBOUNCE_MS = 300;

const page = document.getElementById('events-page');
const searchInput = document.getElementById('searchInput');
const searchClear = document.getElementById('searchClear');
const container = document.getElementById('eventsContainer');
const resultsBar = document.getElementById('resultsBar');
const resultsCount = document.getElementById('resultsCount');
const loadMoreWrap = document.getElementById('loadMoreWrap');
const loadMoreButton = document.getElementById('loadMoreBtn');

const state = {
  events: [],
  query: '',
  categoryIds: [],
  page: 1,
  lastPage: 1,
  total: 0,
  // Номер последнего запроса: ответы устаревших запросов отбрасываем
  version: 0
};
let debounceTimeout;

const categoryFilter = createCategoryFilter({
  tab: document.getElementById('categoriesTab'),
  count: document.getElementById('categoriesCount'),
  chips: document.getElementById('selectedCategoryFilter'),
  modalRoot: document.getElementById('categoriesModal'),
  onChange: () => loadEvents()
});

const eventDetail = createEventDetail(document.getElementById('eventDetailModal'), {
  onEventUpdated: () => renderEvents(state.events),
  onEventDeleted: deleted => {
    state.total = Math.max(state.total - 1, 0);
    renderEvents(state.events.filter(event => event.id !== deleted.id));
  }
});

function currentQuery() {
  return searchInput.value.trim();
}

function syncSearchClear() {
  searchClear.hidden = !searchInput.value;
}

function resetFilters() {
  clearTimeout(debounceTimeout);
  searchInput.value = '';
  syncSearchClear();
  categoryFilter.clear();
  loadEvents();
}

function updateFooter() {
  resultsBar.hidden = state.total === 0 || state.events.length === 0;
  resultsCount.textContent = `Найдено: ${state.total}`;
  loadMoreWrap.hidden = state.page >= state.lastPage;
}

function applyPagination(pagination, fallbackPage) {
  state.page = pagination?.current_page ?? fallbackPage;
  state.lastPage = pagination?.last_page ?? state.page;
  state.total = pagination?.total ?? state.events.length;
}

function emptyState() {
  const hasFilters = Boolean(state.query) || state.categoryIds.length > 0;
  if (hasFilters) {
    return createEmptyState({
      icon: 'fa-magnifying-glass',
      title: 'Ничего не найдено',
      text: 'Попробуйте изменить запрос или убрать фильтры.',
      action: { label: 'Сбросить фильтры', onClick: resetFilters }
    });
  }
  return createEmptyState({
    icon: 'fa-calendar',
    title: 'Пока нет предстоящих мероприятий',
    text: 'Загляните позже или создайте своё.',
    action: { label: 'Создать мероприятие', href: page.dataset.createUrl }
  });
}

function renderEvents(events) {
  // Список мог устареть, пока страница была открыта: начавшиеся не показываем
  state.events = events.filter(event => isEventUpcoming(event));
  updateFooter();

  if (!state.events.length) {
    container.replaceChildren(emptyState());
    return;
  }
  container.replaceChildren(...state.events.map(event => createEventCard(event)));
}

function appendEvents(events) {
  const known = new Set(state.events.map(event => event.id));
  const fresh = events.filter(event => isEventUpcoming(event) && !known.has(event.id));
  state.events.push(...fresh);
  container.append(...fresh.map(event => createEventCard(event)));
  updateFooter();
}

function setLoading(isLoading) {
  container.classList.toggle('is-loading', isLoading);
  container.setAttribute('aria-busy', String(isLoading));
}

function showSkeleton() {
  container.replaceChildren(...Array.from({ length: 3 }, () =>
    h('div', { className: 'event-skeleton', 'aria-hidden': 'true' })
  ));
}

async function loadEvents() {
  const version = ++state.version;
  state.query = currentQuery();
  state.categoryIds = categoryFilter.ids;

  if (container.querySelector('.event-card')) setLoading(true);
  else showSkeleton();

  try {
    const data = await fetchEvents({ search: state.query, categoryIds: state.categoryIds });
    if (version !== state.version) return;
    applyPagination(data.pagination, 1);
    renderEvents(data.events);
  } catch (error) {
    if (version !== state.version) return;
    state.events = [];
    resultsBar.hidden = true;
    loadMoreWrap.hidden = true;
    container.replaceChildren(createErrorState(`Ошибка загрузки мероприятий: ${error.message}`, loadEvents));
  } finally {
    if (version === state.version) setLoading(false);
  }
}

async function loadMoreEvents() {
  const version = state.version;
  const label = loadMoreButton.textContent;
  loadMoreButton.disabled = true;
  loadMoreButton.textContent = 'Загрузка…';

  try {
    const data = await fetchEvents({
      search: state.query,
      categoryIds: state.categoryIds,
      page: state.page + 1
    });
    if (version !== state.version) return;
    applyPagination(data.pagination, state.page + 1);
    appendEvents(data.events);
  } catch (error) {
    if (version === state.version) showToast(`Ошибка: ${error.message}`, 'error');
  } finally {
    loadMoreButton.disabled = false;
    loadMoreButton.textContent = label;
  }
}

container.addEventListener('click', event => {
  const card = event.target.closest('.event-card');
  if (!card) return;
  const selected = state.events.find(item => String(item.id) === card.dataset.eventId);
  if (selected) eventDetail.open(selected);
});

searchInput.addEventListener('input', () => {
  syncSearchClear();
  clearTimeout(debounceTimeout);
  debounceTimeout = setTimeout(loadEvents, SEARCH_DEBOUNCE_MS);
});

searchInput.addEventListener('keydown', event => {
  if (event.key !== 'Enter') return;
  clearTimeout(debounceTimeout);
  loadEvents();
  searchInput.blur();
});

searchClear.addEventListener('click', () => {
  clearTimeout(debounceTimeout);
  searchInput.value = '';
  syncSearchClear();
  loadEvents();
  searchInput.focus();
});

loadMoreButton.addEventListener('click', loadMoreEvents);

loadEvents();
