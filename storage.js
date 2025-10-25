(function (global) {
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

  let cfg = {
    ns: 'default',
    storageKey: '',
    tableStorageKey: '',
    nameEl: null,
    propsStorageKey: '' // ключ для блоков свойств
  };

  function init({ ns, storageKey, tableStorageKey, nameEl, propsStorageKey }) {
    cfg.ns = ns;
    cfg.storageKey = storageKey;
    cfg.tableStorageKey = tableStorageKey;
    cfg.nameEl = nameEl;
    cfg.propsStorageKey = propsStorageKey || '';
  }

  function buildRowsFromTbody(tbody) {
    if (!tbody) return [];
    const rows = [];
    Array.from(tbody.rows).forEach((tr) => {
      if (tr.classList.contains('unit-separator')) {
        rows.push({ type: 'separator' });
        return;
      }
      const firstTd = tr.querySelector('td:first-child');
      const imgEl = firstTd?.querySelector('.unit-image');
      const imgSrc = imgEl?.src || '';
      const captionEl = firstTd?.querySelector('.unit-caption');
      const caption = captionEl?.textContent.trim() || '';

      const tdList = Array.from(tr.querySelectorAll('td'));
      const dataCells = tdList.slice(-3);
      const cells = dataCells.map((td) => td.textContent.trim());

      const obj = { type: 'data', imgSrc, caption, cells };

      const labelCell = tr.querySelector('td.type-label');
      if (labelCell) obj.groupLabel = labelCell.textContent.trim();

      rows.push(obj);
    });
    return rows;
  }

  function saveTableNowFrom(tbody) {
    const rows = buildRowsFromTbody(tbody);
    lsSet(cfg.tableStorageKey, JSON.stringify(rows));
  }
  function makeSaveTableDebounced(tbody) {
    return debounce(() => saveTableNowFrom(tbody), 150);
  }

  function restoreTableInto(tbody, renderTableFn) {
    const raw = lsGet(cfg.tableStorageKey);
    if (!raw) return;
    let rows;
    try {
      rows = JSON.parse(raw);
    } catch {
      return;
    }
    renderTableFn(rows);
  }

  function exportTable() {
    // Принудительно сохраним перед экспортом
    const raw = lsGet(cfg.tableStorageKey);
    if (!raw) return;
    let rows;
    try {
      rows = JSON.parse(raw);
    } catch {
      rows = [];
    }

    // читаем свойства, если есть
    let unitProps = [];
    try {
      const propsRaw = lsGet(cfg.propsStorageKey);
      unitProps = propsRaw ? JSON.parse(propsRaw) : [];
    } catch {
      unitProps = [];
    }

    const payload = {
      factionName: cfg.nameEl?.textContent.trim() || '',
      rows,
      unitProps
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `unit-table-${cfg.ns}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  function importTableFromFile(file, renderTableFn, renderPropsFn) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      let parsed;
      try {
        parsed = JSON.parse(reader.result);
      } catch {
        alert('Ошибка: некорректный JSON');
        return;
      }

      const rows = Array.isArray(parsed) ? parsed : parsed?.rows;
      if (!Array.isArray(rows)) {
        alert('Ошибка: ожидается массив строк таблицы');
        return;
      }

      lsSet(cfg.tableStorageKey, JSON.stringify(rows));

      const factionName = Array.isArray(parsed) ? null : parsed?.factionName || '';
      if (typeof factionName === 'string' && cfg.nameEl) {
        cfg.nameEl.textContent = factionName;
        lsSet(cfg.storageKey, factionName.trim());
      }

      // восстановление свойств, если присутствуют
      const unitProps = Array.isArray(parsed) ? [] : (Array.isArray(parsed?.unitProps) ? parsed.unitProps : []);
      if (cfg.propsStorageKey) {
        lsSet(cfg.propsStorageKey, JSON.stringify(unitProps));
      }
      if (typeof renderPropsFn === 'function') {
        renderPropsFn(unitProps);
      }

      renderTableFn(rows);
    };
    reader.readAsText(file);
  }

  // Работа с блоками свойств
  function buildPropsFromPanel(panelEl) {
    if (!panelEl) return [];
    return Array.from(panelEl.querySelectorAll('.unit-prop')).map((prop) => {
      const title = prop.querySelector('.prop-title')?.textContent?.trim() || '';
      const note  = prop.querySelector('.prop-note')?.textContent?.trim() || '';
      const desc  = prop.querySelector('.prop-desc')?.textContent || ''; // сохраняем переносы
      const yStr = prop.style.top || '';
      const y = yStr.endsWith('px') ? parseFloat(yStr) : (prop.offsetTop || 0);
      return { title, note, desc, y };
    });
  }

  function savePropsNowFrom(panelEl) {
    const props = buildPropsFromPanel(panelEl);
    if (cfg.propsStorageKey) {
      lsSet(cfg.propsStorageKey, JSON.stringify(props));
    }
  }

  function makeSavePropsDebounced(panelEl) {
    return debounce(() => savePropsNowFrom(panelEl), 150);
  }

  function restorePropsInto(panelEl, renderPropsFn) {
    if (!cfg.propsStorageKey) return;
    const raw = lsGet(cfg.propsStorageKey);
    if (!raw) return;
    let list;
    try {
      list = JSON.parse(raw);
    } catch {
      return;
    }
    if (typeof renderPropsFn === 'function') {
      renderPropsFn(list);
    }
  }

  global.StorageAPI = {
    init,
    saveTableNowFrom,
    makeSaveTableDebounced,
    restoreTableInto,
    exportTable,
    importTableFromFile,
    lsGet,
    lsSet,
    // свойства
    savePropsNowFrom,
    makeSavePropsDebounced,
    restorePropsInto,
  };
})(window);