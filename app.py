#!/usr/bin/env python3
"""Akıllı Dosya Düzenleyici — yalnızca Python standart kütüphanesi."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import shutil
import stat
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

GROUPS = {
    'Belgeler': 'pdf doc docx txt rtf odt xls xlsx csv ppt pptx epub md',
    'Görseller': 'jpg jpeg png gif webp svg bmp heic tiff ico raw',
    'Videolar': 'mp4 mov mkv avi webm m4v mpg',
    'Müzikler': 'mp3 wav flac aac ogg m4a',
    'Arşivler': 'zip rar 7z tar gz bz2 xz',
    'Uygulamalar': 'exe msi dmg pkg deb rpm appimage',
    'Kod': 'py js ts jsx tsx html css json yaml yml sql ipynb sh',
}
EXTENSIONS = {ext: group for group, extensions in GROUPS.items() for ext in extensions.split()}
INTERNAL = '.akilli-duzenleyici'
TEMP = {'.part', '.crdownload', '.download', '.tmp', '.temp'}


def downloads_directory():
    """Read the freedesktop XDG download directory without executing shell code."""
    home = Path.home()
    config_home = Path(os.environ.get('XDG_CONFIG_HOME') or home / '.config')
    if not config_home.is_absolute():
        config_home = home / '.config'
    try:
        for line in (config_home / 'user-dirs.dirs').read_text('utf-8').splitlines():
            name, sep, value = line.partition('=')
            if sep and name.strip() == 'XDG_DOWNLOAD_DIR':
                parts = shlex.split(value, comments=True)
                if len(parts) == 1:
                    configured = Path(parts[0].replace('${HOME}', str(home)).replace('$HOME', str(home)))
                    if configured.is_absolute():
                        return configured
    except (OSError, ValueError):
        pass
    return home / 'Downloads'


def category(path):
    return EXTENSIONS.get(path.suffix.lower().lstrip('.'), 'Diğer')


def signature(path):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode):
        raise ValueError('Normal bir dosya değil: ' + path.name)
    return [s.st_size, s.st_mtime_ns, s.st_ino, s.st_dev]


def digest(path):
    before = signature(path)
    h = hashlib.sha256()
    # O_NOFOLLOW prevents following a symlink swapped in during a scan on Unix.
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as f:
        s = os.fstat(f.fileno())
        if [s.st_size, s.st_mtime_ns, s.st_ino, s.st_dev] != before:
            raise ValueError('Tarama sırasında dosya değişti: ' + path.name)
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    if signature(path) != before:
        raise ValueError('Tarama sırasında dosya değişti: ' + path.name)
    return h.hexdigest()


class Organizer:
    def __init__(self, root=None):
        self.lock = threading.RLock()
        self.root = None
        self.auto = False
        self.plan = None
        self.last_auto = ''
        if root:
            self.set_root(root)

    def set_root(self, value):
        with self.lock:
            p = Path(value).expanduser().resolve(strict=True)
            if not p.is_dir() or p == Path(p.anchor):
                raise ValueError('Bir çalışma klasörü seçin; disk kökü seçilemez.')
            self.auto = False
            self.root, self.plan = p, None
            return str(p)

    def require_root(self):
        if self.root is None:
            raise ValueError('Önce klasör yolunu girin.')

    def safe(self, relative):
        self.require_root()
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts:
            raise ValueError('Geçersiz dosya yolu.')
        p = self.root
        for part in rel.parts:
            p = p / part
            if p.is_symlink():
                raise ValueError('Sembolik bağlantılar işlenmez: ' + str(relative))
        return p

    def scan(self):
        with self.lock:
            self.require_root()
            files, errors = [], []
            def onerror(e):
                errors.append(str(e))
            for folder, dirs, names in os.walk(self.root, followlinks=False, onerror=onerror):
                dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not (Path(folder) / d).is_symlink())
                for name in sorted(names):
                    p = Path(folder) / name
                    if name.startswith('.') or p.suffix.lower() in TEMP or p.is_symlink():
                        continue
                    try:
                        s = signature(p)
                        files.append({'path': str(p.relative_to(self.root)), 'name': name,
                                      'size': s[0], 'mtime': p.stat().st_mtime,
                                      'category': category(p), 'signature': s})
                    except (OSError, ValueError) as e:
                        errors.append(str(e))
            sizes = {}
            for f in files:
                sizes.setdefault(f['size'], []).append(f)
            duplicates = []
            for candidates in sizes.values():
                if len(candidates) < 2:
                    continue
                hashes = {}
                for f in candidates:
                    try:
                        p = self.safe(f['path'])
                        h = digest(p)
                        if signature(p) != f['signature']:
                            raise ValueError('Dosya değişti: ' + f['name'])
                        hashes.setdefault(h, []).append(f)
                    except (OSError, ValueError) as e:
                        errors.append(str(e))
                for h, group in hashes.items():
                    if len(group) > 1:
                        group.sort(key=lambda f: (f['mtime'], f['path']))
                        duplicates.append({'hash': h, 'files': group, 'wasted': group[0]['size'] * (len(group)-1)})
            totals = {}
            for f in files:
                t = totals.setdefault(f['category'], {'size': 0, 'count': 0})
                t['size'] += f['size']
                t['count'] += 1
            disk = shutil.disk_usage(self.root)
            return {'root': str(self.root), 'files': files, 'count': len(files),
                    'size': sum(f['size'] for f in files), 'categories': totals,
                    'largest': sorted(files, key=lambda f: f['size'], reverse=True)[:15],
                    'duplicates': duplicates, 'wasted': sum(g['wasted'] for g in duplicates),
                    'disk': {'total': disk.total, 'used': disk.used, 'free': disk.free},
                    'auto': self.auto, 'last_auto': self.last_auto, 'errors': errors,
                    'history': self.history()}

    def history(self):
        folder = self.safe(INTERNAL + '/history')
        if not folder.exists():
            return []
        results = []
        for p in sorted(folder.glob('*.json'), reverse=True)[:30]:
            try:
                if p.is_symlink():
                    continue
                j = json.loads(p.read_text('utf-8'))
                results.append({'id': p.stem, 'label': j['label'], 'time': j['time'],
                                'count': len(j['moves']), 'undone': j.get('undone', False)})
            except (OSError, ValueError, KeyError):
                continue
        return results

    def preview(self, kind):
        with self.lock:
            data = self.scan()
            moves = []
            if kind == 'organize':
                for f in data['files']:
                    if len(Path(f['path']).parts) == 1 and time.time() - f['mtime'] >= 10:
                        moves.append({'src': f['path'], 'dst': f['category'] + '/' + f['name'],
                                      'signature': f['signature']})
            elif kind == 'duplicates':
                for g in data['duplicates']:
                    for f in g['files'][1:]:
                        moves.append({'src': f['path'], 'dst': INTERNAL + '/karantina/' + f['path'],
                                      'signature': f['signature'], 'hash': g['hash'],
                                      'keep': g['files'][0]['path']})
            else:
                raise ValueError('Geçersiz işlem.')
            reserved = set()
            for m in moves:
                target = Path(m['dst'])
                i = 1
                while self.safe(str(target)).exists() or str(target) in reserved:
                    target = Path(m['dst']).with_name(Path(m['dst']).stem + f' ({i})' + Path(m['dst']).suffix)
                    i += 1
                m['dst'] = str(target)
                reserved.add(str(target))
            token = secrets.token_urlsafe(24)
            self.plan = {'token': token, 'moves': moves, 'kind': kind, 'time': time.time()}
            return self.plan

    def write_journal(self, batch, data):
        folder = self.safe(INTERNAL + '/history')
        folder.mkdir(parents=True, exist_ok=True)
        target = self.safe(INTERNAL + '/history/' + batch + '.json')
        tmp = self.safe(INTERNAL + '/history/' + batch + '.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, target)

    def move(self, src, dst, expected_hash):
        source, target = self.safe(src), self.safe(dst)
        target.parent.mkdir(parents=True, exist_ok=True)
        self.safe(dst)
        # Hard links are atomic and fail if the destination already exists.
        # All destinations are on the selected filesystem; no overwriting.
        os.link(source, target, follow_symlinks=False)
        try:
            if digest(target) != expected_hash or digest(source) != expected_hash:
                raise ValueError('Taşıma sırasında dosya değişti: ' + src)
            source.unlink()
        except Exception:
            target.unlink(missing_ok=True)
            raise

    def apply(self, token):
        with self.lock:
            plan = self.plan
            if not plan or token != plan['token'] or time.time() - plan['time'] > 300:
                raise ValueError('Önizleme süresi doldu. Yeniden önizleyin.')
            self.plan = None
            batch = time.strftime('%Y%m%d-%H%M%S') + '-' + secrets.token_hex(4)
            journal = {'label': 'Klasörü düzenle' if plan['kind'] == 'organize' else 'Kopyaları karantinaya taşı',
                       'time': time.time(), 'moves': [], 'undone': False}
            errors, count = [], 0
            for m in plan['moves']:
                try:
                    source = self.safe(m['src'])
                    if signature(source) != m['signature']:
                        raise ValueError('Dosya değişti; atlandı: ' + m['src'])
                    h = digest(source)
                    if 'keep' in m and (h != m['hash'] or digest(self.safe(m['keep'])) != h):
                        raise ValueError('Kopya doğrulanamadı; atlandı: ' + m['src'])
                    record = {'src': m['src'], 'dst': m['dst'], 'hash': h, 'status': 'planned'}
                    journal['moves'].append(record)
                    self.write_journal(batch, journal)
                    self.move(m['src'], m['dst'], h)
                    record['status'] = 'done'
                    count += 1
                    self.write_journal(batch, journal)
                except (OSError, ValueError) as e:
                    errors.append(str(e))
            return {'count': count, 'errors': errors}

    def undo(self, batch):
        with self.lock:
            if not batch or any(c not in '0123456789abcdef-' for c in batch):
                raise ValueError('Geçersiz işlem kimliği.')
            j = json.loads(self.safe(INTERNAL + '/history/' + batch + '.json').read_text('utf-8'))
            errors, count = [], 0
            for m in reversed(j['moves']):
                if m.get('status') == 'undone':
                    continue
                try:
                    source, dest = self.safe(m['src']), self.safe(m['dst'])
                    if not dest.exists() and source.exists() and m['status'] == 'planned':
                        m['status'] = 'undone'
                    else:
                        if source.exists():
                            raise ValueError('İlk konum dolu; üzerine yazılmadı: ' + m['src'])
                        if digest(dest) != m['hash']:
                            raise ValueError('Dosya değişmiş; geri alınmadı: ' + m['dst'])
                        self.move(m['dst'], m['src'], m['hash'])
                        m['status'] = 'undone'
                        count += 1
                    self.write_journal(batch, j)
                except (OSError, ValueError) as e:
                    errors.append(str(e))
            j['undone'] = all(m.get('status') == 'undone' for m in j['moves'])
            self.write_journal(batch, j)
            return {'count': count, 'errors': errors}

    def auto_tick(self):
        with self.lock:
            if not self.auto or not self.root:
                return
            try:
                # An open manual preview must not be replaced by the watcher.
                if self.plan and time.time() - self.plan['time'] < 300:
                    return
                p = self.preview('organize')
                result = self.apply(p['token']) if p['moves'] else {'count': 0, 'errors': []}
                self.plan = None
                self.last_auto = time.strftime('%H:%M:%S') + ' · ' + str(result['count']) + ' dosya düzenlendi'
                if result['errors']:
                    self.last_auto += ' · ' + result['errors'][0]
            except (OSError, ValueError) as e:
                self.last_auto = str(e)

    def watch(self):
        while True:
            time.sleep(15)
            self.auto_tick()


ASSETS = Path(__file__).parent / 'static'


def make_handler(engine, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, content, mime='application/json; charset=utf-8'):
            data = content.encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)

        def valid_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

        def do_GET(self):
            if not self.valid_host():
                return self.send(403, '{}')
            routes = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8'), '/i18n.js': ('i18n.js', 'text/javascript; charset=utf-8')}
            if self.path not in routes:
                return self.send(404, '{}')
            file, mime = routes[self.path]
            content = (ASSETS / file).read_text('utf-8')
            if file == 'index.html':
                content = content.replace('__TOKEN__', token)
            self.send(200, content, mime)

        def do_POST(self):
            if not self.valid_host() or self.headers.get('X-App-Token') != token:
                return self.send(403, json.dumps({'error': 'Yerel oturum doğrulanamadı.'}))
            try:
                length = int(self.headers.get('Content-Length', 0))
                if not 0 < length < 16384:
                    raise ValueError('Geçersiz istek boyutu.')
                data = json.loads(self.rfile.read(length))
                with engine.lock:
                    if self.path == '/api/status':
                        result = {'root': str(engine.root) if engine.root else '', 'suggested': str(downloads_directory()), 'auto': engine.auto}
                    elif self.path == '/api/root':
                        result = {'root': engine.set_root(data['path'])}
                    elif self.path == '/api/scan':
                        result = engine.scan()
                    elif self.path == '/api/preview':
                        result = engine.preview(data['kind'])
                    elif self.path == '/api/apply':
                        result = engine.apply(data['token'])
                    elif self.path == '/api/undo':
                        result = engine.undo(data['id'])
                    elif self.path == '/api/auto':
                        engine.require_root()
                        engine.auto = bool(data['enabled'])
                        result = {'auto': engine.auto}
                    else:
                        return self.send(404, '{}')
                self.send(200, json.dumps(result, ensure_ascii=False))
            except (OSError, ValueError, KeyError, TypeError) as e:
                self.send(400, json.dumps({'error': str(e)}, ensure_ascii=False))
    return Handler


def main():
    parser = argparse.ArgumentParser(description='Akıllı Dosya Düzenleyici')
    parser.add_argument('--folder', help='Düzenlenecek klasör')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    engine = Organizer(args.folder)
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(engine, secrets.token_urlsafe(32)))
    threading.Thread(target=engine.watch, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Akıllı Dosya Düzenleyici: {url}\nDurdurmak için Ctrl+C. Otomatik düzenleme başlangıçta kapalıdır.')
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
