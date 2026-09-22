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
      titleHtml: '',
      titleFontPx: null,
      note: 'Базовый модуль',
      noteFontPx: null,
      desc: 'Короткое описание эффекта технологии для примера.',
      descHtml: '',
      descFontPx: null
    }));
    return {
      cardType,
      frontTexts: Array.from({ length: PACK_SIZE }, () => DEFAULT_NUMBER),
      goalRichTexts: Array.from({ length: PACK_SIZE }, () => DEFAULT_NUMBER),
      goalTextFontPx: Array.from({ length: PACK_SIZE }, () => null),
      techCards: cardType === 'tech'
        ? defaultTechCards
        : Array.from({ length: PACK_SIZE }, () => ({ title: '', titleHtml: '', titleFontPx: null, note: '', noteFontPx: null, desc: '', descHtml: '', descFontPx: null })),
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
    const goalRichTexts = Array.isArray(pack.goalRichTexts) ? pack.goalRichTexts.slice(0, PACK_SIZE) : [];
    while (goalRichTexts.length < PACK_SIZE) goalRichTexts.push('');
    const goalTextFontPx = Array.isArray(pack.goalTextFontPx) ? pack.goalTextFontPx.slice(0, PACK_SIZE) : [];
    while (goalTextFontPx.length < PACK_SIZE) goalTextFontPx.push(null);
    const techCardsRaw = Array.isArray(pack.techCards) ? pack.techCards.slice(0, PACK_SIZE) : [];
    while (techCardsRaw.length < PACK_SIZE) techCardsRaw.push({});
    const techCards = techCardsRaw.map((card) => ({
      title: String(card && card.title != null ? card.title : ''),
      titleHtml: String(card && card.titleHtml != null ? card.titleHtml : ''),
      titleFontPx: Number.isFinite(Number(card && card.titleFontPx)) ? Number(card.titleFontPx) : null,
      note: String(card && card.note != null ? card.note : ''),
      noteFontPx: Number.isFinite(Number(card && card.noteFontPx)) ? Number(card.noteFontPx) : null,
      desc: String(card && card.desc != null ? card.desc : ''),
      descHtml: String(card && card.descHtml != null ? card.descHtml : ''),
      descFontPx: Number.isFinite(Number(card && card.descFontPx)) ? Number(card.descFontPx) : null
    }));
    return {
      cardType,
      frontTexts: frontTexts.map((v) => String(v ?? DEFAULT_NUMBER)),
      goalRichTexts: goalRichTexts.map((v, index) => String(v || frontTexts[index] || DEFAULT_NUMBER)),
      goalTextFontPx: goalTextFontPx.map((v) => (Number.isFinite(Number(v)) ? Number(v) : null)),
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
        goalRichTexts: pack.goalRichTexts.slice(0, PACK_SIZE),
        goalTextFontPx: pack.goalTextFontPx.slice(0, PACK_SIZE),
        techCards: pack.techCards.slice(0, PACK_SIZE).map((card) => {
          const normalizedCard = {
            title: String(card.title || ''),
            titleHtml: String(card.titleHtml || ''),
            note: String(card.note || ''),
            desc: String(card.desc || ''),
            descHtml: String(card.descHtml || '')
          };
          if (Number.isFinite(card.titleFontPx) && card.titleFontPx > 0) {
            normalizedCard.titleFontPx = Number(card.titleFontPx);
          }
          if (Number.isFinite(card.noteFontPx) && card.noteFontPx > 0) {
            normalizedCard.noteFontPx = Number(card.noteFontPx);
          }
          if (Number.isFinite(card.descFontPx) && card.descFontPx > 0) {
            normalizedCard.descFontPx = Number(card.descFontPx);
          }
          return normalizedCard;
        }),
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
          goalRichText: pack.goalRichTexts[i] || pack.frontTexts[i] || DEFAULT_NUMBER,
          techCard: pack.techCards[i] || { title: '', titleHtml: '', note: '', desc: '', descHtml: '' },
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

  function readMultilineEditableText(node) {
    if (!node) return '';
    return String(node.innerText || '').replace(/\r\n/g, '\n');
  }

  function plainTextToEditableHtml(text) {
    const normalized = String(text || '').replace(/\r\n?/g, '\n');
    const temp = document.createElement('div');
    temp.textContent = normalized;
    return temp.innerHTML.replace(/\n/g, '<br>');
  }

  function sanitizeRichHtml(rawHtml) {
    const temp = document.createElement('div');
    temp.innerHTML = String(rawHtml || '');
    const allowedTags = new Set(['BR', 'B', 'STRONG', 'I', 'EM', 'SPAN']);
    const walk = (node) => {
      const children = Array.from(node.childNodes);
      children.forEach((child) => {
        if (child.nodeType === Node.ELEMENT_NODE) {
          const tag = child.tagName.toUpperCase();
          if (tag === 'DIV' || tag === 'P') {
            const fragment = document.createDocumentFragment();
            const prev = child.previousSibling;
            if (prev && !(prev.nodeType === Node.ELEMENT_NODE && prev.tagName === 'BR')) {
              fragment.appendChild(document.createElement('br'));
            }
            while (child.firstChild) fragment.appendChild(child.firstChild);
            fragment.appendChild(document.createElement('br'));
            child.replaceWith(fragment);
            return;
          }
          if (!allowedTags.has(tag)) {
            const fragment = document.createDocumentFragment();
            while (child.firstChild) fragment.appendChild(child.firstChild);
            child.replaceWith(fragment);
            return;
          }
          if (tag === 'SPAN') {
            const style = child.getAttribute('style') || '';
            const styleMap = style.split(';').map((part) => part.trim()).filter(Boolean);
            const kept = [];
            styleMap.forEach((entry) => {
              const [keyRaw, valueRaw] = entry.split(':');
              const key = String(keyRaw || '').trim().toLowerCase();
              const value = String(valueRaw || '').trim();
              if (!value) return;
              if (key === 'font-family' || key === 'font-style' || key === 'font-weight') {
                kept.push(`${key}: ${value}`);
              }
            });
            if (kept.length) child.setAttribute('style', kept.join('; '));
            else child.removeAttribute('style');
          }
          Array.from(child.attributes).forEach((attr) => {
            if (attr.name === 'style') return;
            child.removeAttribute(attr.name);
          });
          walk(child);
          return;
        }
        if (child.nodeType !== Node.TEXT_NODE) {
          child.remove();
        }
      });
    };
    walk(temp);
    return temp.innerHTML;
  }

  function normalizePastedText(text, singleLine) {
    const normalized = String(text || '').replace(/\r\n?/g, '\n');
    if (!singleLine) return normalized;
    return normalized.replace(/\n+/g, ' ');
  }

  function insertPlainTextAtCursor(node, text) {
    if (!node) return;
    node.focus();
    if (document.queryCommandSupported && document.queryCommandSupported('insertText')) {
      document.execCommand('insertText', false, text);
      return;
    }
    const selection = window.getSelection();
    if (!selection || selection.rangeCount === 0) {
      node.textContent = `${node.textContent || ''}${text}`;
      return;
    }
    const range = selection.getRangeAt(0);
    range.deleteContents();
    const textNode = document.createTextNode(text);
    range.insertNode(textNode);
    range.setStartAfter(textNode);
    range.collapse(true);
    selection.removeAllRanges();
    selection.addRange(range);
  }

  function attachPlainTextPaste(node, singleLine) {
    if (!node) return;
    node.addEventListener('paste', (event) => {
      event.preventDefault();
      const clipboard = event.clipboardData || window.clipboardData;
      const raw = clipboard ? (clipboard.getData('text/plain') || clipboard.getData('text') || '') : '';
      const text = normalizePastedText(raw, !!singleLine);
      insertPlainTextAtCursor(node, text);
    });
  }

  function getCurrentFontPx(node) {
    if (!node) return 12;
    const inlinePx = parseFloat(node.style.fontSize);
    if (Number.isFinite(inlinePx) && inlinePx > 0) return inlinePx;
    const cssPx = parseFloat(window.getComputedStyle(node).fontSize);
    return Number.isFinite(cssPx) && cssPx > 0 ? cssPx : 12;
  }

  function showCardControls(cardNode, activeClassName) {
    if (!cardNode) return;
    cardNode.classList.add('controls-visible');
    cardNode.dataset.activeField = activeClassName;
  }

  function hideCardControls(cardNode) {
    if (!cardNode) return;
    cardNode.classList.remove('controls-visible');
    delete cardNode.dataset.activeField;
  }

  function fitTechDescFont(node) {
    if (!node) return null;
    const maxLines = 6;
    const minFontPx = 8;
    const stepPx = 0.5;

    node.style.fontSize = '';
    const computed = window.getComputedStyle(node);
    const cssFontPx = parseFloat(computed.fontSize);
    const maxFontPx = Number.isFinite(cssFontPx) && cssFontPx > 0 ? cssFontPx : 12;
    let lineHeightPx = parseFloat(computed.lineHeight);
    if (!Number.isFinite(lineHeightPx) || lineHeightPx <= 0) {
      lineHeightPx = maxFontPx * 1.25;
    }
    const maxHeightPx = lineHeightPx * maxLines;
    if (node.scrollHeight <= maxHeightPx + 0.5) {
      node.style.fontSize = '';
      return null;
    }
    let fontPx = maxFontPx;

    while (fontPx > minFontPx && node.scrollHeight > maxHeightPx + 0.5) {
      fontPx -= stepPx;
      node.style.fontSize = `${fontPx}px`;
    }
    if (fontPx < maxFontPx - 0.01) return Math.round(fontPx * 100) / 100;
    node.style.fontSize = '';
    return null;
  }

  function applyRichCommand(editableNode, command, value) {
    if (!editableNode) return;
    editableNode.focus();
    if (command === 'fontName') document.execCommand('styleWithCSS', false, true);
    if (value != null) document.execCommand(command, false, value);
    else document.execCommand(command, false);
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
        const sizeControls = node.querySelector('.text-size-controls');
        const formatControls = node.querySelector('.text-format-controls');
        const controlsList = [sizeControls, formatControls].filter(Boolean);
        const decBtn = node.querySelector('.text-size-dec');
        const incBtn = node.querySelector('.text-size-inc');
        const fontSelect = node.querySelector('.text-font-select');
        const boldBtn = node.querySelector('.text-bold-btn');
        const italicBtn = node.querySelector('.text-italic-btn');
        let controlsMouseDown = false;
        let lastRichRange = null;
        let lastRichOwner = null;

        attachPlainTextPaste(goalText, false);
        attachPlainTextPaste(techTitle, false);
        attachPlainTextPaste(techNote, true);
        attachPlainTextPaste(techDesc, false);

        goalText.innerHTML = sanitizeRichHtml(source.goalRichText || source.text);
        techTitle.innerHTML = sanitizeRichHtml(source.techCard.titleHtml || plainTextToEditableHtml(source.techCard.title || ''));
        techNote.textContent = source.techCard.note || '';
        techDesc.innerHTML = sanitizeRichHtml(source.techCard.descHtml || plainTextToEditableHtml(source.techCard.desc || ''));
        const presetGoalFont = Number.isFinite(state.packs[source.packIndex].goalTextFontPx[source.innerIndex])
          ? Number(state.packs[source.packIndex].goalTextFontPx[source.innerIndex])
          : null;
        const presetTitleFont = Number.isFinite(source.techCard.titleFontPx) ? Number(source.techCard.titleFontPx) : null;
        const presetNoteFont = Number.isFinite(source.techCard.noteFontPx) ? Number(source.techCard.noteFontPx) : null;
        const presetDescFont = Number.isFinite(source.techCard.descFontPx) ? Number(source.techCard.descFontPx) : null;
        goalText.style.fontSize = presetGoalFont ? `${presetGoalFont}px` : '';
        techTitle.style.fontSize = presetTitleFont ? `${presetTitleFont}px` : '';
        techNote.style.fontSize = presetNoteFont ? `${presetNoteFont}px` : '';
        techDesc.style.fontSize = presetDescFont ? `${presetDescFont}px` : '';

        const editableNodes = [goalText, techTitle, techNote, techDesc];
        editableNodes.forEach((editableNode) => {
          editableNode.addEventListener('focus', () => showCardControls(node, editableNode.className));
          editableNode.addEventListener('click', () => showCardControls(node, editableNode.className));
          editableNode.addEventListener('blur', () => {
            setTimeout(() => {
              if (controlsMouseDown) return;
              const active = document.activeElement;
              if (active && controlsList.some((c) => c.contains(active))) return;
              if (active && editableNodes.includes(active)) return;
              hideCardControls(node);
            }, 0);
          });
        });

        function saveRichSelection(editableNode) {
          const selection = window.getSelection();
          if (!selection || selection.rangeCount === 0) return;
          const range = selection.getRangeAt(0);
          const ancestor = range.commonAncestorContainer;
          if (!editableNode.contains(ancestor)) return;
          lastRichRange = range.cloneRange();
          lastRichOwner = editableNode;
        }

        [goalText, techDesc].forEach((editableNode) => {
          editableNode.addEventListener('keyup', () => saveRichSelection(editableNode));
          editableNode.addEventListener('mouseup', () => saveRichSelection(editableNode));
          editableNode.addEventListener('focus', () => saveRichSelection(editableNode));
        });

        controlsList.forEach((controlsNode) => {
          controlsNode.addEventListener('mousedown', () => {
            controlsMouseDown = true;
            showCardControls(node, node.dataset.activeField || '');
          });
          controlsNode.addEventListener('mouseup', () => {
            controlsMouseDown = false;
          });
          controlsNode.addEventListener('mouseleave', () => {
            controlsMouseDown = false;
          });
        });

        function updateFontByButton(deltaPx) {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          const activeField = node.dataset.activeField || '';
          const targetNode =
            activeField.indexOf('goal-text') >= 0 ? goalText :
              activeField.indexOf('tech-title') >= 0 ? techTitle :
                activeField.indexOf('tech-note') >= 0 ? techNote :
                  activeField.indexOf('tech-desc') >= 0 ? techDesc : null;
          if (!targetNode) return;
          const currentFontPx = getCurrentFontPx(targetNode);
          const nextFontPx = Math.max(8, Math.min(28, currentFontPx + deltaPx));
          targetNode.style.fontSize = `${nextFontPx}px`;
          if (targetNode === goalText) {
            pack.goalTextFontPx[source.innerIndex] = nextFontPx;
          } else if (targetNode === techTitle) {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.titleFontPx = nextFontPx;
          } else if (targetNode === techNote) {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.noteFontPx = nextFontPx;
          } else if (targetNode === techDesc) {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.descFontPx = nextFontPx;
          }
          scheduleSave();
        }

        function getActiveRichEditableNode() {
          const activeField = node.dataset.activeField || '';
          if (activeField.indexOf('goal-text') >= 0) return goalText;
          if (activeField.indexOf('tech-desc') >= 0) return techDesc;
          if (lastRichOwner === goalText || lastRichOwner === techDesc) return lastRichOwner;
          return null;
        }

        function restoreRichSelection(targetNode) {
          if (!targetNode || !lastRichRange || lastRichOwner !== targetNode) return;
          const selection = window.getSelection();
          if (!selection) return;
          selection.removeAllRanges();
          selection.addRange(lastRichRange);
        }

        decBtn.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          updateFontByButton(-0.5);
        });
        incBtn.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          updateFontByButton(0.5);
        });
        fontSelect.addEventListener('change', (event) => {
          event.preventDefault();
          event.stopPropagation();
          const targetNode = getActiveRichEditableNode();
          if (!targetNode) return;
          restoreRichSelection(targetNode);
          applyRichCommand(targetNode, 'fontName', fontSelect.value);
          saveRichSelection(targetNode);
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          if (targetNode === goalText) {
            pack.goalRichTexts[source.innerIndex] = sanitizeRichHtml(goalText.innerHTML);
            pack.frontTexts[source.innerIndex] = readMultilineEditableText(goalText);
          } else {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.descHtml = sanitizeRichHtml(techDesc.innerHTML);
            target.desc = readMultilineEditableText(techDesc);
          }
          scheduleSave();
        });
        boldBtn.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          const targetNode = getActiveRichEditableNode();
          if (!targetNode) return;
          restoreRichSelection(targetNode);
          applyRichCommand(targetNode, 'bold');
          saveRichSelection(targetNode);
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          if (targetNode === goalText) pack.goalRichTexts[source.innerIndex] = sanitizeRichHtml(goalText.innerHTML);
          else {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.descHtml = sanitizeRichHtml(techDesc.innerHTML);
          }
          scheduleSave();
        });
        italicBtn.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();
          const targetNode = getActiveRichEditableNode();
          if (!targetNode) return;
          restoreRichSelection(targetNode);
          applyRichCommand(targetNode, 'italic');
          saveRichSelection(targetNode);
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          if (targetNode === goalText) pack.goalRichTexts[source.innerIndex] = sanitizeRichHtml(goalText.innerHTML);
          else {
            const target = pack.techCards[source.innerIndex];
            if (!target) return;
            target.descHtml = sanitizeRichHtml(techDesc.innerHTML);
          }
          scheduleSave();
        });

        goalText.addEventListener('focus', () => {
          if (!setCurrentPackByIndex(source.packIndex)) return;
          renderAll();
        });
        goalText.addEventListener('input', () => {
          const pack = state.packs[source.packIndex];
          if (!pack) return;
          pack.goalRichTexts[source.innerIndex] = sanitizeRichHtml(goalText.innerHTML);
          pack.frontTexts[source.innerIndex] = readMultilineEditableText(goalText);
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
          target.titleHtml = sanitizeRichHtml(techTitle.innerHTML);
          target.title = readMultilineEditableText(techTitle);
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
          target.descHtml = sanitizeRichHtml(techDesc.innerHTML);
          target.desc = readMultilineEditableText(techDesc);
          target.descFontPx = fitTechDescFont(techDesc);
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
        node.dataset.cardType = source.cardType;
        node.classList.toggle('is-goal', source.cardType === 'goal');
        node.classList.toggle('is-tech', source.cardType === 'tech');
        if (source.packIndex === state.currentPackIndex) node.classList.add('current-pack');
        const backImage = getImageDataUrl(source.backImageId);
        const centerIcon = node.querySelector('.back-center-icon');
        centerIcon.style.backgroundImage = backImage ? `url("${backImage}")` : '';
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
