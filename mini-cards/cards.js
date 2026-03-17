(function () {
  const COLS = 5;
  const ROWS = 4;
  const CARD_COUNT = COLS * ROWS;
  const DEFAULT_NUMBER = '3';
  const params = new URLSearchParams(window.location.search);
  const ns = params.get('id') || (location.pathname.split('/').pop() || '').replace(/\.html?$/i, '') || 'default';
  const storageKey = `mini-american-cards:${ns}`;

  const sheetsRoot = document.getElementById('sheetsRoot');
  const pairInfo = document.getElementById('pairInfo');
  const prevPairBtn = document.getElementById('prevPairBtn');
  const nextPairBtn = document.getElementById('nextPairBtn');
  const addPairBtn = document.getElementById('addPairBtn');
  const removePairBtn = document.getElementById('removePairBtn');
  const exportBtn = document.getElementById('exportBtn');
  const importBtn = document.getElementById('importBtn');
  const importInput = document.getElementById('importInput');
  const mirrorBacksInput = document.getElementById('mirrorBacksInput');
  const frontCardTemplate = document.getElementById('frontCardTemplate');
  const backCardTemplate = document.getElementById('backCardTemplate');

  const state = {
    currentPairIndex: 0,
    mirrorBacks: true,
    pairs: [createDefaultPair()]
  };

  function createDefaultPair() {
    return {
      frontTexts: Array.from({ length: CARD_COUNT }, () => DEFAULT_NUMBER)
    };
  }

  function safeLoad() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      const data = JSON.parse(raw);
      applyData(data);
    } catch (e) {
    }
  }

  function safeSaveNow() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(buildExportPayload()));
    } catch (e) {
    }
  }

  let saveTimer = null;
  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(safeSaveNow, 220);
  }

  function normalizePair(input) {
    const pair = input && typeof input === 'object' ? input : {};
    const frontTexts = Array.isArray(pair.frontTexts) ? pair.frontTexts.slice(0, CARD_COUNT) : [];
    while (frontTexts.length < CARD_COUNT) frontTexts.push(DEFAULT_NUMBER);
    return {
      frontTexts: frontTexts.map((v) => String(v ?? DEFAULT_NUMBER))
    };
  }

  function applyData(data) {
    if (!data || typeof data !== 'object') return;
    const srcPairs = Array.isArray(data.pairs) ? data.pairs : [];
    const normalized = srcPairs.map(normalizePair).filter(Boolean);
    state.pairs = normalized.length ? normalized : [createDefaultPair()];
    state.mirrorBacks = data.mirrorBacks !== false;
    const idx = Number.isInteger(data.currentPairIndex) ? data.currentPairIndex : 0;
    state.currentPairIndex = clampIndex(idx, state.pairs.length);
    renderAll();
  }

  function buildExportPayload() {
    return {
      type: 'mini-american-cards',
      version: 1,
      ns,
      currentPairIndex: state.currentPairIndex,
      cardsPerSheet: CARD_COUNT,
      cardSizeMm: { width: 41, height: 63 },
      mirrorBacks: state.mirrorBacks,
      pairs: state.pairs.map((p) => ({
        frontTexts: p.frontTexts.slice(0, CARD_COUNT)
      }))
    };
  }

  function clampIndex(index, total) {
    if (!total) return 0;
    if (index < 0) return 0;
    if (index > total - 1) return total - 1;
    return index;
  }

  function mapBackIndex(index) {
    if (!state.mirrorBacks) return index;
    const row = Math.floor(index / COLS);
    const col = index % COLS;
    return row * COLS + (COLS - 1 - col);
  }

  function appendCutMarks(grid) {
    const layer = document.createElement('div');
    layer.className = 'cut-marks';
    for (let y = 0; y <= ROWS; y += 1) {
      for (let x = 0; x <= COLS; x += 1) {
        const isLeft = x === 0;
        const isRight = x === COLS;
        const isTop = y === 0;
        const isBottom = y === ROWS;
        const isInternal = x > 0 && x < COLS && y > 0 && y < ROWS;
        const mark = document.createElement('div');
        if (isInternal) {
          mark.className = 'cut-mark cross';
        } else if (isLeft && isTop) {
          mark.className = 'cut-mark corner-tl';
        } else if (isRight && isTop) {
          mark.className = 'cut-mark corner-tr';
        } else if (isLeft && isBottom) {
          mark.className = 'cut-mark corner-bl';
        } else if (isRight && isBottom) {
          mark.className = 'cut-mark corner-br';
        } else if (isTop && x > 0 && x < COLS) {
          mark.className = 'cut-mark edge-top';
        } else if (isBottom && x > 0 && x < COLS) {
          mark.className = 'cut-mark edge-bottom';
        } else if (isLeft && y > 0 && y < ROWS) {
          mark.className = 'cut-mark edge-left';
        } else if (isRight && y > 0 && y < ROWS) {
          mark.className = 'cut-mark edge-right';
        } else {
          continue;
        }
        mark.style.left = `calc(${x} * var(--card-w))`;
        mark.style.top = `calc(${y} * var(--card-h))`;
        layer.appendChild(mark);
      }
    }
    grid.appendChild(layer);
  }

  function renderAll() {
    sheetsRoot.innerHTML = '';
    state.pairs.forEach((pair, pairIndex) => {
      const frontSheet = document.createElement('section');
      frontSheet.className = 'sheet front-sheet';
      frontSheet.dataset.pairIndex = String(pairIndex);
      if (pairIndex === state.currentPairIndex) frontSheet.classList.add('current');

      const frontTitle = document.createElement('div');
      frontTitle.className = 'sheet-title';
      frontTitle.textContent = `Пара ${pairIndex + 1} · Лицевая`;
      frontSheet.appendChild(frontTitle);

      const frontGrid = document.createElement('div');
      frontGrid.className = 'card-grid';
      for (let i = 0; i < CARD_COUNT; i += 1) {
        const node = frontCardTemplate.content.firstElementChild.cloneNode(true);
        node.dataset.cardIndex = String(i);
        const editable = node.querySelector('.card-number');
        editable.textContent = pair.frontTexts[i] || DEFAULT_NUMBER;
        editable.addEventListener('input', () => {
          pair.frontTexts[i] = editable.textContent || '';
          scheduleSave();
        });
        frontGrid.appendChild(node);
      }
      appendCutMarks(frontGrid);
      frontSheet.appendChild(frontGrid);

      const backSheet = document.createElement('section');
      backSheet.className = 'sheet back-sheet';
      backSheet.dataset.pairIndex = String(pairIndex);
      if (pairIndex === state.currentPairIndex) backSheet.classList.add('current');

      const backTitle = document.createElement('div');
      backTitle.className = 'sheet-title';
      backTitle.textContent = `Пара ${pairIndex + 1} · Рубашка`;
      backSheet.appendChild(backTitle);

      const backGrid = document.createElement('div');
      backGrid.className = 'card-grid';
      for (let i = 0; i < CARD_COUNT; i += 1) {
        const sourceIndex = mapBackIndex(i);
        const node = backCardTemplate.content.firstElementChild.cloneNode(true);
        node.dataset.cardIndex = String(sourceIndex);
        backGrid.appendChild(node);
      }
      appendCutMarks(backGrid);
      backSheet.appendChild(backGrid);

      sheetsRoot.appendChild(frontSheet);
      sheetsRoot.appendChild(backSheet);
    });
    renderPairInfo();
    scheduleSave();
  }

  function renderPairInfo() {
    pairInfo.textContent = `Пара ${state.currentPairIndex + 1} / ${state.pairs.length}`;
    prevPairBtn.disabled = state.currentPairIndex <= 0;
    nextPairBtn.disabled = state.currentPairIndex >= state.pairs.length - 1;
    removePairBtn.disabled = state.pairs.length <= 1;
    mirrorBacksInput.checked = state.mirrorBacks;
  }

  prevPairBtn.addEventListener('click', () => {
    state.currentPairIndex = clampIndex(state.currentPairIndex - 1, state.pairs.length);
    renderAll();
    const target = document.querySelector(`.sheet[data-pair-index="${state.currentPairIndex}"]`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  nextPairBtn.addEventListener('click', () => {
    state.currentPairIndex = clampIndex(state.currentPairIndex + 1, state.pairs.length);
    renderAll();
    const target = document.querySelector(`.sheet[data-pair-index="${state.currentPairIndex}"]`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  addPairBtn.addEventListener('click', () => {
    state.pairs.push(createDefaultPair());
    state.currentPairIndex = state.pairs.length - 1;
    renderAll();
    const target = document.querySelector(`.sheet[data-pair-index="${state.currentPairIndex}"]`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  removePairBtn.addEventListener('click', () => {
    if (state.pairs.length <= 1) return;
    state.pairs.splice(state.currentPairIndex, 1);
    state.currentPairIndex = clampIndex(state.currentPairIndex, state.pairs.length);
    renderAll();
  });

  mirrorBacksInput.addEventListener('change', () => {
    state.mirrorBacks = !!mirrorBacksInput.checked;
    renderAll();
    safeSaveNow();
  });

  exportBtn.addEventListener('click', () => {
    const payload = buildExportPayload();
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    const safeNs = String(ns).replace(/[^\w.-]+/g, '_');
    a.href = URL.createObjectURL(blob);
    a.download = `mini-american-cards-${safeNs}.json`;
    document.body.appendChild(a);
    a.click();
    URL.revokeObjectURL(a.href);
    a.remove();
  });

  importBtn.addEventListener('click', () => importInput.click());
  importInput.addEventListener('change', async () => {
    const file = importInput.files && importInput.files[0];
    if (!file) return;
    try {
      const text = await file.text();
      const data = JSON.parse(text);
      applyData(data);
      safeSaveNow();
      alert('Импорт выполнен');
    } catch (e) {
      alert('Не удалось импортировать JSON');
    } finally {
      importInput.value = '';
    }
  });

  safeLoad();
  renderAll();
})();
