import { fetchCreatedEvents, fetchParticipatingEvents } from '../api/events.js';
import { h } from '../core/dom.js';
import { isEventPast } from '../core/format.js';
import { session } from '../core/storage.js';
import { createEmptyState, createErrorState } from '../components/empty-state.js';
import { createEventCard } from '../components/event-card.js';
import { createEventDetail } from '../components/event-detail.js';
import { initEventForm } from '../components/event-form.js';
import { createModal } from '../components/modal.js';

// «Мои мероприятия»: вкладки «Я участвую» / «Я организую», форма создания

const TAB_STORAGE_KEY = 'myEventsTab';

const page = document.getElementById('my-events-page');
const tabButtons = [...document.querySelectorAll('.my-events-tab')];
const createButton = document.querySelector('.new-event-btn');

// Описание каждой вкладки: где рисовать, как загружать, что показать в пустом списке
const sections = {
  participations: {
    container: document.getElementById('participationsContainer'),
    count: document.getElementById('participationsCount'),
    load: fetchParticipatingEvents,
    errorText: 'Ошибка загрузки записей',
    cardOptions: {},
    empty: {
      icon: 'group',
      title: 'Вы пока не записались на мероприятия',
      text: 'Найдите интересное в общем списке и запишитесь.',
      action: { label: 'Найти мероприятие', href: page.dataset.searchUrl }
    },
    events: []
  },
  created: {
    container: document.getElementById('createdEventsContainer'),
    count: document.getElementById('createdCount'),
    load: fetchCreatedEvents,
    errorText: 'Ошибка загрузки мероприятий',
    // организатор здесь всегда сам пользователь — строка с ником только повторяется
    cardOptions: { showOrganizer: false },
    empty: {
      icon: 'calendar_add_on',
      title: 'Вы пока не создали мероприятий',
      text: 'Оно появится в общем списке, и на него смогут записаться другие.',
      action: { label: 'Создать мероприятие', onClick: () => createEventModal.open() }
    },
    events: []
  }
};

function renderSection(section) {
  const { container, events, empty, cardOptions } = section;
  let upcomingCount = 0;

  if (!events.length) {
    container.replaceChildren(createEmptyState(empty));
  } else {
    const upcoming = events.filter(event => !isEventPast(event));
    const past = events.filter(event => isEventPast(event));
    upcomingCount = upcoming.length;

    const children = upcoming.map(event => createEventCard(event, cardOptions));
    if (!upcoming.length) {
      children.push(h('p', { className: 'no-events', text: 'Нет предстоящих мероприятий' }));
    }
    if (past.length) {
      children.push(h('details', { className: 'past-events' },
        h('summary', { text: `Прошедшие мероприятия (${past.length})` }),
        h('div', { className: 'events-container past-events-container' },
          past.map(event => createEventCard(event, cardOptions))
        )
      ));
    }
    container.replaceChildren(...children);
  }

  // Бейдж на вкладке — число предстоящих
  section.count.textContent = String(upcomingCount);
  section.count.hidden = upcomingCount === 0;
}

async function loadSection(section) {
  try {
    const data = await section.load();
    section.events = data.events;
    renderSection(section);
  } catch (error) {
    section.container.replaceChildren(createErrorState(`${section.errorText}: ${error.message}`));
  }
}

function renderAll() {
  Object.values(sections).forEach(renderSection);
}

const eventDetail = createEventDetail(document.getElementById('eventDetailModal'), {
  onEventUpdated: updated => {
    Object.values(sections).forEach(section => {
      const match = section.events.find(event => event.id === updated.id);
      if (match) match.registered_count = updated.registered_count;
    });
    renderAll();
  },
  onEventDeleted: deleted => {
    Object.values(sections).forEach(section => {
      section.events = section.events.filter(event => event.id !== deleted.id);
    });
    renderAll();
  },
  onParticipationChanged: () => loadSection(sections.participations)
});

Object.values(sections).forEach(section => {
  section.container.addEventListener('click', event => {
    const card = event.target.closest('.event-card');
    if (!card) return;
    const selected = section.events.find(item => String(item.id) === card.dataset.eventId);
    if (selected) eventDetail.open(selected);
  });
});

// ---------- Вкладки ----------

function setTab(name, { focus = false } = {}) {
  tabButtons.forEach(tab => {
    const active = tab.dataset.tab === name;
    tab.classList.toggle('is-active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    if (active && focus) tab.focus();
  });
  session.set(TAB_STORAGE_KEY, name);
}

tabButtons.forEach((tab, index) => {
  tab.addEventListener('click', () => setTab(tab.dataset.tab));
  tab.addEventListener('keydown', event => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    event.preventDefault();
    const step = event.key === 'ArrowRight' ? 1 : -1;
    const next = tabButtons[(index + step + tabButtons.length) % tabButtons.length];
    setTab(next.dataset.tab, { focus: true });
  });
});

const storedTab = session.get(TAB_STORAGE_KEY);
setTab(storedTab in sections ? storedTab : 'participations');

// ---------- Создание ----------

const createEventModal = createModal(document.getElementById('createEventModal'), {
  // «Создать» открывает форму и переключает на «Я организую», где появится новое мероприятие
  onOpen: () => {
    page.classList.add('is-creating');
    setTab('created');
  },
  onClose: () => page.classList.remove('is-creating')
});

createButton.addEventListener('click', createEventModal.open);

initEventForm(document.getElementById('event-form'), {
  onCreated: () => {
    createEventModal.close();
    loadSection(sections.created);
  }
});

Object.values(sections).forEach(loadSection);
