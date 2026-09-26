"""Скачивание страниц из сети в source/web/ по списку адресов.

    python rules/tools/fetch.py              # скачать всё из очереди
    python rules/tools/fetch.py --dry        # только показать, что и как будет скачано
    python rules/tools/fetch.py --force      # перекачать, даже если файл уже есть
    python rules/tools/fetch.py список.txt   # взять адреса из другого файла

Очередь — `rules/tools/fetch-queue.txt`, по строке на адрес. Сюда пишет
Claude, когда сам достучаться до сайта не может. Формат строки:

    https://boardgamegeek.com/thread/2189926 — They Break Through
    1. https://example.com/page — комментарий     (нумерация не мешает)
    [страница] https://boardgamegeek.com/thread/2189926 — нужна с картинками

Комментарий после адреса идёт в заголовок и в имя файла. Строки с `#` — комментарии.
После прогона скачанные строки из очереди стираются, нескачанные остаются.

Как качается:

1. Тред BoardGameGeek (`/thread/<id>`) — через JSON-API сайта
   (api.geekdo.com), без браузера: все посты всех страниц, автор, дата,
   текст поста как есть. Результат — один `.md`. Картинки из постов
   остаются ссылками.
2. Любая другая страница или строка с меткой `[страница]` — через
   настоящий браузер (Edge или Chrome, что установлено) в видимом окне.
   Результат — `.mhtml` (страница целиком, с картинками, открывается
   в браузере) и `.md` (видимый текст страницы). Если Cloudflare покажет
   проверку — пройди её в этом окне руками, скрипт ждёт 3 минуты.
   Профиль браузера отдельный и живёт в %LOCALAPPDATA%\\ow-fetch —
   пройденная проверка запоминается между запусками.

Если API BoardGameGeek отказал (403/429), скрипт перестаёт к нему ходить
и оставшиеся треды качает через браузер.

Темп — «человеческий»: 6–12 с между запросами к API, 20–40 с между
страницами в браузере. Повторных попыток нет: что не скачалось, остаётся
в очереди и печатается списком в конце — это сохраняется руками
(Ctrl+S → «Веб-страница, один файл») в source/web/.

Зависимости: для тредов BGG — ничего сверх Python. Для режима браузера —
`pip install playwright` (браузер не скачивается, берётся установленный).
"""
import argparse, datetime, html, json, math, os, random, re, sys, time
import urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = Path(__file__).resolve().with_name('fetch-queue.txt')
OUT = ROOT / 'source' / 'web'
PROFILE = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'ow-fetch' / 'profile'
TODAY = f'{datetime.date.today():%Y-%m-%d}'

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0')
API = 'https://api.geekdo.com/api'
API_PAUSE = (6, 12)
PAGE_PAUSE = (20, 40)
CF_WAIT = 180

QUEUE_HEADER = """\
# Очередь скачивания для rules/tools/fetch.py. По строке на адрес.
#   https://адрес — комментарий           → тред BGG: .md через API; остальное: .mhtml + .md
#   [страница] https://адрес — комментарий → всегда через браузер, с картинками
# Скачанные строки стираются; то, что не скачалось, остаётся.
"""

URL_RE = re.compile(r'https?://\S+')
BGG_THREAD_RE = re.compile(r'^https?://(?:www\.)?boardgamegeek\.com/thread/(\d+)', re.I)

try:
    sys.stdout.reconfigure(errors='replace')
except AttributeError:
    pass


# ── Очередь ──────────────────────────────────────────────────────────────

class Item:
    def __init__(self, line, url, comment, force_page):
        self.line, self.url, self.comment, self.force_page = line, url, comment, force_page
        m = BGG_THREAD_RE.match(url)
        self.thread_id = m.group(1) if m else None

    @property
    def mode(self):
        return 'api' if self.thread_id and not self.force_page else 'page'


def parse_queue(path: Path):
    items = []
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        m = URL_RE.search(s)
        if not m:
            print(f'  пропуск, нет адреса: {s}')
            continue
        url = m.group(0).rstrip('.,;)')
        comment = s[m.end():].strip().lstrip('—–-:|').strip()
        force_page = '[страница]' in s[:m.start()].lower()
        items.append(Item(line, url, comment, force_page))
    return items


def rewrite_queue(path: Path, done_lines):
    if path != QUEUE:
        return  # чужой список не трогаем
    header = set(QUEUE_HEADER.splitlines())
    body = [l for l in path.read_text(encoding='utf-8-sig').splitlines()
            if l not in done_lines and l not in header]
    path.write_text(QUEUE_HEADER + '\n'.join(body).strip('\n') + ('\n' if body else ''),
                    encoding='utf-8')


# ── Имена файлов ─────────────────────────────────────────────────────────

def slug(text, limit=40):
    words = re.findall(r'[A-Za-z0-9]+', text or '')
    s = '-'.join(words).lower()
    return s[:limit].rstrip('-')


def base_name(item: Item):
    if item.thread_id:
        prefix = f'BGG-{item.thread_id}'
    else:
        host = re.sub(r'^www\.', '', re.match(r'https?://([^/]+)', item.url).group(1))
        prefix = 'WEB-' + slug(host, 30)
        if not item.comment:
            prefix += '__' + slug(item.url.split('/', 3)[-1], 40)
    s = slug(item.comment)
    return f'{prefix}__{s}__{TODAY}' if s else f'{prefix}__{TODAY}'


def existing(item: Item):
    """Уже скачанное раньше — под любой датой."""
    stem = base_name(item).rsplit('__', 1)[0]
    return sorted(OUT.glob(f'{stem}__*.md'))


# ── Пауза ────────────────────────────────────────────────────────────────

_last = 0.0


def pause(rng):
    global _last
    wait = random.uniform(*rng) - (time.monotonic() - _last)
    if _last and wait > 0:
        time.sleep(wait)
    _last = time.monotonic()


# ── Режим 1: тред BGG через API ──────────────────────────────────────────

class Blocked(Exception):
    pass


def api_get(path):
    pause(API_PAUSE)
    req = urllib.request.Request(f'{API}/{path}', headers={
        'User-Agent': UA, 'Accept': 'application/json',
        'Referer': 'https://boardgamegeek.com/', 'Origin': 'https://boardgamegeek.com'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503):
            raise Blocked(f'API ответил {e.code}')
        raise
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise Blocked('API вернул не JSON (вероятно, страница проверки Cloudflare)')


TAG_RE = re.compile(r'<(br|p|div|/p|/div|li|/li|blockquote|/blockquote|img|a|/a|b|/b|i|/i|span|/span)\b', re.I)


def body_text(body):
    if not body:
        return ''
    if not TAG_RE.search(body):
        return body.strip()
    t = re.sub(r'<br\s*/?>', '\n', body, flags=re.I)
    t = re.sub(r'</(p|div|li|blockquote)>', '\n\n', t, flags=re.I)
    t = re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', r'[картинка: \1]', t, flags=re.I)
    t = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r'\2 (\1)', t, flags=re.I | re.S)
    t = re.sub(r'<[^>]+>', '', t)
    return re.sub(r'\n{3,}', '\n\n', html.unescape(t)).strip()


def fmt_date(s):
    if not s:
        return ''
    try:
        d = datetime.datetime.fromisoformat(s)
        return d.astimezone(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    except ValueError:
        return s


def fetch_thread(item: Item, users: dict):
    tid = item.thread_id
    first = api_get(f'articles?threadid={tid}&pageid=1')
    articles = list(first.get('articles') or [])
    total, per = int(first.get('total') or 0), int(first.get('perPage') or 25)
    if not articles:
        raise RuntimeError('API не вернул ни одного поста')
    for page in range(2, math.ceil(total / per) + 1):
        print(f'    страница постов {page} из {math.ceil(total / per)}')
        articles += api_get(f'articles?threadid={tid}&pageid={page}').get('articles') or []

    for a in articles:
        uid = str(a.get('author') or '')
        if uid and uid not in users:
            try:
                u = api_get(f'users/{uid}')
                users[uid] = u.get('username') or f'user {uid}'
            except Blocked:
                raise
            except Exception:
                users[uid] = f'user {uid}'

    title = item.comment or f'Тред BGG {tid}'
    out = [f'# {title}', '',
           f'- Источник: {item.url}',
           f'- Получено: {TODAY}, через {API}/articles?threadid={tid}',
           f'- Постов: {len(articles)}' + (f' (API сообщил {total})' if total != len(articles) else ''),
           '- Текст постов — как в источнике, разметка BGG ([b], [q], [imageid] …) не раскрывалась.',
           '']
    for n, a in enumerate(articles, 1):
        who = users.get(str(a.get('author') or ''), '?')
        when = fmt_date(a.get('postdate'))
        edit = fmt_date(a.get('editdate'))
        href = a.get('href') or ''
        link = f'https://boardgamegeek.com{href}' if href.startswith('/') else href
        head = f'## {n}. {who} · {when}'
        if edit and edit != when:
            head += f' (изменён {edit})'
        out += ['---', '', head, '', f'<{link}>' if link else '', '', body_text(a.get('body')), '']
    path = OUT / f'{base_name(item)}.md'
    path.write_text('\n'.join(out), encoding='utf-8')
    return [path]


# ── Режим 2: страница через браузер ──────────────────────────────────────

class Browser:
    def __init__(self):
        self.pw = self.ctx = None

    def open(self):
        if self.ctx:
            return self.ctx
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError('нет playwright — выполни: pip install playwright')
        self.pw = sync_playwright().start()
        PROFILE.mkdir(parents=True, exist_ok=True)
        last = None
        for channel in ('msedge', 'chrome'):
            try:
                self.ctx = self.pw.chromium.launch_persistent_context(
                    str(PROFILE), channel=channel, headless=False,
                    args=['--disable-blink-features=AutomationControlled'],
                    ignore_default_args=['--enable-automation'],
                    viewport={'width': 1280, 'height': 900})
                print(f'    браузер: {channel}')
                return self.ctx
            except Exception as e:
                last = e
        raise RuntimeError(f'не удалось запустить ни Edge, ни Chrome: {last}')

    def close(self):
        if self.ctx:
            self.ctx.close()
        if self.pw:
            self.pw.stop()


def is_challenge(page):
    try:
        t = page.title().lower()
    except Exception:
        return True
    if 'just a moment' in t or 'один момент' in t or 'attention required' in t:
        return True
    return page.locator('iframe[src*="challenges.cloudflare.com"], #challenge-running, #cf-challenge-running').count() > 0


def fetch_page(item: Item, browser: Browser):
    pause(PAGE_PAUSE)
    ctx = browser.open()
    page = ctx.new_page()
    try:
        page.goto(item.url, wait_until='domcontentloaded', timeout=60_000)
        if is_challenge(page):
            print(f'    Cloudflare: пройди проверку в окне браузера, жду до {CF_WAIT // 60} мин')
            deadline = time.monotonic() + CF_WAIT
            while is_challenge(page):
                if time.monotonic() > deadline:
                    raise RuntimeError('проверка Cloudflare не пройдена')
                time.sleep(2)
        try:
            page.wait_for_load_state('networkidle', timeout=30_000)
        except Exception:
            pass
        # медленно прокрутить вниз — чтобы подгрузились ленивые картинки
        for _ in range(30):
            at_end = page.evaluate('window.scrollY + window.innerHeight >= document.body.scrollHeight - 5')
            if at_end:
                break
            page.mouse.wheel(0, random.randint(500, 800))
            time.sleep(random.uniform(0.4, 0.9))
        time.sleep(2)
        title = page.title()
        cdp = ctx.new_cdp_session(page)
        mhtml = cdp.send('Page.captureSnapshot', {'format': 'mhtml'})['data']
        text = page.inner_text('body')
    finally:
        page.close()

    base = base_name(item)
    p_mhtml = OUT / f'{base}.mhtml'
    p_md = OUT / f'{base}.md'
    p_mhtml.write_text(mhtml, encoding='utf-8', newline='')
    head = [f'# {item.comment or title}', '',
            f'- Источник: {item.url}',
            f'- Заголовок страницы: {title}',
            f'- Получено: {TODAY}, браузером; полная страница с картинками — `{p_mhtml.name}`',
            '- Ниже — видимый текст страницы как есть, вместе с меню и подвалом сайта.',
            '', '---', '']
    p_md.write_text('\n'.join(head) + text.strip() + '\n', encoding='utf-8')
    return [p_md, p_mhtml]


# ── Прогон ───────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Скачать страницы по списку в source/web/.')
    ap.add_argument('list', nargs='?', type=Path, default=QUEUE, help='файл со списком адресов')
    ap.add_argument('--dry', action='store_true', help='только показать план')
    ap.add_argument('--force', action='store_true', help='перекачать уже скачанное')
    args = ap.parse_args()

    if not args.list.exists():
        args.list.write_text(QUEUE_HEADER, encoding='utf-8')
        sys.exit(f'Список пуст: {args.list}. Впиши адреса и запусти снова.')
    items = parse_queue(args.list)
    if not items:
        sys.exit(f'В {args.list} нет адресов.')

    OUT.mkdir(parents=True, exist_ok=True)
    done, failed, users, browser, api_blocked = [], [], {}, Browser(), False
    print(f'Адресов: {len(items)}. Куда: {OUT.relative_to(ROOT)}')
    try:
        for i, it in enumerate(items, 1):
            mode = 'page' if (it.mode == 'api' and api_blocked) else it.mode
            label = 'API BGG → .md' if mode == 'api' else 'браузер → .mhtml + .md'
            print(f'[{i}/{len(items)}] {it.url}  ({label})')
            old = existing(it)
            if old and not args.force:
                print(f'    уже есть: {old[-1].name} — пропуск (--force перекачает)')
                done.append(it.line)
                continue
            if args.dry:
                print(f'    → {base_name(it)}')
                continue
            try:
                if mode == 'api':
                    try:
                        files = fetch_thread(it, users)
                    except Blocked as e:
                        api_blocked = True
                        print(f'    {e}; дальше треды BGG — через браузер')
                        files = fetch_page(it, browser)
                else:
                    files = fetch_page(it, browser)
                for f in files:
                    print(f'    сохранено: {f.relative_to(ROOT)} ({f.stat().st_size // 1024} КБ)')
                done.append(it.line)
            except Exception as e:
                print(f'    НЕ СКАЧАНО: {e}')
                failed.append((it, str(e)))
    except KeyboardInterrupt:
        print('\nПрервано. Скачанное сохранено, остальное осталось в очереди.')
    finally:
        browser.close()
        if not args.dry:
            rewrite_queue(args.list, set(done))

    if args.dry:
        return
    print(f'\nГотово: {len(done)}, не скачано: {len(failed)}.')
    if failed:
        print('Сохранить руками (Ctrl+S → «Веб-страница, один файл») в source/web/:')
        for it, why in failed:
            print(f'  {it.url}  — {why}')


if __name__ == '__main__':
    main()
