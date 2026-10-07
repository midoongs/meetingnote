'use strict';

// ===== 공통 도우미 =====
const el = (id) => document.getElementById(id);
const role = (name) => document.querySelector(`[data-role="${name}"]`);

// 서버 데이터는 textContent 로만 넣는다 (innerHTML 금지)
function h(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' });
}

function toLocalInputValue(date) {
  const shifted = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return shifted.toISOString().slice(0, 16);
}

function splitLines(text) {
  return (text || '').split('\n').map((line) => line.trim()).filter(Boolean);
}

function isSplitFailed(note) {
  return !(note.summary || '').trim() && !(note.decisions || '').trim() && !(note.todos || '').trim();
}

async function api(path, options) {
  let response;
  try {
    response = await fetch(path, options);
  } catch {
    throw new Error('서버에 연결하지 못했습니다.');
  }
  if (response.status === 204) return null;
  let data = null;
  try {
    data = await response.json();
  } catch {
    // 본문이 JSON 이 아니면 아래에서 상태 코드로 처리한다
  }
  if (!response.ok) {
    const detail = data && data.detail;
    throw new Error(typeof detail === 'string' ? detail : '입력값을 확인해 주세요.');
  }
  return data;
}

// ===== 테마 (라이트/다크, localStorage, 초기값은 시스템 설정) =====
const THEME_KEY = 'theme';

function readStoredTheme() {
  try {
    return localStorage.getItem(THEME_KEY);
  } catch {
    return null;
  }
}

function applyTheme(theme) {
  document.documentElement.classList.toggle('dark', theme === 'dark');
}

function initTheme() {
  const stored = readStoredTheme();
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(stored === 'light' || stored === 'dark' ? stored : systemDark ? 'dark' : 'light');
  role('themeToggle').addEventListener('click', () => {
    const next = document.documentElement.classList.contains('dark') ? 'light' : 'dark';
    applyTheme(next);
    try {
      localStorage.setItem(THEME_KEY, next);
    } catch {
      // 저장이 막힌 환경에서는 이번 방문에만 적용된다
    }
  });
}

// ===== 화면 전환 =====
const VIEWS = ['list', 'new', 'todos'];
const TAB_ON = ['bg-slate-800', 'text-white', 'dark:bg-slate-100', 'dark:text-slate-900'];
const TAB_OFF = ['text-slate-600', 'hover:bg-slate-200/70', 'dark:text-slate-300', 'dark:hover:bg-slate-700/70'];

let currentView = 'list';

function showView(name) {
  currentView = VIEWS.includes(name) ? name : 'list';
  closeModal();
  document.querySelectorAll('[data-view]').forEach((section) => {
    section.classList.toggle('hidden', section.dataset.view !== currentView);
  });
  document.querySelectorAll('[data-nav]').forEach((tab) => {
    const active = tab.dataset.nav === currentView;
    tab.classList.remove(...TAB_ON, ...TAB_OFF);
    tab.classList.add(...(active ? TAB_ON : TAB_OFF));
    tab.setAttribute('aria-current', active ? 'page' : 'false');
  });
  if (currentView === 'list') loadNotes();
  if (currentView === 'todos') loadTodos();
}

function initNav() {
  document.querySelectorAll('[data-nav]').forEach((tab) => {
    tab.addEventListener('click', () => {
      location.hash = tab.dataset.nav;
    });
  });
  window.addEventListener('hashchange', () => showView(location.hash.slice(1)));
}

// ===== 세 갈래 표시 (넣기 결과와 상세 창이 같이 쓴다) =====
const PART_STYLES = {
  summary: { title: '요약', bar: 'border-cyan-600', text: 'text-cyan-700 dark:text-cyan-400' },
  decisions: { title: '결정사항', bar: 'border-orange-600', text: 'text-orange-700 dark:text-orange-400' },
  todos: { title: '할 일', bar: 'border-emerald-600', text: 'text-emerald-700 dark:text-emerald-400' },
};

function partCard(kind, lines) {
  const style = PART_STYLES[kind];
  const card = h('div', `rounded-xl border-l-4 ${style.bar} bg-white/70 p-4 shadow-sm dark:bg-slate-900/50`);
  card.dataset.part = kind;
  card.append(h('h3', `mb-2 font-semibold ${style.text}`, style.title));
  if (!lines.length) {
    card.append(h('p', 'text-sm text-slate-400', '없음'));
    return card;
  }
  const list = h('ul', 'space-y-1.5 text-sm');
  lines.forEach((line) => {
    if (kind === 'todos') {
      const [what, who, when] = line.split('|').map((part) => part.trim());
      const item = h('li');
      item.append(h('span', '', what || ''));
      const sub = [who || '미정', when].filter(Boolean).join(' · ');
      item.append(h('span', 'block text-xs text-slate-500 dark:text-slate-400', sub));
      list.append(item);
    } else {
      list.append(h('li', '', line));
    }
  });
  card.append(list);
  return card;
}

function renderParts(container, note) {
  container.replaceChildren();
  if (isSplitFailed(note)) {
    const notice = h(
      'p',
      'rounded-xl border border-amber-400/60 bg-amber-100/70 p-4 text-sm text-amber-900 dark:bg-amber-900/30 dark:text-amber-200',
      '구분 실패: 본문은 저장되었지만 요약 · 결정사항 · 할 일로 나누지 못했습니다.',
    );
    notice.dataset.part = 'failed';
    container.append(notice);
    return;
  }
  const grid = h('div', 'grid grid-cols-1 gap-4 md:grid-cols-3');
  grid.append(
    partCard('summary', splitLines(note.summary)),
    partCard('decisions', splitLines(note.decisions)),
    partCard('todos', splitLines(note.todos)),
  );
  container.append(grid);
}

// ===== 화면 1: 목록 =====
let listRequestId = 0;
let searchTimer = null;

function buildCard(note) {
  const card = h(
    'button',
    'glass rounded-2xl p-5 text-left transition hover:-translate-y-0.5 hover:shadow-xl focus:outline-none focus:ring-2 focus:ring-cyan-500',
  );
  card.type = 'button';
  card.dataset.noteId = String(note.id);
  card.append(h('h3', 'break-words text-lg font-bold', note.title));
  const meta = [formatDateTime(note.met_at), (note.attendees || '').trim()].filter(Boolean).join(' · ');
  card.append(h('p', 'mt-1 text-sm text-slate-500 dark:text-slate-400', meta));
  if (isSplitFailed(note)) {
    card.append(h('p', 'mt-3 text-sm text-amber-700 dark:text-amber-400', '구분 실패'));
  } else {
    const firstLine = splitLines(note.summary)[0] || '';
    card.append(h('p', 'mt-3 line-clamp-2 break-words text-sm', firstLine));
  }
  card.addEventListener('click', () => openModal(note.id));
  return card;
}

async function loadNotes() {
  const requestId = ++listRequestId;
  const params = new URLSearchParams();
  if (el('q').value.trim()) params.set('q', el('q').value.trim());
  if (el('from').value) params.set('from', el('from').value);
  if (el('to').value) params.set('to', el('to').value);
  const status = role('listStatus');
  try {
    const notes = await api('/api/notes' + (params.size ? `?${params}` : ''));
    if (requestId !== listRequestId) return; // 더 최근 검색이 있으면 이 결과는 버린다
    el('cards').replaceChildren(...notes.map(buildCard));
    status.textContent = notes.length ? `${notes.length}건` : '조건에 맞는 회의록이 없습니다.';
  } catch (error) {
    if (requestId !== listRequestId) return;
    el('cards').replaceChildren();
    status.textContent = error.message;
  }
}

function initList() {
  const onInput = () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadNotes, 250);
  };
  ['q', 'from', 'to'].forEach((id) => el(id).addEventListener('input', onInput));
}

// ===== 화면 2: 넣기 =====
const MAX_UPLOAD_BYTES = 25 * 1024 * 1024;

function initNewForm() {
  el('metAt').value = toLocalInputValue(new Date());

  el('btnUp').addEventListener('click', async () => {
    const status = role('upStatus');
    const file = el('file').files[0];
    if (!file) {
      status.textContent = '녹취 파일을 먼저 선택하세요.';
      return;
    }
    if (!/\.(mp3|wav)$/i.test(file.name)) {
      status.textContent = 'mp3, wav 파일만 올릴 수 있습니다.';
      return;
    }
    if (file.size > MAX_UPLOAD_BYTES) {
      status.textContent = '파일은 25MB 이하여야 합니다.';
      return;
    }
    el('btnUp').disabled = true;
    status.textContent = '받아쓰는 중… (파일이 길면 1~2분 걸립니다)';
    try {
      const form = new FormData();
      form.append('file', file);
      const data = await api('/api/upload', { method: 'POST', body: form });
      el('body').value = data.text;
      status.textContent = '받아쓰기 완료. 내용을 확인하고 정리하기를 누르세요.';
    } catch (error) {
      status.textContent = `받아쓰기 실패: ${error.message}`;
    } finally {
      el('btnUp').disabled = false;
    }
  });

  el('btnSave').addEventListener('click', async () => {
    const status = role('saveStatus');
    const title = el('title').value.trim();
    const body = el('body').value.trim();
    const metAt = new Date(el('metAt').value); // datetime-local 은 로컬 시각이므로 UTC 로 바꿔 보낸다
    if (!title) return void (status.textContent = '제목을 입력하세요.');
    if (Number.isNaN(metAt.getTime())) return void (status.textContent = '일시를 입력하세요.');
    if (!body) return void (status.textContent = '본문을 입력하세요.');

    el('btnSave').disabled = true;
    status.textContent = '정리하는 중…';
    try {
      const note = await api('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          met_at: metAt.toISOString(),
          attendees: el('attendees').value.trim() || null,
          body,
        }),
      });
      renderParts(el('result'), note);
      el('result').classList.remove('hidden');
      status.textContent = isSplitFailed(note) ? '저장됨 (구분 실패)' : '저장됨';
      ['title', 'attendees', 'body'].forEach((id) => (el(id).value = ''));
      el('file').value = '';
      el('metAt').value = toLocalInputValue(new Date());
      role('upStatus').textContent = '';
    } catch (error) {
      status.textContent = `저장 실패: ${error.message}`;
    } finally {
      el('btnSave').disabled = false;
    }
  });
}

// ===== 화면 3: 상세 (겹침 창) =====
let modalNote = null;
let deleteArmed = false;
let deleteTimer = null;

function resetDeleteButton() {
  deleteArmed = false;
  clearTimeout(deleteTimer);
  role('mDelete').textContent = '삭제';
}

function setModalStatus(text) {
  role('mStatus').textContent = text;
}

function renderModal(note) {
  role('mHeading').textContent = note.title;
  const meta = [formatDateTime(note.met_at), (note.attendees || '').trim()].filter(Boolean).join(' · ');
  role('mMeta').textContent = meta;
  renderParts(role('mParts'), note);
  role('mBody').textContent = note.body;
  el('mTitle').value = note.title;
}

async function openModal(noteId) {
  try {
    modalNote = await api(`/api/notes/${noteId}`);
  } catch (error) {
    role('listStatus').textContent = error.message;
    return;
  }
  resetDeleteButton();
  setModalStatus('삭제는 한 번 더 눌러야 지워집니다.');
  renderModal(modalNote);
  role('mBody').closest('details').open = false;
  el('modal').classList.remove('hidden');
  el('modal').classList.add('flex');
  el('mTitle').blur();
}

function closeModal() {
  el('modal').classList.add('hidden');
  el('modal').classList.remove('flex');
  resetDeleteButton();
  modalNote = null;
}

function refreshCurrentView() {
  if (currentView === 'list') loadNotes();
  if (currentView === 'todos') loadTodos();
}

function initModal() {
  const modal = el('modal');
  modal.addEventListener('click', (event) => {
    if (event.target === modal) closeModal(); // 바깥 어두운 영역
  });
  role('mClose').addEventListener('click', closeModal);
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });

  role('mSave').addEventListener('click', async () => {
    if (!modalNote) return;
    const title = el('mTitle').value.trim();
    if (!title) return setModalStatus('제목을 입력하세요.');
    try {
      // PUT 은 필수 3개(title, met_at, body)를 모두 받는다. 나머지는 보내지 않아 그대로 남는다
      const updated = await api(`/api/notes/${modalNote.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, met_at: modalNote.met_at, body: modalNote.body }),
      });
      modalNote = updated;
      renderModal(updated);
      setModalStatus('제목을 수정했습니다.');
      refreshCurrentView();
    } catch (error) {
      setModalStatus(`수정 실패: ${error.message}`);
    }
  });

  role('mDelete').addEventListener('click', async () => {
    if (!modalNote) return;
    if (!deleteArmed) {
      deleteArmed = true;
      role('mDelete').textContent = '정말 삭제';
      setModalStatus('한 번 더 누르면 삭제됩니다.');
      deleteTimer = setTimeout(() => {
        resetDeleteButton();
        setModalStatus('삭제는 한 번 더 눌러야 지워집니다.');
      }, 4000);
      return;
    }
    try {
      await api(`/api/notes/${modalNote.id}`, { method: 'DELETE' });
      closeModal();
      refreshCurrentView();
    } catch (error) {
      resetDeleteButton();
      setModalStatus(`삭제 실패: ${error.message}`);
    }
  });
}

// ===== 화면 4: 할 일 =====
async function loadTodos() {
  const status = role('todoStatus');
  const body = el('todoBody');
  try {
    const todos = await api('/api/todos');
    body.replaceChildren();
    if (!todos.length) {
      const row = h('tr');
      const cell = h('td', 'px-4 py-6 text-center text-slate-400', '할 일이 없습니다.');
      cell.colSpan = 4;
      row.append(cell);
      body.append(row);
    }
    todos.forEach((todo) => {
      const row = h('tr', 'odd:bg-white/40 dark:odd:bg-slate-900/30');
      row.append(h('td', 'px-4 py-3 break-words', todo.what));
      row.append(h('td', 'px-4 py-3 font-semibold whitespace-nowrap', todo.who));
      row.append(h('td', 'px-4 py-3 whitespace-nowrap', todo.when));
      const meeting = h('td', 'px-4 py-3');
      const link = h('button', 'text-left text-cyan-700 underline-offset-2 hover:underline dark:text-cyan-400', todo.note_title);
      link.type = 'button';
      link.addEventListener('click', () => openModal(todo.note_id));
      meeting.append(link);
      row.append(meeting);
      body.append(row);
    });
    status.textContent = todos.length ? `${todos.length}건 · 회의 날짜 오래된 순` : '';
  } catch (error) {
    body.replaceChildren();
    status.textContent = error.message;
  }
}

// ===== 시작 =====
initTheme();
initNav();
initList();
initNewForm();
initModal();
showView(location.hash.slice(1));
