(function () {
  const panelEl = document.querySelector('.unit-props-panel');
  const addBtn = document.getElementById('add-prop-btn');
  const deleteBtn = document.getElementById('delete-prop-btn');
  if (!panelEl) return;

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

  // Инициализация одного блока свойства: выбор, ввод, drag
  function hydratePropItem(propEl) {
    if (!propEl || propEl.dataset?.inited === '1') return;
    propEl.dataset.inited = '1';

    // фиксация контекста позиционирования для хэндла
    propEl.style.position = 'relative';

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
  function createProp({ title = 'Новое свойство', note = 'Кратко', desc = 'Полное описание…' } = {}) {
    const box = document.createElement('div');
    box.className = 'unit-prop';
    box.style.position = 'relative';

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

  // Drag & drop: свободное вертикальное движение внутри панели
  let dragging = null;
  let startOffsetY = 0;
  let placeholder = null;

  function startDrag(e, el) {
    // блокируем drag, если не выбран
    if (!el.classList.contains('prop-selected')) return;

    e.preventDefault();
    dragging = el;
    document.body.classList.add('dragging-props');

    const rect = el.getBoundingClientRect();
    const panelRect = panelEl.getBoundingClientRect();
    startOffsetY = e.clientY - rect.top;

    placeholder = document.createElement('div');
    placeholder.className = 'prop-placeholder';
    placeholder.style.height = rect.height + 'px';
    panelEl.insertBefore(placeholder, el.nextSibling);

    el.classList.add('dragging');
    el.style.willChange = 'transform';

    el.setPointerCapture && el.setPointerCapture(e.pointerId);
    document.addEventListener('pointermove', onDragMove);
    document.addEventListener('pointerup', endDrag);
  }

  function onDragMove(e) {
    if (!dragging) return;

    const panelRect = panelEl.getBoundingClientRect();

    // Автопрокрутка панели у краёв
    if (e.clientY < panelRect.top + 24) {
      panelEl.scrollTop -= 12;
    } else if (e.clientY > panelRect.bottom - 24) {
      panelEl.scrollTop += 12;
    }

    // Текущая позиция указателя относительно панели (учитывая scroll)
    const panelY = e.clientY - panelRect.top + panelEl.scrollTop;

    // Исходная позиция dragged относительно панели
    const elTopPanel = dragging.offsetTop;
    const translateY = panelY - startOffsetY - elTopPanel;
    dragging.style.transform = `translateY(${translateY}px)`;

    // Перестановка плейсхолдера по центрам соседей
    const props = Array.from(panelEl.querySelectorAll('.unit-prop')).filter(p => p !== dragging);
    const yCenter = panelY - startOffsetY + (dragging.offsetHeight / 2);

    let targetIndex = props.length;
    for (let i = 0; i < props.length; i++) {
      const p = props[i];
      const mid = p.offsetTop + p.offsetHeight / 2;
      if (yCenter < mid) {
        targetIndex = i;
        break;
      }
    }

    const ref = props[targetIndex] || null;
    if (ref) {
      panelEl.insertBefore(placeholder, ref);
    } else {
      panelEl.appendChild(placeholder);
    }
  }

  function endDrag(e) {
    if (!dragging) return;

    // Закрепляем блок на месте плейсхолдера
    dragging.classList.remove('dragging');
    dragging.style.transform = '';
    dragging.style.willChange = '';
    if (placeholder) {
      panelEl.insertBefore(dragging, placeholder);
      placeholder.remove();
      placeholder = null;
    }

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
  Array.from(panelEl.querySelectorAll('.unit-prop')).forEach(hydratePropItem);
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
      const el = createProp(p);
      panelEl.appendChild(el);
    });
    updateHandlesVisibility();
  }
  window.UnitProps = { renderProps, addProp, deleteSelectedProp };

  // Восстановление из localStorage: прямо передаём renderProps
  StorageAPI.restorePropsInto(panelEl, renderProps);
})();