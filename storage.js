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
    propsStorageKey: '', // ключ для блоков свойств
    linksStorageKey: '',  // ключ для связей свойство↔юнит
    factionInfoStorageKey: '', // ключ для подготовки фракции
    backInfoStorageKey: ''     // добавлено: ключ для задника
  };

  function init({ ns, storageKey, tableStorageKey, nameEl, propsStorageKey, linksStorageKey, factionInfoStorageKey, backInfoStorageKey }) {
    cfg.ns = ns;
    cfg.storageKey = storageKey;
    cfg.tableStorageKey = tableStorageKey;
    cfg.nameEl = nameEl;
    cfg.propsStorageKey = propsStorageKey || '';
    cfg.linksStorageKey = linksStorageKey || '';
    cfg.factionInfoStorageKey = factionInfoStorageKey || '';
    cfg.backInfoStorageKey = backInfoStorageKey || ''; // добавлено: задник
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
      const unitId = captionEl?.dataset?.unitId || '';

      const tdList = Array.from(tr.querySelectorAll('td'));
      const dataCells = tdList.slice(-3);
      const cells = dataCells.map((td) => td.textContent.trim());

      const obj = { type: 'data', imgSrc, caption, cells, unitId };

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

    // читаем связи
    let unitLinks = [];
    try {
      const linksRaw = lsGet(cfg.linksStorageKey);
      unitLinks = linksRaw ? JSON.parse(linksRaw) : [];
    } catch {
      unitLinks = [];
    }
    // читаем подготовку фракции
    let factionInfo = {};
    try {
      const infoRaw = lsGet(cfg.factionInfoStorageKey);
      factionInfo = infoRaw ? JSON.parse(infoRaw) : {};
    } catch {
      factionInfo = {};
    }

    // читаем задник
    let backInfo = {};
    try {
      const backRaw = lsGet(cfg.backInfoStorageKey);
      backInfo = backRaw ? JSON.parse(backRaw) : {};
    } catch {
      backInfo = {};
    }

    const payload = {
      factionName: cfg.nameEl?.textContent.trim() || '',
      rows,
      unitProps,
      unitLinks,
      factionInfo,
      backInfo
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

  function importTableFromFile(file, renderTableFn, renderPropsFn, renderLinksFn, renderFactionInfoFn, renderBackInfoFn) {
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

      // восстановление связей, если присутствуют
      const unitLinks = Array.isArray(parsed) ? [] : (Array.isArray(parsed?.unitLinks) ? parsed.unitLinks : []);
      if (cfg.linksStorageKey) {
        lsSet(cfg.linksStorageKey, JSON.stringify(unitLinks));
      }
      if (typeof renderLinksFn === 'function') {
        renderLinksFn(unitLinks);
      }

      // восстановление подготовки фракции
      const factionInfo = Array.isArray(parsed) ? {} : (parsed?.factionInfo && typeof parsed.factionInfo === 'object' ? parsed.factionInfo : {});
      if (cfg.factionInfoStorageKey) {
        lsSet(cfg.factionInfoStorageKey, JSON.stringify(factionInfo));
      }
      if (typeof renderFactionInfoFn === 'function') {
        renderFactionInfoFn(factionInfo);
      }

      // восстановление задника
      const backInfo = Array.isArray(parsed) ? {} : (parsed?.backInfo && typeof parsed.backInfo === 'object' ? parsed.backInfo : {});
      if (cfg.backInfoStorageKey) {
        lsSet(cfg.backInfoStorageKey, JSON.stringify(backInfo));
      }
      if (typeof renderBackInfoFn === 'function') {
        renderBackInfoFn(backInfo);
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
      const noteHTML  = prop.querySelector('.prop-note')?.innerHTML || '';
      const descHTML  = prop.querySelector('.prop-desc')?.innerHTML || ''; // сохраняем переносы и разметку
      const note = sanitizeNoFontSize(noteHTML);
      const desc = sanitizeNoFontSize(descHTML);
      const yStr = prop.style.top || '';
      const y = yStr.endsWith('px') ? parseFloat(yStr) : (prop.offsetTop || 0);
      const id = prop.dataset?.propId || '';
      return { id, title, note, desc, y };
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

  // Связи: геттер/сеттер
  function getUnitLinks() {
    if (!cfg.linksStorageKey) return [];
    const raw = lsGet(cfg.linksStorageKey);
    if (!raw) return [];
    try {
      const links = JSON.parse(raw);
      return Array.isArray(links) ? links : [];
    } catch {
      return [];
    }
  }
  function setUnitLinks(list) {
    if (!cfg.linksStorageKey) return;
    const safe = Array.isArray(list) ? list : [];
    lsSet(cfg.linksStorageKey, JSON.stringify(safe));
  }

  // Работа с блоком подготовки фракции
  function getRobotPanelsFromInfo(info = {}) {
    const list = Array.isArray(info?.robotPanels) ? info.robotPanels : null;
    if (list && list.length) {
      const normalized = list
        .filter((item) => item && typeof item === 'object')
        .map((item) => ({
          title: typeof item.title === 'string' ? item.title : '',
          stepsHtml: typeof item.stepsHtml === 'string'
            ? item.stepsHtml
            : (typeof item.steps === 'string' ? item.steps : '')
        }));
      if (normalized.length) return normalized;
    }
    return [{
      title: typeof info?.robotTitle === 'string' ? info.robotTitle : 'Создание боевого робота',
      stepsHtml: typeof info?.robotSteps === 'string'
        ? info.robotSteps
        : '<li>В стартовом регионе Островной Империи должна быть фабрика (может быть свободной или контролироваться врагом).</li><li>Заплатите 10 нефти, или 4 если создаете не первый раз.</li><li>“Краб” появляется в стартовом регионе фракции.</li>'
    }];
  }

  function buildFactionInfoFromPanel(panelEl) {
    if (!panelEl) return { queue: '', oil: '', region: '', notes: '', robotPanels: [], robotTitle: '', robotSteps: '', logoSrc: '' };
    const queue = panelEl.querySelector('.prep-value[data-key="queue"]')?.textContent?.trim() || '';
    const oil = panelEl.querySelector('.prep-value[data-key="oil"]')?.textContent?.trim() || '';
    const region = panelEl.querySelector('.prep-value[data-key="region"]')?.textContent?.trim() || '';
    const notes = panelEl.querySelector('.prep-notes[data-key="notes"]')?.innerHTML || '';
    const robotPanelsRaw = Array.from(panelEl.querySelectorAll('.robot-panels .robot-panel'));
    const robotPanels = (robotPanelsRaw.length ? robotPanelsRaw : Array.from(panelEl.querySelectorAll('.robot-panel')))
      .map((robotPanel) => {
        const title = robotPanel.querySelector('.robot-title')?.textContent?.trim() || '';
        const stepsHtml = robotPanel.querySelector('.robot-steps')?.innerHTML || '';
        return { title, stepsHtml };
      });
    if (!robotPanels.length) {
      robotPanels.push({ title: 'Создание боевого робота', stepsHtml: '' });
    }
    const robotTitle = robotPanels[0]?.title || '';
    const robotSteps = robotPanels[0]?.stepsHtml || '';
    const logoSrc = document.querySelector('.faction-logo .faction-logo-image')?.getAttribute('src') || '';
    return { queue, oil, region, notes, robotPanels, robotTitle, robotSteps, logoSrc };
  }

  function saveFactionInfoNowFrom(panelEl) {
    const info = buildFactionInfoFromPanel(panelEl);
    if (cfg.factionInfoStorageKey) {
      lsSet(cfg.factionInfoStorageKey, JSON.stringify(info));
    }
  }

  function makeSaveFactionInfoDebounced(panelEl) {
    return debounce(() => saveFactionInfoNowFrom(panelEl), 150);
  }

  function restoreFactionInfoInto(panelEl, renderFn) {
    if (!cfg.factionInfoStorageKey) return;
    const raw = lsGet(cfg.factionInfoStorageKey);
    if (!raw) return;
    let info;
    try {
      info = JSON.parse(raw);
    } catch {
      return;
    }
    if (typeof renderFn === 'function') {
      renderFn(info);
      return;
    }
    // дефолтное применение в DOM, если рендерер не задан
    const qEl = panelEl.querySelector('.prep-value[data-key="queue"]');
    const oEl = panelEl.querySelector('.prep-value[data-key="oil"]');
    const rEl = panelEl.querySelector('.prep-value[data-key="region"]');
    const nEl = panelEl.querySelector('.prep-notes[data-key="notes"]');
    if (qEl) qEl.textContent = info.queue ?? '0';
    if (oEl) oEl.textContent = info.oil ?? '8';
    if (rEl) rEl.textContent = info.region ?? '';
    if (nEl) nEl.innerHTML = info.notes ?? '';
    // добавлено: восстановление нового блока
    const robotPanelsContainer = panelEl.querySelector('.robot-panels');
    const robotPanels = getRobotPanelsFromInfo(info);
    if (robotPanelsContainer) {
      robotPanelsContainer.innerHTML = '';
      robotPanels.forEach((item) => {
        const robotPanel = document.createElement('div');
        robotPanel.className = 'robot-panel';

        const header = document.createElement('div');
        header.className = 'robot-header';

        const rtEl = document.createElement('div');
        rtEl.className = 'prep-title robot-title';
        rtEl.contentEditable = 'true';
        rtEl.spellcheck = false;
        rtEl.textContent = typeof item.title === 'string' ? item.title : '';

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'robot-remove-btn';
        removeBtn.setAttribute('aria-label', 'Удалить панель робота');
        removeBtn.textContent = '×';

        const rsEl = document.createElement('ol');
        rsEl.className = 'robot-steps';
        rsEl.contentEditable = 'true';
        rsEl.spellcheck = false;
        rsEl.innerHTML = typeof item.stepsHtml === 'string' ? item.stepsHtml : '';

        header.appendChild(rtEl);
        header.appendChild(removeBtn);
        robotPanel.appendChild(header);
        robotPanel.appendChild(rsEl);
        robotPanelsContainer.appendChild(robotPanel);
      });
      const allPanels = Array.from(robotPanelsContainer.querySelectorAll('.robot-panel'));
      const single = allPanels.length <= 1;
      allPanels.forEach((panel) => {
        const btn = panel.querySelector('.robot-remove-btn');
        if (!btn) return;
        btn.disabled = single;
        btn.style.visibility = single ? 'hidden' : 'visible';
      });
    } else {
      const rtEl = panelEl.querySelector('.robot-title');
      const rsEl = panelEl.querySelector('.robot-steps');
      const first = robotPanels[0] || { title: 'Создание боевого робота', stepsHtml: '' };
      if (rtEl) rtEl.textContent = first.title ?? 'Создание боевого робота';
      if (rsEl) rsEl.innerHTML = first.stepsHtml ?? '';
    }
    const logoImg = document.querySelector('.faction-logo .faction-logo-image');
    if (logoImg && info.logoSrc) logoImg.src = info.logoSrc;
  }

  // Работа с задником
  function buildBackInfoFromPanel(panelEl) {
    if (!panelEl) return { desc: '', guideTitle: 'Как играть за данную фракцию', guideText: '', imgSrc: '' };
    const descHTML = panelEl.querySelector('.back-desc')?.innerHTML || '';
    const guideTitle = panelEl.querySelector('.back-guide-title')?.textContent?.trim() || '';
    const guideTextHTML = panelEl.querySelector('.back-guide-text')?.innerHTML || '';
    const imgSrc = panelEl.querySelector('.back-image')?.getAttribute('src') || '';
    return {
      desc: sanitizeNoFontSize(descHTML),
      guideTitle,
      guideText: sanitizeNoFontSize(guideTextHTML),
      imgSrc
    };
  }
  
  function saveBackInfoNowFrom(panelEl) {
    const info = buildBackInfoFromPanel(panelEl);
    if (cfg.backInfoStorageKey) {
      lsSet(cfg.backInfoStorageKey, JSON.stringify(info));
    }
  }
  
  function makeSaveBackInfoDebounced(panelEl) {
    return debounce(() => saveBackInfoNowFrom(panelEl), 150);
  }
  
  function restoreBackInfoInto(panelEl) {
    if (!cfg.backInfoStorageKey) return;
    const raw = lsGet(cfg.backInfoStorageKey);
    if (!raw) return;
    let info;
    try {
      info = JSON.parse(raw);
    } catch {
      return;
    }
    const descEl = panelEl.querySelector('.back-desc');
    const titleEl = panelEl.querySelector('.back-guide-title');
    const textEl = panelEl.querySelector('.back-guide-text');
    const imgEl = panelEl.querySelector('.back-image');
    if (descEl) descEl.innerHTML = info.desc ?? '';
    if (titleEl) titleEl.textContent = info.guideTitle ?? 'Как играть за данную фракцию';
    if (textEl) textEl.innerHTML = info.guideText ?? '';
    if (imgEl && info.imgSrc) imgEl.src = info.imgSrc;
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
    // связи
    getUnitLinks,
    setUnitLinks,
    // подготовка
    saveFactionInfoNowFrom,
    makeSaveFactionInfoDebounced,
    restoreFactionInfoInto,
    // задник
    saveBackInfoNowFrom,
    makeSaveBackInfoDebounced,
    restoreBackInfoInto,
  };
})(window);


// Утилита: очищаем HTML от изменения размера шрифта
function sanitizeNoFontSize(html) {
    const wrapper = document.createElement('div');
    wrapper.innerHTML = html || '';
    wrapper.querySelectorAll('*').forEach((el) => {
        if (el.style && el.style.fontSize) el.style.fontSize = '';
        if (el.tagName === 'FONT') el.removeAttribute('size');
    });
    return wrapper.innerHTML;
}

(function(){
  const zone = document.querySelector('.faction-logo .faction-logo-dropzone');
  const input = document.querySelector('.faction-logo .faction-logo-file');
  const img = document.querySelector('.faction-logo .faction-logo-image');
  if (!zone || !input || !img) return;
  function loadLogoFile(file){
    if (!file || !file.type?.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = () => {
      img.src = reader.result;
      const panelEl = document.querySelector('.faction-info-panel');
      StorageAPI?.saveFactionInfoNowFrom?.(panelEl);
    };
    reader.readAsDataURL(file);
  }
  zone.addEventListener('click', () => input.click());
  zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer?.files?.[0];
    if (file) loadLogoFile(file);
  });
  zone.addEventListener('paste', (e) => {
    const text = (e.clipboardData || window.clipboardData)?.getData('text');
    if (text && /^(https?:\/\/|data:image)/i.test(text)) {
      e.preventDefault();
      img.src = text;
      const panelEl = document.querySelector('.faction-info-panel');
      StorageAPI?.saveFactionInfoNowFrom?.(panelEl);
    }
  });
  input.addEventListener('change', () => {
    const file = input.files?.[0];
    if (file) loadLogoFile(file);
  });
})();
