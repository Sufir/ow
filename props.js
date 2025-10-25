(function () {
  const panelEl = document.querySelector('.unit-props-panel');
  const addBtn = document.getElementById('add-prop-btn');
  const deleteBtn = document.getElementById('delete-prop-btn');
  if (!panelEl) return;

  // локальный генератор id для свойств
  const genId = () => (crypto?.randomUUID?.() || ('pid-' + Math.random().toString(36).slice(2)));

  // Дебаунс сохранения при вводе
  const saveDebounced = StorageAPI.makeSavePropsDebounced(panelEl);

  // Управление видимостью хэндлов: показываем только у выбранного блока
  function updateHandlesVisibility() {
    panelEl.querySelectorAll('.unit-prop').forEach((p) => {
      const h = p.querySelector('.prop-handle');
      if (!h) return;
      h.style.display = p.classList.contains('prop-selected') ? 'block' : 'none';
    });
  }

  // Вспомогательная: следующая координата Y (нижний край + небольшой зазор)
  function getNextY() {
    const props = Array.from(panelEl.querySelectorAll('.unit-prop'));
    if (props.length === 0) return 0;
    const bottoms = props
      .map(p => (parseFloat(p.style.top || '0') || p.offsetTop) + p.offsetHeight);
    const maxBottom = Math.max(...bottoms);
    return Math.max(0, Math.round(maxBottom + 8)); // зазор 8px
  }

  // Инициализируем контекст для абсолютного позиционирования блоков
  panelEl.style.position = 'relative';

  // Управление видимостью хэндлов: показываем только у выбранного блока
  function updateHandlesVisibility() {
    panelEl.querySelectorAll('.unit-prop').forEach((p) => {
      const h = p.querySelector('.prop-handle');
      if (!h) return;
      h.style.display = p.classList.contains('prop-selected') ? 'block' : 'none';
    });
  }

  // Вспомогательная: следующая координата Y (нижний край + небольшой зазор)
  function getNextY() {
    const props = Array.from(panelEl.querySelectorAll('.unit-prop'));
    if (props.length === 0) return 0;
    const bottoms = props
      .map(p => (parseFloat(p.style.top || '0') || p.offsetTop) + p.offsetHeight);
    const maxBottom = Math.max(...bottoms);
    return Math.max(0, Math.round(maxBottom + 8)); // зазор 8px
  }

  // Инициализация одного блока свойства: выбор, ввод, drag
  function hydratePropItem(propEl) {
    if (!propEl || propEl.dataset?.inited === '1') return;
    propEl.dataset.inited = '1';

    // присваиваем стабильный id, если не задан
    if (!propEl.dataset.propId) {
      propEl.dataset.propId = genId();
    }

    // измеряем текущую позицию в потоке и переводим блок в абсолют с тем же top
    const initialTop = propEl.offsetTop;
    propEl.style.position = 'absolute';
    propEl.style.left = '0';
    propEl.style.right = '0';
    if (!propEl.style.top) {
      propEl.style.top = `${initialTop}px`;
    }

    // Выбор блока по клику
    propEl.addEventListener('click', () => {
      panelEl.querySelectorAll('.unit-prop.prop-selected').forEach(p => p.classList.remove('prop-selected'));
      propEl.classList.add('prop-selected');
      updateHandlesVisibility();
    });

    // Сохранение при вводе текста в редактируемых полях
    propEl.addEventListener('input', (e) => {
      if (e.target.matches('.prop-title, .prop-note, .prop-desc')) {
        saveDebounced();
      }
    });

    // Drag & drop через хэндл, только если блок выбран
    const handle = propEl.querySelector('.prop-handle');
    if (handle) {
      handle.style.display = propEl.classList.contains('prop-selected') ? 'block' : 'none';
      handle.addEventListener('mousedown', (e) => e.preventDefault());
      handle.addEventListener('dragstart', (e) => e.preventDefault());
      handle.addEventListener('pointerdown', (e) => {
        if (!propEl.classList.contains('prop-selected')) return;
        startDrag(e, propEl);
      });
    }
  }

  // Создание нового блока свойства
  function createProp({ id, title = 'Новое свойство', note = 'Кратко', desc = 'Полное описание…', y } = {}) {
    const box = document.createElement('div');
    box.className = 'unit-prop';
    box.style.position = 'absolute';
    box.style.left = '0';
    box.style.right = '0';
    box.style.top = `${typeof y === 'number' ? Math.max(0, y) : 0}px`;
    // стабильный id для линков
    box.dataset.propId = id || genId();

    const handle = document.createElement('div');
    handle.className = 'prop-handle';
    handle.textContent = '⋮⋮';
    handle.style.display = 'none';

    const titleEl = document.createElement('div');
    titleEl.className = 'prop-title';
    titleEl.contentEditable = 'true';
    titleEl.spellcheck = false;
    titleEl.textContent = title || '';

    const noteEl = document.createElement('div');
    noteEl.className = 'prop-note';
    noteEl.contentEditable = 'true';
    noteEl.spellcheck = false;
    noteEl.textContent = note || '';

    const descEl = document.createElement('div');
    descEl.className = 'prop-desc';
    descEl.contentEditable = 'true';
    descEl.spellcheck = false;
    descEl.textContent = desc || '';

    box.appendChild(handle);
    box.appendChild(titleEl);
    box.appendChild(noteEl);
    box.appendChild(descEl);

    hydratePropItem(box);
    return box;
  }

  // Добавление свойства
  function addProp(initial) {
    const el = createProp(initial);
    panelEl.appendChild(el);
    const t = el.querySelector('.prop-title');
    t && t.focus();
    StorageAPI.savePropsNowFrom(panelEl);
    updateHandlesVisibility();
  }

  // Удаление выбранного (или последнего) и безусловное восстановление дефолтного, если стало пусто
  function deleteSelectedProp() {
    const selected = panelEl.querySelector('.unit-prop.prop-selected');
    const target = selected || panelEl.querySelector('.unit-prop:last-of-type');
    if (!target) return;
    target.remove();
    if (!panelEl.querySelector('.unit-prop')) {
      const el = createProp();
      panelEl.appendChild(el);
    }
    StorageAPI.savePropsNowFrom(panelEl);
    updateHandlesVisibility();
  }

  // Кнопки тулбара: прямой поиск, чтобы не зависеть от переменных
  document.getElementById('add-prop-btn')?.addEventListener('click', () => addProp());
  document.getElementById('delete-prop-btn')?.addEventListener('click', () => deleteSelectedProp());

  // Drag & drop: свободное вертикальное движение внутри панели по top
  let dragging = null;
  let startPointerY = 0;
  let dragStartTop = 0;
  let startScrollTop = 0;

  function startDrag(e, el) {
    if (!el.classList.contains('prop-selected')) return;

    e.preventDefault();
    dragging = el;
    document.body.classList.add('dragging-props');

    startPointerY = e.clientY;
    const topStr = getComputedStyle(el).top || el.style.top || '0px';
    dragStartTop = topStr.endsWith('px') ? parseFloat(topStr) : 0;
    startScrollTop = panelEl.scrollTop;

    el.classList.add('dragging');

    el.setPointerCapture && el.setPointerCapture(e.pointerId);
    document.addEventListener('pointermove', onDragMove);
    document.addEventListener('pointerup', endDrag);
  }

  function onDragMove(e) {
    if (!dragging) return;

    const panelRect = panelEl.getBoundingClientRect();

    // Автопрокрутка панели у краёв
    if (e.clientY < panelRect.top + 24) {
      panelEl.scrollTop = Math.max(0, panelEl.scrollTop - 12);
    } else if (e.clientY > panelRect.bottom - 24) {
      panelEl.scrollTop = panelEl.scrollTop + 12;
    }

    // Смещение указателя + учёт прокрутки панели
    const deltaY = (e.clientY - startPointerY) + (panelEl.scrollTop - startScrollTop);
    let newTop = dragStartTop + deltaY;

    // Кламп по всей высоте контента панели
    const minTop = 0;
    const maxTop = Math.max(0, panelEl.scrollHeight - dragging.offsetHeight);
    newTop = Math.min(Math.max(newTop, minTop), maxTop);

    dragging.style.top = `${Math.round(newTop)}px`;
  }

  function endDrag(e) {
    if (!dragging) return;

    dragging.classList.remove('dragging');

    dragging.releasePointerCapture && dragging.releasePointerCapture(e.pointerId);
    dragging = null;
    document.body.classList.remove('dragging-props');

    StorageAPI.savePropsNowFrom(panelEl);
  }

  // Сохранение при вводе на панели (защита, если добавляются новые элементы)
  panelEl.addEventListener('input', (e) => {
    if (e.target.matches('.prop-title, .prop-note, .prop-desc')) {
      saveDebounced();
    }
  });

  // Инициализация существующих блоков из шаблона + актуализация хэндлов
  Array.from(panelEl.querySelectorAll('.unit-prop')).forEach((el) => {
    hydratePropItem(el);
    if (!el.style.top) {
      el.style.top = getNextY() + 'px';
    }
  });
  updateHandlesVisibility();

  // Обновляем видимость хэндлов после глобального снятия выделений (клик вне)
  document.addEventListener('click', () => updateHandlesVisibility());

  // Единый рендер свойств: используется для восстановления и импорта
  function renderProps(list = []) {
    panelEl.innerHTML = '';
    if (!Array.isArray(list) || list.length === 0) {
      const el = createProp();
      panelEl.appendChild(el);
      updateHandlesVisibility();
      return;
    }
    list.forEach((p) => {
      const el = createProp(p); // p может содержать y и id
      panelEl.appendChild(el);
    });
    updateHandlesVisibility();
  }
  window.UnitProps = { renderProps, addProp, deleteSelectedProp };

  // Восстановление из localStorage: прямо передаём renderProps
  StorageAPI.restorePropsInto(panelEl, renderProps);
})();