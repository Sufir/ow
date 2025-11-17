(function () {
  const pageEl = document.querySelector('.page');
  const panelEl = document.querySelector('.unit-props-panel');
  const tableEl = document.querySelector('.unit-table');
  if (!pageEl || !panelEl || !tableEl) return;

  // берём или создаём оверлей
  let svg = document.getElementById('link-overlay');
  if (!svg) {
    svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.id = 'link-overlay';
    svg.classList.add('link-overlay');
    pageEl.appendChild(svg);
  }

  function resizeOverlay() {
    const w = pageEl.clientWidth;
    const h = pageEl.clientHeight;
    svg.setAttribute('width', w);
    svg.setAttribute('height', h);
    svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
  }
  resizeOverlay();

  // локальный генератор id
  const genId = () => (crypto?.randomUUID?.() || ('id-' + Math.random().toString(36).slice(2)));

  // держим список связей
  let links = [];
  let suppressPersist = false;

  function ensurePropIds() {
    panelEl.querySelectorAll('.unit-prop').forEach((el) => {
      if (!el.dataset.propId) el.dataset.propId = genId();
    });
  }
  function ensureUnitIds() {
    tableEl.querySelectorAll('.unit-caption').forEach((el) => {
      if (!el.dataset.unitId) el.dataset.unitId = genId();
    });
  }

  function getAnchors(propId, unitId) {
    const propEl = panelEl.querySelector(`.unit-prop[data-prop-id="${propId}"]`);
    const capEl  = tableEl.querySelector(`.unit-caption[data-unit-id="${unitId}"]`);
    if (!propEl || !capEl) return null;

    const pageRect = pageEl.getBoundingClientRect();
    const propRect = propEl.getBoundingClientRect();
    const capRect  = capEl.getBoundingClientRect();

    // начало: правый верхний угол unit-prop
    const x1 = propRect.right - pageRect.left;
    const y1 = propRect.top   - pageRect.top;
    // конец: левый край unit-caption (по вертикали — центр)
    const x2 = capRect.left - pageRect.left;
    const y2 = (capRect.top + capRect.height / 2) - pageRect.top;

    return { x1, y1, x2, y2 };
  }

  function updateAll() {
    resizeOverlay();
    const elbow = 6; // длина короткого горизонтального «заломного» участка у подписи
    links.forEach((ln) => {
      const anchors = getAnchors(ln.propId, ln.unitId);
      if (!anchors) return;
  
      // Прямой участок от unit-prop → точка у подписи, затем горизонтально в левый край подписи
      const points = `${anchors.x1},${anchors.y1} ${anchors.x2 - elbow},${anchors.y2} ${anchors.x2},${anchors.y2}`;
  
      if (ln.el.tagName.toLowerCase() === 'polyline') {
        ln.el.setAttribute('points', points);
      } else {
        // конвертация старых <line> → <polyline>
        const newEl = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
        newEl.setAttribute('points', points);
        newEl.setAttribute('fill', 'none');
        newEl.setAttribute('stroke', '#25a4ee');
        newEl.setAttribute('stroke-width', '1.5');
        newEl.setAttribute('shape-rendering', 'crispEdges');
        newEl.setAttribute('stroke-linecap', 'round');
        newEl.setAttribute('stroke-linejoin', 'round');
        svg.replaceChild(newEl, ln.el);
        ln.el = newEl;
      }
    });
  }

  function persist() {
    if (suppressPersist) return;
    const data = links.map(l => ({ propId: l.propId, unitId: l.unitId }));
    StorageAPI.setUnitLinks(data);
  }

  function createLink(propId, unitId) {
    const anchors = getAnchors(propId, unitId);
    if (!anchors) return;
  
    const elbow = 6; // длина «заломного» участка
    // Диагональ от prop → точка залома у подписи → горизонтальный вход под прямым углом
    const points = `${anchors.x1},${anchors.y1} ${anchors.x2 - elbow},${anchors.y2} ${anchors.x2},${anchors.y2}`;
  
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    line.setAttribute('points', points);
    line.setAttribute('fill', 'none');
    line.setAttribute('stroke', '#25a4ee');
    line.setAttribute('stroke-width', '1.5'); // толще на 50%
    line.setAttribute('shape-rendering', 'crispEdges');
    line.setAttribute('stroke-linecap', 'round');
    line.setAttribute('stroke-linejoin', 'round');
  
    svg.appendChild(line);
    links.push({ propId, unitId, el: line });
    persist();
  }

  // Режим создания связи: клик по свойству → клик по подписи
  let linkMode = false;
  let pendingPropId = null;

  const linkBtn = document.getElementById('link-mode-btn');
  function setLinkMode(on) {
    linkMode = !!on;
    pendingPropId = null;
    document.body.classList.toggle('link-mode', linkMode);
  }
  linkBtn?.addEventListener('click', () => setLinkMode(!linkMode));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && linkMode) setLinkMode(false);
  });

  panelEl.addEventListener('click', (e) => {
    if (!linkMode) return;
    const prop = e.target.closest('.unit-prop');
    if (!prop) return;
    ensurePropIds();
    pendingPropId = prop.dataset.propId;
  });
  tableEl.addEventListener('click', (e) => {
    if (!linkMode || !pendingPropId) return;
    const cap = e.target.closest('.unit-caption');
    if (!cap) return;
    ensureUnitIds();
    const unitId = cap.dataset.unitId;
    createLink(pendingPropId, unitId);
    setLinkMode(false);
    updateAll();
  });

  // Обновления при resize/scroll/drag
  window.addEventListener('resize', updateAll);
  panelEl.addEventListener('scroll', updateAll);

  let rafId = null;
  function tick() {
    updateAll();
    if (document.body.classList.contains('dragging-props')) {
      rafId = requestAnimationFrame(tick);
    } else {
      rafId = null;
    }
  }
  document.addEventListener('pointerdown', () => {
    if (document.body.classList.contains('dragging-props')) {
      if (!rafId) rafId = requestAnimationFrame(tick);
    }
  });
  document.addEventListener('pointerup', () => {
    updateAll();
  });

  // Восстановление связей
  function renderLinks(list = []) {
    svg.innerHTML = '';
    links = [];
    suppressPersist = true;
    ensurePropIds();
    ensureUnitIds();
    list.forEach((d) => d?.propId && d?.unitId && createLink(d.propId, d.unitId));
    suppressPersist = false;
    updateAll();
  }
  function restoreSaved() {
    const saved = StorageAPI.getUnitLinks();
    renderLinks(Array.isArray(saved) ? saved : []);
  }
  restoreSaved();

  window.UnitLinks = {
    updateAll,
    ensureUnitIds,
    renderLinks
  };
})();