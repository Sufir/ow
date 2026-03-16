// === Namespace (по ?id= или имени файла) ===
const params = new URLSearchParams(location.search);
const ns = params.get('id') || location.pathname.split('/').pop().split('.')[0] || 'default';

// Мини-утилиты: DOM-хелперы, безопасный localStorage и дебаунс
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const lsGet = (key, fallback = null) => {
  try {
    const v = localStorage.getItem(key);
    return v === null ? fallback : v;
  } catch {
    return fallback;
  }
};
const lsSet = (key, value) => {
  try {
    localStorage.setItem(key, value);
  } catch {}
};

const debounce = (fn, ms = 150) => {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
};

// Добавлено: учёт несохранённых изменений и подавление предупреждения после экспорта
let hasUnsavedChanges = false;

function markUnsaved() {
  hasUnsavedChanges = true;
}

function markExported() {
  hasUnsavedChanges = false;
}

window.addEventListener('beforeunload', (e) => {
  if (!hasUnsavedChanges) return;
  e.preventDefault();
  e.returnValue = ''; // стандартный способ показать диалог подтверждения
});

// === Сохранение заголовка фракции ===
const storageKey = `faction-name:${ns}`;
const nameEl = document.querySelector('.faction-name');
const savedName = lsGet(storageKey);
if (nameEl && savedName) nameEl.textContent = savedName;

function updateDocumentTitle() {
  const fallback = 'Без названия';
  const factionName = (nameEl?.textContent || '').trim() || fallback;
  document.title = `Faction Card — ${factionName}`;
}

function fitFactionName() {
  if (!nameEl) return;
  const MAX_PT = 20;
  const MIN_PT = 8;
  const available = nameEl.clientWidth;

  nameEl.style.fontSize = `${MAX_PT}pt`;
  if (nameEl.scrollWidth <= available) return;

  let low = MIN_PT;
  let high = MAX_PT;
  while (high - low > 0.1) {
    const mid = (low + high) / 2;
    nameEl.style.fontSize = `${mid}pt`;
    if (nameEl.scrollWidth <= available) {
      low = mid;
    } else {
      high = mid;
    }
  }
  nameEl.style.fontSize = `${Math.max(MIN_PT, Math.floor(low * 100) / 100)}pt`;
}
if (nameEl) {
  const applyFit = debounce(() => fitFactionName(), 100);
  updateDocumentTitle();

  nameEl.addEventListener('input', () => {
    lsSet(storageKey, nameEl.textContent.trim());
    updateDocumentTitle();
    applyFit();
  });

  const titleObserver = new MutationObserver(() => updateDocumentTitle());
  titleObserver.observe(nameEl, {
    childList: true,
    characterData: true,
    subtree: true
  });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(applyFit);
  } else {
    applyFit();
  }

  window.addEventListener('resize', applyFit);
}

// === Таблица и панель ===
const table = document.querySelector('.unit-table');
const tbody = table?.querySelector('tbody');
const addRowBtn = document.getElementById('add-row-btn');
const addSepBtn = document.getElementById('add-separator-btn');
const addCommentBtn = document.getElementById('add-comment-btn');
const deleteRowBtn = document.getElementById('delete-row-btn');
const exportBtn = document.getElementById('export-btn');
const importBtn = document.getElementById('import-btn');
const importFileInput = document.getElementById('import-file');
const tableStorageKey = `unit-table:${ns}`;
let currentRowIndex = null;

// === Инициализация StorageAPI с ключами ===
// Top-level initialization near StorageAPI.init
StorageAPI.init({
  ns,
  storageKey,
  tableStorageKey,
  nameEl,
  propsStorageKey: `unit-props:${ns}`,
  linksStorageKey: `unit-links:${ns}`,
  factionInfoStorageKey: `faction-info:${ns}`,
  backInfoStorageKey: `back-info:${ns}` // добавлено
});

// Запоминаем выбранную строку (для вставки разделителя «после» неёй)
// Выделение строки и удаление
function selectRow(tr) {
  if (!tbody) return;
  Array.from(tbody.rows).forEach(r => r.classList.remove('row-selected'));
  if (!tr) {
    currentRowIndex = null;
    return;
  }
  tr.classList.add('row-selected');
  currentRowIndex = Array.from(tbody.rows).indexOf(tr);
}

// Пересчёт вертикальных меток типа и их rowspan по группам (между разделителями)
function ensureTypeLabelCell(tr) {
  let labelCell = tr.querySelector('td.type-label');
  if (!labelCell) {
    labelCell = document.createElement('td');
    labelCell.className = 'type-label';
    labelCell.contentEditable = 'true';
    labelCell.spellcheck = false;
    labelCell.textContent = '';
    const firstTd = tr.querySelector('td:first-child');
    if (firstTd && firstTd.nextSibling) {
      tr.insertBefore(labelCell, firstTd.nextSibling);
    } else {
      tr.appendChild(labelCell);
    }
  }
  return labelCell;
}

function recalculateGroupLabels() {
  if (!tbody) return;
  const rows = Array.from(tbody.rows);
  let inGroup = false;

  for (let i = 0; i < rows.length; i++) {
    const tr = rows[i];
    if (tr.classList.contains('unit-separator') || tr.classList.contains('unit-comment')) {
      inGroup = false;
      continue;
    }
    if (!inGroup) {
      // старт новой группы
      inGroup = true;

      // найдём/создадим ячейку метки
      const labelCell = ensureTypeLabelCell(tr);

      // посчитать длину группы до ближайшего разделителя
      let length = 1;
      for (let j = i + 1; j < rows.length && !rows[j].classList.contains('unit-separator') && !rows[j].classList.contains('unit-comment'); j++) {
        length++;
      }
      labelCell.rowSpan = length;
    } else {
      // внутри группы — убедимся, что лишних меток нет
      const extra = tr.querySelector('td.type-label');
      if (extra) extra.remove();
    }
  }
}

function deleteRow(index = currentRowIndex) {
  if (!tbody) return;
  if (index == null || index < 0 || index >= tbody.rows.length) return;
  const tr = tbody.rows[index];

  // если удаляем первая строка группы — сохраним текст метки и перенесём на следующую
  const deletedLabelText = tr.querySelector('td.type-label')?.textContent.trim() || null;

  tr?.remove();
  currentRowIndex = null;

  // перенесём метку на новый старт группы, если есть следующий ряд и он не разделитель
  if (deletedLabelText) {
    const next = tbody.rows[index] || null;
    if (next && !next.classList.contains('unit-separator') && !next.classList.contains('unit-comment')) {
      const labelCell = ensureTypeLabelCell(next);
      labelCell.textContent = deletedLabelText;
    }
  }

  recalculateGroupLabels();
  saveTable();
}

// Навешиваем события выбора и удаления
if (tbody) {
  tbody.addEventListener('click', (e) => {
    const tr = e.target.closest('tr');
    if (!tr) return;
    selectRow(tr);
  });
}
deleteRowBtn?.addEventListener('click', () => deleteRow());

// объединённый обработчик клавиш Escape и Delete
document.addEventListener('keydown', (e) => {
  const active = document.activeElement;

  if (e.key === 'Escape') {
    clearSelection();
    return;
  }

  if (e.key === 'Delete') {
    // не перехватываем Delete при редактировании любых contenteditable/вводов
    if (active && (active.closest('[contenteditable="true"]') || active.tagName === 'INPUT' || active.tagName === 'TEXTAREA')) {
      return;
    }
    deleteRow();
  }
});

// === Работа с изображениями ===
function loadImageFile(file, imgEl) {
  if (!file || !file.type.startsWith('image/')) return;
  const reader = new FileReader();
  reader.onload = () => {
    imgEl.src = reader.result;
    imgEl.style.display = 'block';
    imgEl.alt = file.name.replace(/\.[^/.]+$/, '');
    saveTable();
  };
  reader.readAsDataURL(file);
}

function initDropzone(zone) {
  if (!zone || zone.dataset?.inited === '1') return;
  zone.dataset.inited = '1';

  const imgEl = zone.querySelector('.unit-image') || zone.querySelector('img');
  const fileInput = zone.querySelector('.unit-file');

  zone.addEventListener('click', () => fileInput && fileInput.click());

  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('dragover');
  });
  zone.addEventListener('dragleave', () => {
    zone.classList.remove('dragover');
  });
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) loadImageFile(file, imgEl);
  });

  // Вставка ссылки (https://... или data:image...)
  zone.addEventListener('paste', (e) => {
    const text = (e.clipboardData || window.clipboardData)?.getData('text');
    if (text && /^(https?:\/\/|data:image)/i.test(text)) {
      e.preventDefault();
      imgEl.src = text;
      imgEl.style.display = 'block';
      imgEl.alt = 'image';
      saveTable();
      markUnsaved();
    }
  });

  fileInput?.addEventListener('change', () => {
    const file = fileInput.files && fileInput.files[0];
    if (file) loadImageFile(file, imgEl);
  });
}

function buildUnitCell(captionText = 'untitled', imgSrc = '') {
  const td1 = document.createElement('td');

  const wrapper = document.createElement('div');
  wrapper.className = 'unit-icon';

  const zone = document.createElement('div');
  zone.className = 'unit-dropzone';

  const img = document.createElement('img');
  img.className = 'unit-image';
  img.alt = '';
  if (imgSrc) {
    img.src = imgSrc;
  }

  const fileInput = document.createElement('input');
  fileInput.type = 'file';
  fileInput.accept = 'image/*';
  fileInput.className = 'unit-file';
  fileInput.hidden = true;

  zone.appendChild(img);
  zone.appendChild(fileInput);

  const caption = document.createElement('div');
  caption.className = 'unit-caption';
  caption.textContent = (captionText && captionText.trim()) ? captionText : 'untitled';
  caption.contentEditable = 'true';
  caption.spellcheck = false;
  // стабильный id для связи
  caption.dataset.unitId = caption.dataset.unitId || genId();

  wrapper.appendChild(zone);
  wrapper.appendChild(caption);
  td1.appendChild(wrapper);

  initDropzone(zone);
  return td1;
}

// упрощённая инициализация дропзон в первой колонке
function initAllFirstCells() {
  if (!tbody) return;
  tbody.querySelectorAll('tr:not(.unit-separator):not(.unit-comment) td:first-child').forEach(ensureDropzone);
}

// === Разделители ===
function createSeparatorRow() {
  const tr = document.createElement('tr');
  tr.className = 'unit-separator';
  const td = document.createElement('td');
  td.colSpan = 5;
  td.innerHTML = '<div class="separator-line"></div>';
  tr.appendChild(td);
  return tr;
}

function addSeparator(afterIndex = null) {
  if (!tbody) return;
  const tr = createSeparatorRow();
  if (afterIndex !== null && afterIndex >= 0 && afterIndex < tbody.rows.length) {
    const ref = tbody.rows[afterIndex];
    ref?.parentNode.insertBefore(tr, ref.nextSibling);
  } else {
    tbody.appendChild(tr);
  }
  recalculateGroupLabels();
  saveTable();
}

function createCommentRow(text = 'Комментарий…') {
  const tr = document.createElement('tr');
  tr.className = 'unit-comment';
  const td = document.createElement('td');
  td.colSpan = 5;
  td.className = 'comment-cell';
  td.contentEditable = 'true';
  td.spellcheck = false;
  td.textContent = text;
  tr.appendChild(td);
  return tr;
}

function addComment(afterIndex = null) {
  if (!tbody) return;
  const tr = createCommentRow();
  if (afterIndex !== null && afterIndex >= 0 && afterIndex < tbody.rows.length) {
    const ref = tbody.rows[afterIndex];
    ref?.parentNode.insertBefore(tr, ref.nextSibling);
  } else {
    tbody.appendChild(tr);
  }
  recalculateGroupLabels();
  saveTable();
}

// === Задник: загрузка иллюстрации и сохранение текста ===
const backPage = document.querySelector('.page-back');
const backPanel = backPage?.querySelector('.back-content');

function initBackImage() {
  if (!backPage) return;
  const dz = backPage.querySelector('.back-dropzone');
  const fileInput = backPage.querySelector('.back-file');
  const img = backPage.querySelector('.back-image');
  if (!dz || !fileInput || !img) return;

  function loadBackImageFile(file) {
    const reader = new FileReader();
    reader.onload = () => {
      img.src = reader.result;
      StorageAPI?.saveBackInfoNowFrom?.(backPanel);
      markUnsaved();
    };
    reader.readAsDataURL(file);
  }

  dz.addEventListener('click', () => fileInput.click());
  dz.addEventListener('dragover', (e) => { e.preventDefault(); dz.classList.add('dragover'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', (e) => {
    e.preventDefault();
    dz.classList.remove('dragover');
    const file = e.dataTransfer?.files?.[0];
    if (file) loadBackImageFile(file);
  });
  fileInput.addEventListener('change', () => {
    const file = fileInput.files?.[0];
    if (file) loadBackImageFile(file);
  });
}
initBackImage();

// дебаунс сохранения задника при вводе
const saveBackInfo = backPanel ? StorageAPI?.makeSaveBackInfoDebounced?.(backPanel) : null;
backPanel?.addEventListener('input', (e) => {
  if (e.target.closest('.back-desc') || e.target.closest('.back-guide-title') || e.target.closest('.back-guide-text')) {
    saveBackInfo?.();
    markUnsaved();
  }
});

// восстановление задника при старте
StorageAPI?.restoreBackInfoInto?.(backPanel);

// === Слушатели ===
if (tbody) {
  tbody.addEventListener('input', (e) => {
    if (
      e.target.matches('td[contenteditable="true"]') ||
      e.target.matches('.unit-caption[contenteditable="true"]')
    ) {
      saveTable();
      markUnsaved(); // Добавлено: любые изменения в таблице считаем несохранёнными
    }
  });
}

// упрощённое добавление строки (использует createDataRow)
addRowBtn?.addEventListener('click', () => {
  if (!tbody) return;
  const tr = createDataRow();
  tbody.appendChild(tr);
  recalculateGroupLabels();
  saveTable();
});

addSepBtn?.addEventListener('click', () => addSeparator(currentRowIndex));
addCommentBtn?.addEventListener('click', () => addComment(currentRowIndex));

// Initialization block
// === Инициализация ===
StorageAPI.restoreTableInto(tbody, renderTable);
recalculateGroupLabels();
initAllFirstCells();
// синхронизируем id и перерисовываем связи при старте
window.UnitLinks?.ensureUnitIds?.();
window.UnitLinks?.updateAll?.();

// Снятие выделения по клику ВНЕ таблицы и ВНЕ панели (capture для надёжности)
document.addEventListener('click', (e) => {
  const insideTable = e.target.closest('.unit-table');
  const insideToolbar = e.target.closest('.toolbar');
  const insideProps = e.target.closest('.unit-props-panel');
  if (insideTable || insideToolbar || insideProps) return;
  clearSelection();
}, { capture: true });

// Снятие выделения при клике вне таблицы и вне панели
function clearSelection() {
  document.querySelectorAll('.unit-table tr.row-selected').forEach(r => r.classList.remove('row-selected'));
  document.querySelectorAll('.unit-prop.prop-selected').forEach(p => p.classList.remove('prop-selected'));
  currentRowIndex = null;
}

// экспорт/импорт JSON с заголовком фракции
function exportTable() {
  StorageAPI.saveTableNowFrom(tbody); // гарантируем сохранение таблицы
  StorageAPI.saveFactionInfoNowFrom(factionInfoPanel); // сохраняем подготовку
  StorageAPI?.saveBackInfoNowFrom?.(backPanel);        // сохраняем задник
  StorageAPI.exportTable();
  markExported(); // экспорт выполнен — не тревожим при закрытии вкладки
}

function renderBackInfo(info = {}) {
  if (!backPanel) return;
  const descEl = backPanel.querySelector('.back-desc');
  const titleEl = backPanel.querySelector('.back-guide-title');
  const textEl = backPanel.querySelector('.back-guide-text');
  const imgEl = backPanel.querySelector('.back-image');
  if (descEl) descEl.innerHTML = info.desc ?? '';
  if (titleEl) titleEl.textContent = info.guideTitle ?? 'Как играть за данную фракцию';
  if (textEl) textEl.innerHTML = info.guideText ?? '';
  if (imgEl && info.imgSrc) imgEl.src = info.imgSrc;
}

// импорт: добавляем рендер задника как доп. аргумент
// Import wiring — keep the listener that provides all renderers
importFileInput?.addEventListener('change', () => StorageAPI.importTableFromFile(
  importFileInput.files?.[0],
  (rows) => { renderTable(rows); },
  window.UnitProps?.renderProps,
  window.UnitLinks?.renderLinks,
  renderFactionInfo,
  renderBackInfo
));

// подключение обработчиков экспорта/импорта
exportBtn?.addEventListener('click', exportTable);
importBtn?.addEventListener('click', () => importFileInput?.click());


// единый рендер таблицы по массиву rows
function renderTable(rows) {
  if (!tbody) return;
  // ... existing code ...
  if (!tbody) return;
  // добавляем контроль начала группы
  let inGroup = false;

  tbody.innerHTML = '';
  rows.forEach((r, i) => {
    if (r && r.type === 'separator') {
      tbody.appendChild(createSeparatorRow());
      // новая группа начнётся после разделителя
      inGroup = false;
      return;
    }
    if (r && r.type === 'comment') {
      tbody.appendChild(createCommentRow(r.text || ''));
      inGroup = false;
      return;
    }
    const tr = document.createElement('tr');
    tr.className = 'unit-data';

    const td1 = buildUnitCell(r?.caption, r?.imgSrc);
    tr.appendChild(td1);

    // если id юнита есть — назначим его для подписи
    const captionEl = td1.querySelector('.unit-caption');
    if (captionEl) {
      captionEl.dataset.unitId = r?.unitId || captionEl.dataset.unitId || genId();
      if (r && r.caption) captionEl.textContent = r.caption;
    }
    for (let k = 0; k < 3; k++) {
      const td = document.createElement('td');
      td.contentEditable = 'true';
      td.classList.add('unit-stat'); // числовая ячейка — стабильный шрифт
      td.textContent = (r && r.cells && r.cells[k]) ? r.cells[k] : '';
      tr.appendChild(td);
    }

    // восстановление вертикальной метки типа из сохранённых данных
    if (!inGroup) {
      const labelCell = ensureTypeLabelCell(tr);
      labelCell.textContent = (r && r.groupLabel) ? r.groupLabel : '';
      inGroup = true;
    }

    tbody.appendChild(tr);

    const imgEl = td1.querySelector('.unit-image');
    if (imgEl && r && r.imgSrc) imgEl.src = r.imgSrc;
  });

  initAllFirstCells();
  recalculateGroupLabels();
  // актуализируем id и перерисуем связи
  window.UnitLinks?.ensureUnitIds?.();
  window.UnitLinks?.updateAll?.();
}

// helper: создание строки-данных с дропзон в первой колонке
function createDataRow(cells = ['', '', ''], imgSrc = '') {
  const tr = document.createElement('tr');
  tr.className = 'unit-data';

  const td1 = buildUnitCell('untitled', imgSrc);
  tr.appendChild(td1);

  for (let i = 0; i < 3; i++) {
    const td = document.createElement('td');
    td.contentEditable = 'true';
    td.className = 'unit-stat'; // числовая ячейка — стабильный шрифт
    td.textContent = cells && cells[i] ? cells[i] : '';
    tr.appendChild(td);
  }

  return tr;
}

function ensureBossSingleAndLast() {
  if (!tbody) return;

  // Удаляем дубль босса из tfoot (если когда-то добавлялся)
  const tfootBoss = document.querySelector('.unit-table tfoot .boss-row');
  if (tfootBoss) {
    const tfoot = document.querySelector('.unit-table tfoot');
    tfootBoss.remove();
    if (tfoot && !tfoot.querySelector('tr')) tfoot.remove();
  }

  // Если вдруг несколько .boss-row в tbody — оставляем один (последний), остальные удаляем
  const bosses = Array.from(tbody.querySelectorAll('tr.boss-row'));
  if (bosses.length > 1) {
    bosses.slice(0, -1).forEach(b => b.remove());
  }

  const bossRow = tbody.querySelector('tr.boss-row') || bosses[bosses.length - 1] || null;
  if (bossRow && bossRow !== tbody.lastElementChild) {
    tbody.appendChild(bossRow);
  }

  recalculateGroupLabels();
}

function ensureDropzone(cell) {
  if (!cell) return;

  // Если структура уже есть — просто удостоверимся, что всё инициализировано
  const dropzone = cell.querySelector('.unit-dropzone');
  const captionEl = cell.querySelector('.unit-caption');
  if (dropzone && captionEl) {
    captionEl.contentEditable = 'true';
    captionEl.spellcheck = false;
    if (!captionEl.textContent.trim()) {
      captionEl.textContent = 'untitled';
    }
    // стабильный id для подписи
    if (!captionEl.dataset.unitId) {
      captionEl.dataset.unitId = genId();
    }
    initDropzone(dropzone);
    return;
  }

  // Иначе перестроим ячейку на стандартную разметку, сохранив имеющиеся данные
  const existingCaption =
    (captionEl && captionEl.textContent) ||
    cell.textContent.trim() ||
    'untitled';
  const existingImgSrc =
    cell.querySelector('.unit-image')?.src ||
    cell.querySelector('img')?.src ||
    '';

  cell.innerHTML = '';
  const tdBuilt = buildUnitCell(existingCaption, existingImgSrc);
  // Переносим содержимое из временного td в текущую ячейку
  while (tdBuilt.firstChild) {
    cell.appendChild(tdBuilt.firstChild);
  }
}
// Генератор уникальных ID (объявлён как function, не попадает в TDZ)
function genId() {
  return crypto?.randomUUID?.() || ('uid-' + Math.random().toString(36).slice(2));
}

// Панель подготовки фракции: сохранение/восстановление
const factionInfoPanel = document.querySelector('.faction-info-panel');
const DEFAULT_ROBOT_TITLE = 'Создание боевого робота';
const DEFAULT_ROBOT_STEPS_HTML = `
  <li>В стартовом регионе Островной Империи должна быть фабрика (может быть свободной или контролироваться врагом).</li>
  <li>Заплатите 10 нефти, или 4 если создаете не первый раз.</li>
  <li>“Краб” появляется в стартовом регионе фракции.</li>
`;

function normalizeRobotPanelsInfo(info = {}) {
  const list = Array.isArray(info?.robotPanels) ? info.robotPanels : null;
  if (list && list.length) {
    return list
      .filter((item) => item && typeof item === 'object')
      .map((item) => ({
        title: typeof item.title === 'string' ? item.title : '',
        stepsHtml: typeof item.stepsHtml === 'string'
          ? item.stepsHtml
          : (typeof item.steps === 'string' ? item.steps : '')
      }));
  }
  return [{
    title: typeof info?.robotTitle === 'string' ? info.robotTitle : DEFAULT_ROBOT_TITLE,
    stepsHtml: typeof info?.robotSteps === 'string' ? info.robotSteps : DEFAULT_ROBOT_STEPS_HTML
  }];
}

function createRobotPanelElement(title = '', stepsHtml = '') {
  const panel = document.createElement('div');
  panel.className = 'robot-panel';

  const header = document.createElement('div');
  header.className = 'robot-header';

  const titleEl = document.createElement('div');
  titleEl.className = 'prep-title robot-title';
  titleEl.contentEditable = 'true';
  titleEl.spellcheck = false;
  titleEl.textContent = title;

  const removeBtn = document.createElement('button');
  removeBtn.type = 'button';
  removeBtn.className = 'robot-remove-btn';
  removeBtn.setAttribute('aria-label', 'Удалить панель робота');
  removeBtn.textContent = '×';

  const stepsEl = document.createElement('ol');
  stepsEl.className = 'robot-steps';
  stepsEl.contentEditable = 'true';
  stepsEl.spellcheck = false;
  stepsEl.innerHTML = stepsHtml;

  header.appendChild(titleEl);
  header.appendChild(removeBtn);
  panel.appendChild(header);
  panel.appendChild(stepsEl);

  sanitizeRobotSteps(stepsEl);
  ensureRobotStepsNotEmpty(stepsEl);
  return panel;
}

function updateRobotRemoveButtonsState() {
  const panels = factionInfoPanel ? Array.from(factionInfoPanel.querySelectorAll('.robot-panels .robot-panel')) : [];
  const single = panels.length <= 1;
  panels.forEach((panel) => {
    const btn = panel.querySelector('.robot-remove-btn');
    if (!btn) return;
    btn.disabled = single;
    btn.style.visibility = single ? 'hidden' : 'visible';
  });
}

function renderRobotPanels(info = {}) {
  if (!factionInfoPanel) return;
  const container = factionInfoPanel.querySelector('.robot-panels');
  if (!container) return;
  const normalized = normalizeRobotPanelsInfo(info);
  container.innerHTML = '';
  normalized.forEach((item) => {
    const title = typeof item.title === 'string' ? item.title : '';
    const stepsHtml = typeof item.stepsHtml === 'string' ? item.stepsHtml : DEFAULT_ROBOT_STEPS_HTML;
    container.appendChild(createRobotPanelElement(title, stepsHtml));
  });
  if (!container.querySelector('.robot-panel')) {
    container.appendChild(createRobotPanelElement(DEFAULT_ROBOT_TITLE, DEFAULT_ROBOT_STEPS_HTML));
  }
  updateRobotRemoveButtonsState();
}

function renderFactionInfo(info = {}) {
  if (!factionInfoPanel) return;
  const qEl = factionInfoPanel.querySelector('.prep-value[data-key="queue"]');
  const oEl = factionInfoPanel.querySelector('.prep-value[data-key="oil"]');
  const rEl = factionInfoPanel.querySelector('.prep-value[data-key="region"]');
  const nEl = factionInfoPanel.querySelector('.prep-notes[data-key="notes"]');
  if (qEl) qEl.textContent = (info.queue ?? '0');
  if (oEl) oEl.textContent = (info.oil ?? '8');
  if (rEl) rEl.textContent = (info.region ?? '');
  if (nEl) nEl.innerHTML = (info.notes ?? '');
  renderRobotPanels(info);
  const logoImg = document.querySelector('.faction-logo .faction-logo-image');
  if (logoImg && info.logoSrc) logoImg.src = info.logoSrc;
}

const saveFactionInfo = factionInfoPanel ? StorageAPI.makeSaveFactionInfoDebounced(factionInfoPanel) : null;
updateRobotRemoveButtonsState();

function addRobotPanel() {
  if (!factionInfoPanel) return;
  const container = factionInfoPanel.querySelector('.robot-panels');
  if (!container) return;
  container.appendChild(createRobotPanelElement(DEFAULT_ROBOT_TITLE, DEFAULT_ROBOT_STEPS_HTML));
  updateRobotRemoveButtonsState();
  saveFactionInfo?.();
  markUnsaved();
}

function removeRobotPanel(panel) {
  if (!factionInfoPanel || !panel) return;
  const container = factionInfoPanel.querySelector('.robot-panels');
  if (!container) return;
  const allPanels = Array.from(container.querySelectorAll('.robot-panel'));
  if (allPanels.length <= 1) return;
  panel.remove();
  updateRobotRemoveButtonsState();
  saveFactionInfo?.();
  markUnsaved();
}

factionInfoPanel?.addEventListener('click', (e) => {
  const target = e.target instanceof Element ? e.target : null;
  if (!target) return;
  if (target.closest('.robot-add-btn')) {
    addRobotPanel();
    return;
  }
  const removeBtn = target.closest('.robot-remove-btn');
  if (!removeBtn) return;
  removeRobotPanel(removeBtn.closest('.robot-panel'));
});

factionInfoPanel?.addEventListener('paste', (e) => {
  const target = e.target instanceof Element ? e.target : null;
  const robotOl = target?.closest('.robot-steps');
  if (!robotOl) return;
  const cd = e.clipboardData;
  if (!cd) return;
  const text = cd.getData('text/plain') || '';
  const html = cd.getData('text/html') || '';
  e.preventDefault();
  const plain = text || (new DOMParser().parseFromString(html, 'text/html').body.textContent || '');
  const sel = window.getSelection();
  if (sel && sel.rangeCount) {
    sel.deleteFromDocument();
    sel.getRangeAt(0).insertNode(document.createTextNode(plain));
    sel.collapseToEnd();
  } else {
    document.execCommand('insertText', false, plain);
  }
  requestAnimationFrame(() => {
    sanitizeRobotSteps(robotOl);
    ensureRobotStepsNotEmpty(robotOl);
    saveFactionInfo?.();
    markUnsaved();
  });
});

factionInfoPanel?.addEventListener('input', (e) => {
  const target = e.target instanceof Element ? e.target : null;
  if (!target) return;
  if (!target.closest('.prep-value[contenteditable="true"], .prep-notes[contenteditable="true"], .robot-title[contenteditable="true"], .robot-steps[contenteditable="true"]')) return;
  const robotOl = target.closest('.robot-steps');
  if (robotOl) {
    sanitizeRobotSteps(robotOl);
    ensureRobotStepsNotEmpty(robotOl);
  }
  saveFactionInfo?.();
  markUnsaved();
});

// восстановление при старте
StorageAPI.restoreFactionInfoInto(factionInfoPanel, renderFactionInfo);

// Дебаунс сохранения таблицы — единая точка вызова
const saveTable = tbody ? StorageAPI.makeSaveTableDebounced(tbody) : () => {};
StorageAPI.init({
  ns,
  storageKey,
  tableStorageKey,
  nameEl,
  propsStorageKey: `unit-props:${ns}`,
  linksStorageKey: `unit-links:${ns}`,
  factionInfoStorageKey: `faction-info:${ns}`,
  backInfoStorageKey: `back-info:${ns}` // добавлено
});

// Всегда держим хотя бы один элемент списка
function ensureRobotStepsNotEmpty(ol) {
  if (!ol) return;
  if (!ol.querySelector('li')) {
    const li = document.createElement('li');
    li.textContent = '';
    ol.appendChild(li);
  }
}

// Санитизация содержимого списка: только li + простой текст
function sanitizeRobotSteps(ol) {
  if (!ol) return;
  Array.from(ol.childNodes).forEach((node) => {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = (node.nodeValue || '').trim();
      if (text) {
        const li = document.createElement('li');
        li.textContent = text;
        ol.replaceChild(li, node);
      } else {
        ol.removeChild(node);
      }
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node;
      if (el.tagName !== 'LI') {
        const li = document.createElement('li');
        li.textContent = el.textContent || '';
        ol.replaceChild(li, el);
      } else {
        const raw = el.textContent || '';
        const lines = raw.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
        if (lines.length <= 1) {
          el.textContent = lines[0] || '';
        } else {
          const frag = document.createDocumentFragment();
          lines.forEach((s) => {
            const li = document.createElement('li');
            li.textContent = s;
            frag.appendChild(li);
          });
          ol.insertBefore(frag, el);
          ol.removeChild(el);
        }
      }
    }
  });
  // Убираем возможные классы/стили
  Array.from(ol.querySelectorAll('li')).forEach((li) => {
    li.removeAttribute('style');
    li.removeAttribute('class');
  });
}
