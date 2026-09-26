"""Уборка проекта: лишнее — в archive/, мусор — удалить насовсем.

    python rules/tools/cleanup.py          # убрать
    python rules/tools/cleanup.py --dry    # только показать, что будет сделано

Что убирается:

1. Очередь `rules/tools/cleanup-queue.txt` — по строке на путь от корня
   проекта, можно маски (`print/icons/oil-barrel-?.svg`). Каждая строка
   начинается с действия:
       архив: путь     — может пригодиться: переносится в
                         archive/уборка-ГГГГ-ММ-ДД/<тот же путь>
       удалить: путь   — точно мусор: удаляется насовсем, без Корзины
   Сюда пишет Claude: у него нет команды удаления на этом компьютере.
   После уборки выполненные строки из очереди стираются, отказанные остаются.
2. Служебный мусор по всему проекту, удаляется насовсем: `__pycache__/`,
   `*.pyc`, `*.tmp`, `Thumbs.db`, `.DS_Store`, файлы блокировки Office `~$*`.

Защита — чтобы не потерять нужное:

- «удалить:» — только НОВЫЕ файлы: не в истории git и не в .gitignore.
  Файл из истории лучше «архив:» — после переноса git покажет его удалённым,
  и это видно в коммите.
- «архив:» — новые файлы и файлы из истории.
- Игнорируемое (`archive/`, `board/legacy/`, рулбуки оригинала) — единственные
  экземпляры, скрипт не трогает их никогда: ни удалить, ни перенести.
- Только внутри проекта, `.git/` не трогается.

Зависимости: только git в PATH.
"""
import argparse, datetime, fnmatch, os, shutil, stat, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = Path(__file__).resolve().with_name('cleanup-queue.txt')
ARCHIVE = ROOT / 'archive' / f'уборка-{datetime.date.today():%Y-%m-%d}'
JUNK_DIRS = {'__pycache__'}
JUNK_FILES = ['*.pyc', '*.tmp', 'Thumbs.db', '.DS_Store', '~$*']
ACTIONS = {'архив': 'archive', 'удалить': 'delete'}

GONE = 'не найден — уже убран, строка снята из очереди'
QUEUE_HEADER = """\
# Очередь уборки для rules/tools/cleanup.py. Путь от корня проекта, маски * и ?.
#   архив: путь     — может пригодиться → archive/уборка-ДАТА/<тот же путь>
#   удалить: путь   — точно мусор → удаляется насовсем (только новые файлы)
# Выполненные строки стираются; то, что сделать отказались, остаётся.
"""


def git_files(*args):
    try:
        out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', *args],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as e:
        sys.exit(f'git недоступен, уборка отменена: {e}')
    return {p for p in out.decode('utf-8').split('\0') if p}


def rel(p: Path):
    return p.relative_to(ROOT).as_posix()


def delete(p: Path):
    def unlock(func, path, _):                  # файлы «только чтение» на Windows
        os.chmod(path, stat.S_IWRITE); func(path)
    shutil.rmtree(p, onerror=unlock) if p.is_dir() else (os.chmod(p, stat.S_IWRITE), p.unlink())


def to_archive(p: Path):
    dest = ARCHIVE / rel(p)
    n = 2
    while dest.exists():                        # не затирать уже архивированное
        dest = dest.with_name(f'{p.stem} ({n}){p.suffix}'); n += 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), str(dest))
    return rel(dest)


def read_queue():
    if not QUEUE.exists():
        return []
    return [l.strip() for l in QUEUE.read_text(encoding='utf-8').splitlines()
            if l.strip() and not l.lstrip().startswith('#')]


def from_queue(entries, new, tracked):
    """→ [(путь, действие, строка)] к выполнению и [(строка, причина)] отказов."""
    ok, refused = [], []
    for e in entries:
        act, _, pat = e.partition(':')
        act = ACTIONS.get(act.strip().lower())
        if not act or not pat.strip():
            refused.append((e, 'нет действия: строка должна начинаться с «архив:» или «удалить:»'))
            continue
        pat = pat.strip().replace('\\', '/').strip('/')
        if '..' in pat.split('/') or ':' in pat or Path(pat).is_absolute():
            refused.append((e, 'путь вне проекта')); continue
        hits = sorted(ROOT.glob(pat)) if any(c in pat for c in '*?[') else [ROOT / pat]
        hits = [h for h in hits if h.exists()]
        if not hits:
            refused.append((e, GONE)); continue
        allowed = new if act == 'delete' else new | tracked
        for h in hits:
            r = rel(h)
            if r == '.git' or r.startswith('.git/') or r == 'archive' or r.startswith('archive/'):
                refused.append((e, f'{r}: .git и archive/ не трогаем')); continue
            files = [rel(f) for f in h.rglob('*') if f.is_file()] if h.is_dir() else [r]
            bad = [f for f in files if f not in allowed]
            if bad:
                why = ('в истории git — используйте «архив:»' if act == 'delete' and bad[0] in tracked
                       else 'в .gitignore — единственный экземпляр, не трогаем')
                refused.append((e, f'{bad[0]}: {why}'))
            else:
                ok.append((h, act, e))
    return ok, refused


def junk(tracked):
    found = []
    for dirpath, dirs, files in os.walk(ROOT):
        d = Path(dirpath)
        if d == ROOT:
            dirs[:] = [x for x in dirs if x != '.git']
        for x in list(dirs):
            if x in JUNK_DIRS:
                found.append(d / x); dirs.remove(x)
        found += [d / f for f in files if any(fnmatch.fnmatch(f, m) for m in JUNK_FILES)]
    return [p for p in found if rel(p) not in tracked]


def main():
    sys.stdout.reconfigure(errors='replace')
    ap = argparse.ArgumentParser(description='Уборка: лишнее в archive/, мусор удалить.')
    ap.add_argument('--dry', action='store_true', help='только показать')
    a = ap.parse_args()

    entries = read_queue()
    tracked = git_files()
    new = git_files('--others', '--exclude-standard')
    todo, refused = from_queue(entries, new, tracked)
    seen = {p for p, _, _ in todo}
    todo += [(p, 'delete', None) for p in junk(tracked) if p not in seen]

    if not todo and not refused:
        print('Чисто, убирать нечего.')
        return
    failed, done = [], {'archive': 0, 'delete': 0}
    for p, act, line in todo:
        r = rel(p)
        if a.dry:
            print(f'  {"в архив" if act == "archive" else "удалить"}  {r}')
            done[act] += 1
            continue
        try:
            if act == 'archive':
                print(f'  в архив  {r}  →  {to_archive(p)}')
            else:
                delete(p); print(f'  удалено  {r}')
            done[act] += 1
        except OSError as e:
            failed.append((line or r, f'{r}: {e}'))
    for line, why in refused + failed:
        print(f'  ОТКАЗ  {line} — {why}')

    head = 'Будет' if a.dry else 'Итого'
    print(f'{head}: в архив {done["archive"]}, удалено {done["delete"]}, '
          f'отказов {len(refused) + len(failed)}.')
    if not a.dry and QUEUE.exists():
        keep = dict.fromkeys(line for line, why in refused + failed
                             if line in entries and why != GONE)
        QUEUE.write_text(QUEUE_HEADER + ''.join(f'{k}\n' for k in keep), encoding='utf-8')


if __name__ == '__main__':
    main()
