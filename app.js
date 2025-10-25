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

// === Сохранение заголовка фракции ===
const storageKey = `faction-name:${ns}`;
const nameEl = document.querySelector('.faction-name');
const savedName = lsGet(storageKey);
if (nameEl && savedName) nameEl.textContent = savedName;
if (nameEl) {
  nameEl.addEventListener('input', () => {
    lsSet(storageKey, nameEl.textContent.trim());
  });
}

// === Таблица и панель ===
// Инициализация элементов панели
const table = document.querySelector('.unit-table');
const tbody = table?.querySelector('tbody');
const addRowBtn = document.getElementById('add-row-btn');
const addSepBtn = document.getElementById('add-separator-btn');
const deleteRowBtn = document.getElementById('delete-row-btn');
const exportBtn = document.getElementById('export-btn');
const importBtn = document.getElementById('import-btn');
const importFileInput = document.getElementById('import-file');
const tableStorageKey = `unit-table:${ns}`;
let currentRowIndex = null;

// Инициализация StorageAPI с ключами
StorageAPI.init({
  ns,
  storageKey,
  tableStorageKey,
  nameEl,
  propsStorageKey: `unit-props:${ns}` // <-- передаём ключ для свойств здесь
});

// Запоминаем выбранную строку (для вставки разделителя «после» неё)
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
    if (tr.classList.contains('unit-separator')) {
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
      for (let j = i + 1; j < rows.length && !rows[j].classList.contains('unit-separator'); j++) {
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
    if (next && !next.classList.contains('unit-separator')) {
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

  wrapper.appendChild(zone);
  wrapper.appendChild(caption);
  td1.appendChild(wrapper);

  initDropzone(zone);
  return td1;
}

// упрощённая инициализация дропзон в первой колонке
function initAllFirstCells() {
  if (!tbody) return;
  tbody.querySelectorAll('tr:not(.unit-separator) td:first-child').forEach(ensureDropzone);
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

// === Сохранение/восстановление таблицы ===
function saveTableNow() {
  StorageAPI.saveTableNowFrom(tbody);
}
const saveTable = StorageAPI.makeSaveTableDebounced(tbody);

function restoreTable() {
  StorageAPI.restoreTableInto(tbody, renderTable);
}

// === Слушатели ===
if (tbody) {
  tbody.addEventListener('input', (e) => {
    if (
      e.target.matches('td[contenteditable="true"]') ||
      e.target.matches('.unit-caption[contenteditable="true"]')
    ) {
      saveTable();
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

// === Инициализация ===
restoreTable();
recalculateGroupLabels();
initAllFirstCells();

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
  saveTableNow(); // гарантируем сохранение
  StorageAPI.exportTable();
}

function importTableFromFile(file) {
  StorageAPI.importTableFromFile(file, (rows) => {
    renderTable(rows);
  }, window.UnitProps?.renderProps);
}

// подключение обработчиков экспорта/импорта
exportBtn?.addEventListener('click', exportTable);
importBtn?.addEventListener('click', () => importFileInput?.click());
importFileInput?.addEventListener('change', () => importTableFromFile(importFileInput.files?.[0]));

// единый рендер таблицы по массиву rows
function renderTable(rows) {
  if (!tbody) return;
  tbody.innerHTML = '';
  rows.forEach((r, i) => {
    if (r && r.type === 'separator') {
      tbody.appendChild(createSeparatorRow());
      return;
    }
    const tr = document.createElement('tr');

    const td1 = buildUnitCell(r?.caption, r?.imgSrc);
    tr.appendChild(td1);

    // если это первая строка группы — добавим вертикальную метку типа
    const groupStart = (i === 0 || rows[i - 1]?.type === 'separator');
    if (groupStart) {
      let length = 1;
      for (let j = i + 1; j < rows.length && rows[j]?.type !== 'separator'; j++) {
        length++;
      }
      const tdLabel = document.createElement('td');
      tdLabel.className = 'type-label';
      tdLabel.rowSpan = length;
      tdLabel.contentEditable = 'true';
      tdLabel.spellcheck = false;
      tdLabel.textContent = r?.groupLabel || '';
      tr.appendChild(tdLabel);
    }

    for (let k = 0; k < 3; k++) {
      const td = document.createElement('td');
      td.contentEditable = 'true';
      td.classList.add('unit-stat'); // числовая ячейка — стабильный шрифт
      td.textContent = (r && r.cells && r.cells[k]) ? r.cells[k] : '';
      tr.appendChild(td);
    }

    tbody.appendChild(tr);

    const imgEl = td1.querySelector('.unit-image');
    if (imgEl && r && r.imgSrc) imgEl.src = r.imgSrc;

    const captionEl = td1.querySelector('.unit-caption');
    if (captionEl && r && r.caption) captionEl.textContent = r.caption;
  });

  initAllFirstCells();
  recalculateGroupLabels();
}

// helper: создание строки-данных с дропзон в первой колонке
function createDataRow(cells = ['', '', ''], imgSrc = '') {
  const tr = document.createElement('tr');

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