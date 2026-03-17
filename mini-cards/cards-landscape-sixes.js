(function () {
  const COLS = 3;
  const ROWS = 6;
  const CARD_COUNT = COLS * ROWS;
  const PACK_SIZE = 6;
  const DEFAULT_NUMBER = '3';
  const params = new URLSearchParams(window.location.search);
  const ns = params.get('id') || (location.pathname.split('/').pop() || '').replace(/\.html?$/i, '') || 'default';
  const storageKey = `mini-american-cards-landscape-sixes:${ns}`;

  const sheetsRoot = document.getElementById('sheetsRoot');
  const pairInfo = document.getElementById('pairInfo');
  const packInfo = document.getElementById('packInfo');
  const prevPairBtn = document.getElementById('prevPairBtn');
  const nextPairBtn = document.getElementById('nextPairBtn');
  const prevPackBtn = document.getElementById('prevPackBtn');
  const nextPackBtn = document.getElementById('nextPackBtn');
  const newPackTypeSelect = document.getElementById('newPackTypeSelect');
  const addSixBtn = document.getElementById('addSixBtn');
  const removeSixBtn = document.getElementById('removeSixBtn');
  const loadFrontBgBtn = document.getElementById('loadFrontBgBtn');
  const clearFrontBgBtn = document.getElementById('clearFrontBgBtn');
  const frontBgInput = document.getElementById('frontBgInput');
  const loadBackBgBtn = document.getElementById('loadBackBgBtn');
  const clearBackBgBtn = document.getElementById('clearBackBgBtn');
  const backBgInput = document.getElementById('backBgInput');
  const exportBtn = document.getElementById('exportBtn');
  const saveSizeInfo = document.getElementById('saveSizeInfo');
  const importBtn = document.getElementById('importBtn');
  const importInput = document.getElementById('importInput');
  const mirrorBacksInput = document.getElementById('mirrorBacksInput');
  const frontCardTemplate = document.getElementById('frontCardTemplate');
  const backCardTemplate = document.getElementById('backCardTemplate');

  const state = {
    currentPairIndex: 0,
    currentPackIndex: 0,
    mirrorBacks: true,
    localStorageAvailable: true,
    imagePool: {},
    packs: [createDefaultPack('goal')]
  };

  function createDefaultPack(type) {
    const cardType = type === 'tech' ? 'tech' : 'goal';
    const defaultTechCards = Array.from({ length: PACK_SIZE }, (_, index) => ({
      title: `Технология ${index + 1}`,
      note: 'Базовый модуль',
      desc: 'Короткое описание эффекта технологии для примера.'
    }));
    return {
      cardType,
      frontTexts: Array.from({ length: PACK_SIZE }, () => DEFAULT_NUMBER),
      techCards: cardType === 'tech'
        ? defaultTechCards
        : Array.from({ length: PACK_SIZE }, () => ({ title: '', note: '', desc: '' })),
      frontImageId: '',
      backImageId: ''
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

  function isQuotaExceededError(error) {
    if (!error) return false;
    if (error.name === 'QuotaExceededError') return true;
    if (error.name === 'NS_ERROR_DOM_QUOTA_REACHED') return true;
    return false;
  }

  function safeSaveNow(payloadText) {
    if (!state.localStorageAvailable) return false;
    try {
      const text = typeof payloadText === 'string' ? payloadText : JSON.stringify(buildExportPayload());
      localStorage.setItem(storageKey, text);
      return true;
    } catch (e) {
      if (isQuotaExceededError(e)) {
        state.localStorageAvailable = false;
        updateSaveSizeInfo();
      }
      return false;
    }
  }

  let saveTimer = null;
  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(safeSaveNow, 220);
  }

  function normalizePack(input) {
    const pack = input && typeof input === 'object' ? input : {};
    const cardType = pack.cardType === 'tech' ? 'tech' : 'goal';
    const frontTexts = Array.isArray(pack.frontTexts) ? pack.frontTexts.slice(0, PACK_SIZE) : [];
    while (frontTexts.length < PACK_SIZE) frontTexts.push(DEFAULT_NUMBER);
    const techCardsRaw = Array.isArray(pack.techCards) ? pack.techCards.slice(0, PACK_SIZE) : [];
    while (techCardsRaw.length < PACK_SIZE) techCardsRaw.push({});
    const techCards = techCardsRaw.map((card) => ({
      title: String(card && card.title != null ? card.title : ''),
      note: String(card && card.note != null ? card.note : ''),
      desc: String(card && card.desc != null ? card.desc : '')
    }));
    return {
      cardType,
      frontTexts: frontTexts.map((v) => String(v ?? DEFAULT_NUMBER)),
      techCards,
      frontImageId: typeof pack.frontImageId === 'string' ? pack.frontImageId : '',
      backImageId: typeof pack.backImageId === 'string' ? pack.backImageId : ''
    };
  }

  function applyData(data) {
    if (!data || typeof data !== 'object') return;
    const imagePool = data.imagePool && typeof data.imagePool === 'object' ? data.imagePool : {};
    state.imagePool = {};
    Object.keys(imagePool).forEach((key) => {
      const value = imagePool[key];
      if (typeof value === 'string' && value.startsWith('data:image/')) {
        state.imagePool[key] = value;
      }
    });

    const srcPacks = Array.isArray(data.packs) ? data.packs : [];
    const normalized = srcPacks.map(normalizePack).filter(Boolean);
    state.packs = normalized.length ? normalized : [createDefaultPack('goal')];
    state.mirrorBacks = data.mirrorBacks !== false;

    const idx = Number.isInteger(data.currentPackIndex) ? data.currentPackIndex : 0;
    state.currentPackIndex = clampIndex(idx, state.packs.length);
    state.currentPairIndex = getPairIndexByPack(state.currentPackIndex);
    cleanupImagePool();
    renderAll();
  }

  function buildExportPayload() {
    cleanupImagePool();
    return {
      type: 'mini-american-cards-landscape-sixes',
      version: 1,
      ns,
      currentPackIndex: state.currentPackIndex,
      cardsPerSheet: CARD_COUNT,
      packSize: PACK_SIZE,
      cardSizeMm: { width: 63, height: 41 },
      mirrorBacks: state.mirrorBacks,
      packs: state.packs.map((pack) => ({
        cardType: pack.cardType === 'tech' ? 'tech' : 'goal',
        frontTexts: pack.frontTexts.slice(0, PACK_SIZE),
        techCards: pack.techCards.slice(0, PACK_SIZE).map((card) => ({
          title: String(card.title || ''),
          note: String(card.note || ''),
          desc: String(card.desc || '')
        })),
        frontImageId: pack.frontImageId || '',
        backImageId: pack.backImageId || ''
      })),
      imagePool: { ...state.imagePool }
    };
  }

  function formatBytes(sizeBytes) {
    if (sizeBytes < 1024) return `Вес: ${sizeBytes} B`;
    const kb = sizeBytes / 1024;
    if (kb < 1024) return `Вес: ${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `Вес: ${mb.toFixed(2)} MB`;
  }

  function updateSaveSizeInfo() {
    if (!saveSizeInfo) return;
    const payloadText = JSON.stringify(buildExportPayload());
    const sizeBytes = new Blob([payloadText], { type: 'application/json' }).size;
    const suffix = state.localStorageAvailable ? '' : ' · localStorage переполнен';
    saveSizeInfo.textContent = `${formatBytes(sizeBytes)}${suffix}`;
  }

  function clampIndex(index, total) {
    if (!total) return 0;
    if (index < 0) return 0;
    if (index > total - 1) return total - 1;
    return index;
  }

  function getPairIndexByPack(packIndex) {
    return Math.floor(packIndex / 3);
  }

  function getPackRangeByPair(pairIndex) {
    const start = pairIndex * 3;
    return [start, start + 1, start + 2];
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

  function getImageDataUrl(imageId) {
    if (!imageId) return '';
    return state.imagePool[imageId] || '';
  }

  function createImageId() {
    const rand = Math.random().toString(36).slice(2, 9);
    return `${Date.now().toString(36)}-${rand}`;
  }

  function putImageInPool(dataUrl) {
    const existing = Object.keys(state.imagePool).find((key) => state.imagePool[key] === dataUrl);
    if (existing) return existing;
    const id = createImageId();
    state.imagePool[id] = dataUrl;
    return id;
  }

  function cleanupImagePool() {
    const used = new Set();
    state.packs.forEach((pack) => {
      if (pack.frontImageId && state.imagePool[pack.frontImageId]) used.add(pack.frontImageId);
      if (pack.backImageId && state.imagePool[pack.backImageId]) used.add(pack.backImageId);
    });
    const nextPool = {};
    used.forEach((id) => {
      nextPool[id] = state.imagePool[id];
    });
    state.imagePool = nextPool;
  }

  function getVisibleCardsByPair(pairIndex) {
    const packIndexes = getPackRangeByPair(pairIndex);
    const cards = [];
    packIndexes.forEach((packIndex) => {
      const pack = state.packs[packIndex];
      if (!pack) {
        for (let i = 0; i < PACK_SIZE; i += 1) cards.push(null);
        return;
      }
      for (let i = 0; i < PACK_SIZE; i += 1) {
        cards.push({
          packIndex,
          innerIndex: i,
          globalIndex: packIndex * PACK_SIZE + i,
          cardType: pack.cardType === 'tech' ? 'tech' : 'goal',
          text: pack.frontTexts[i] || DEFAULT_NUMBER,
          techCard: pack.techCards[i] || { title: '', note: '', desc: '' },
          frontImageId: pack.frontImageId || '',
          backImageId: pack.backImageId || ''
        });
      }
    });
    return cards;
  }

  function setCurrentPackByIndex(packIndex) {
    const nextPackIndex = clampIndex(packIndex, state.packs.length);
    const changed = nextPackIndex !== state.currentPackIndex;
    state.currentPackIndex = nextPackIndex;
    state.currentPairIndex = getPairIndexByPack(nextPackIndex);
    return changed;
  }

  function renderAll() {
    sheetsRoot.innerHTML = '';
    const pairCount = Math.max(1, Math.ceil(state.packs.length / 3));
    for (let pairIndex = 0; pairIndex < pairCount; pairIndex += 1) {
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
      const frontCards = getVisibleCardsByPair(pairIndex);
      for (let i = 0; i < CARD_COUNT; i += 1) {
        const source = frontCards[i];
        const node = frontCardTemplate.content.firstElementChild.cloneNode(true);
        if (!source) {
          node.classList.add('empty-card');
          frontGrid.appendChild(node);
          continue;
        }
        node.dataset.cardIndex = String(source.globalIndex);
        node.dataset.packIndex = String(source.packIndex);
        node.dataset.cardType = source.cardType;
        node.classList.toggle('is-goal', source.cardType === 'goal');
        node.classList.toggle('is-tech', source.cardType === 'tech');
        if (source.packIndex === state.currentPackIndex) node.classList.add('current-pack');
        const frontImage = getImageDataUrl(source.frontImageId);
        node.style.backgroundImage = frontImage ? `url("${frontImage}")` : '';
        node.addEventListener('click', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        const goalText = node.querySelector('.goal-text');
        const techTitle = node.querySelector('.tech-title');
        const techNote = node.querySelector('.tech-note');
        const techDesc = node.querySelector('.tech-desc');

        goalText.textContent = source.text;
        techTitle.textContent = source.techCard.title || '';
        techNote.textContent = source.techCard.note || '';
        techDesc.textContent = source.techCard.desc || '';

        goalText.addEventListener('focus', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        goalText.addEventListener('input', () => {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          pack.frontTexts[source.innerIndex] = goalText.textContent || '';
          scheduleSave();
        });
        techTitle.addEventListener('focus', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        techNote.addEventListener('focus', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        techDesc.addEventListener('focus', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        techTitle.addEventListener('input', () => {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          const target = pack.techCards[source.innerIndex];
          if (!target) return;
          target.title = techTitle.textContent || '';
          scheduleSave();
        });
        techNote.addEventListener('input', () => {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          const target = pack.techCards[source.innerIndex];
          if (!target) return;
          target.note = techNote.textContent || '';
          scheduleSave();
        });
        techDesc.addEventListener('input', () => {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          const target = pack.techCards[source.innerIndex];
          if (!target) return;
          target.desc = techDesc.textContent || '';
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
        const source = frontCards[sourceIndex];
        const node = backCardTemplate.content.firstElementChild.cloneNode(true);
        if (!source) {
          node.classList.add('empty-card');
          backGrid.appendChild(node);
          continue;
        }
        node.dataset.cardIndex = String(source.globalIndex);
        node.dataset.packIndex = String(source.packIndex);
        if (source.packIndex === state.currentPackIndex) node.classList.add('current-pack');
        const backImage = getImageDataUrl(source.backImageId);
        node.style.backgroundImage = backImage ? `url("${backImage}")` : '';
        node.addEventListener('click', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        backGrid.appendChild(node);
      }
      appendCutMarks(backGrid);
      backSheet.appendChild(backGrid);

      sheetsRoot.appendChild(frontSheet);
      sheetsRoot.appendChild(backSheet);
    }
    state.currentPairIndex = clampIndex(state.currentPairIndex, pairCount);
    renderToolbarState();
    scheduleSave();
  }

  function renderToolbarState() {
    const pairCount = Math.max(1, Math.ceil(state.packs.length / 3));
    pairInfo.textContent = `Пара ${state.currentPairIndex + 1} / ${pairCount}`;
    packInfo.textContent = `Шестёрка ${state.currentPackIndex + 1} / ${state.packs.length}`;
    prevPairBtn.disabled = state.currentPairIndex <= 0;
    nextPairBtn.disabled = state.currentPairIndex >= pairCount - 1;
    prevPackBtn.disabled = state.currentPackIndex <= 0;
    nextPackBtn.disabled = state.currentPackIndex >= state.packs.length - 1;
    removeSixBtn.disabled = state.packs.length <= 1;
    mirrorBacksInput.checked = state.mirrorBacks;
    updateSaveSizeInfo();
  }

  function scrollToCurrentPair() {
    const target = document.querySelector(`.sheet[data-pair-index="${state.currentPairIndex}"]`);
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  async function fileToDataUrl(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ''));
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  async function loadImageForCurrentPack(input, side) {
    const file = input.files && input.files[0];
    if (!file) return;
    try {
      const dataUrl = await fileToDataUrl(file);
      if (!dataUrl.startsWith('data:image/')) throw new Error('bad image');
      const imageId = putImageInPool(dataUrl);
      const pack = state.packs[state.currentPackIndex];
      if (!pack) return;
      if (side === 'front') pack.frontImageId = imageId;
      if (side === 'back') pack.backImageId = imageId;
      renderAll();
      safeSaveNow();
    } catch (e) {
      alert('Не удалось загрузить изображение');
    } finally {
      input.value = '';
    }
  }

  function clearImageForCurrentPack(side) {
    const pack = state.packs[state.currentPackIndex];
    if (!pack) return;
    if (side === 'front') pack.frontImageId = '';
    if (side === 'back') pack.backImageId = '';
    cleanupImagePool();
    renderAll();
    safeSaveNow();
  }

  prevPairBtn.addEventListener('click', () => {
    const pairCount = Math.max(1, Math.ceil(state.packs.length / 3));
    state.currentPairIndex = clampIndex(state.currentPairIndex - 1, pairCount);
    const firstPack = state.currentPairIndex * 3;
    if (firstPack < state.packs.length) setCurrentPackByIndex(firstPack);
    renderAll();
    scrollToCurrentPair();
  });

  nextPairBtn.addEventListener('click', () => {
    const pairCount = Math.max(1, Math.ceil(state.packs.length / 3));
    state.currentPairIndex = clampIndex(state.currentPairIndex + 1, pairCount);
    const firstPack = state.currentPairIndex * 3;
    if (firstPack < state.packs.length) setCurrentPackByIndex(firstPack);
    renderAll();
    scrollToCurrentPair();
  });

  prevPackBtn.addEventListener('click', () => {
    setCurrentPackByIndex(state.currentPackIndex - 1);
    renderAll();
    scrollToCurrentPair();
  });

  nextPackBtn.addEventListener('click', () => {
    setCurrentPackByIndex(state.currentPackIndex + 1);
    renderAll();
    scrollToCurrentPair();
  });

  addSixBtn.addEventListener('click', () => {
    const type = newPackTypeSelect && newPackTypeSelect.value === 'tech' ? 'tech' : 'goal';
    state.packs.push(createDefaultPack(type));
    setCurrentPackByIndex(state.packs.length - 1);
    renderAll();
    scrollToCurrentPair();
  });

  removeSixBtn.addEventListener('click', () => {
    if (state.packs.length <= 1) return;
    state.packs.splice(state.currentPackIndex, 1);
    setCurrentPackByIndex(state.currentPackIndex);
    cleanupImagePool();
    renderAll();
  });

  loadFrontBgBtn.addEventListener('click', () => frontBgInput.click());
  frontBgInput.addEventListener('change', () => loadImageForCurrentPack(frontBgInput, 'front'));
  loadBackBgBtn.addEventListener('click', () => backBgInput.click());
  backBgInput.addEventListener('change', () => loadImageForCurrentPack(backBgInput, 'back'));

  clearFrontBgBtn.addEventListener('click', () => clearImageForCurrentPack('front'));
  clearBackBgBtn.addEventListener('click', () => clearImageForCurrentPack('back'));

  mirrorBacksInput.addEventListener('change', () => {
    state.mirrorBacks = !!mirrorBacksInput.checked;
    renderAll();
    safeSaveNow();
  });

  exportBtn.addEventListener('click', () => {
    const payload = buildExportPayload();
    const payloadText = JSON.stringify(payload, null, 2);
    const blob = new Blob([payloadText], { type: 'application/json' });
    const a = document.createElement('a');
    const safeNs = String(ns).replace(/[^\w.-]+/g, '_');
    a.href = URL.createObjectURL(blob);
    a.download = `mini-american-cards-landscape-sixes-${safeNs}.json`;
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
      safeSaveNow(JSON.stringify(buildExportPayload()));
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
