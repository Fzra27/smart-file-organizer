import json
import os
from pathlib import Path
import tempfile
import subprocess
import sys
import types
import selectors
from unittest.mock import patch, Mock
import threading
import time
import unittest
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer
from app import Organizer, make_handler, downloads_directory


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.app = Organizer(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def file(self, path, content=b'example'):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
        os.utime(p, (time.time()-60, time.time()-60))
        return p

    def test_preview_collision_and_undo(self):
        self.file('report.pdf', b'new')
        self.file('Belgeler/report.pdf', b'old')
        plan = self.app.preview('organize')
        self.assertTrue((self.root / 'report.pdf').exists())
        self.assertEqual(plan['moves'][0]['dst'], 'Belgeler/report (1).pdf')
        self.assertEqual(self.app.apply(plan['token'])['count'], 1)
        self.assertEqual((self.root / 'Belgeler/report.pdf').read_bytes(), b'old')
        result = self.app.undo(self.app.history()[0]['id'])
        self.assertEqual(result['count'], 1)
        self.assertEqual((self.root / 'report.pdf').read_bytes(), b'new')

    def test_duplicates_content_and_quarantine(self):
        self.file('a.txt', b'same')
        self.file('sub/b.txt', b'same')
        self.file('c.txt', b'else')
        scan = self.app.scan()
        self.assertEqual(len(scan['duplicates']), 1)
        self.assertEqual(scan['wasted'], 4)
        plan = self.app.preview('duplicates')
        self.assertEqual(self.app.apply(plan['token'])['count'], 1)
        self.assertEqual(self.app.scan()['count'], 2)
        self.assertEqual(self.app.undo(self.app.history()[0]['id'])['count'], 1)
        self.assertEqual(self.app.scan()['count'], 3)

    def test_changed_file_is_not_moved(self):
        p = self.file('a.pdf')
        plan = self.app.preview('organize')
        p.write_bytes(b'changed')
        result = self.app.apply(plan['token'])
        self.assertEqual(result['count'], 0)
        self.assertTrue(result['errors'])
        self.assertTrue(p.exists())

    def test_keep_copy_revalidated(self):
        self.file('a.txt', b'same')
        self.file('b.txt', b'same')
        plan = self.app.preview('duplicates')
        (self.root / plan['moves'][0]['keep']).write_bytes(b'changed')
        self.assertEqual(self.app.apply(plan['token'])['count'], 0)
        self.assertTrue((self.root / plan['moves'][0]['src']).exists())

    def test_undo_never_overwrites(self):
        self.file('a.pdf')
        self.app.apply(self.app.preview('organize')['token'])
        self.file('a.pdf', b'do not overwrite')
        result = self.app.undo(self.app.history()[0]['id'])
        self.assertTrue(result['errors'])
        self.assertEqual((self.root / 'a.pdf').read_bytes(), b'do not overwrite')
        self.assertTrue((self.root / 'Belgeler/a.pdf').exists())

    def test_symlinks_and_downloads_skipped(self):
        self.file('pending.crdownload')
        self.file('.hidden')
        p = self.file('a.pdf')
        os.utime(p, None)
        (self.root / 'alias.pdf').symlink_to(p)
        self.assertEqual(self.app.scan()['count'], 1)
        self.assertEqual(self.app.preview('organize')['moves'], [])
        with self.assertRaises(ValueError):
            self.app.safe('../outside')

    def test_symlink_destination_rejected(self):
        self.file('a.pdf')
        with tempfile.TemporaryDirectory() as outside:
            (self.root / 'Belgeler').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.app.preview('organize')
            self.assertTrue((self.root / 'a.pdf').exists())

    def test_auto_opt_in_and_manual_preview(self):
        self.file('a.pdf')
        self.app.auto_tick()
        self.assertTrue((self.root / 'a.pdf').exists())
        plan = self.app.preview('organize')
        self.app.auto = True
        self.app.auto_tick()
        self.assertEqual(self.app.plan['token'], plan['token'])
        self.assertTrue((self.root / 'a.pdf').exists())
        self.app.plan = None
        self.app.auto_tick()
        self.assertTrue((self.root / 'Belgeler/a.pdf').exists())
        self.assertTrue(self.app.history())

    def test_xdg_download_directory(self):
        config = self.root / 'config'
        config.mkdir()
        dirs = config / 'user-dirs.dirs'
        dirs.write_text('XDG_DOWNLOAD_DIR="$HOME/İndirilenler ä"\n', encoding='utf-8')
        with patch('app.Path.home', return_value=self.root), patch.dict(os.environ, {'XDG_CONFIG_HOME': str(config)}):
            self.assertEqual(downloads_directory(), self.root / 'İndirilenler ä')
            dirs.write_text('XDG_DOWNLOAD_DIR="relative/path"\n', encoding='utf-8')
            self.assertEqual(downloads_directory(), self.root / 'Downloads')
            dirs.write_text('XDG_DOWNLOAD_DIR="unterminated\n', encoding='utf-8')
            self.assertEqual(downloads_directory(), self.root / 'Downloads')

    @unittest.skipUnless(os.name == 'posix', 'Linux/macOS launcher test')
    def test_linux_launcher_and_assets(self):
        folder = self.root / 'İndirilenler ä'
        folder.mkdir()
        launcher = Path(__file__).resolve().parent / 'Baslat.sh'
        process = subprocess.Popen(['sh', str(launcher), '--no-browser', '--port', '0', '--folder', str(folder)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                   env={**os.environ, 'PYTHONUNBUFFERED': '1'})
        selector = selectors.DefaultSelector()
        try:
            selector.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(selector.select(timeout=10), 'Launcher did not start within 10 seconds')
            line = process.stdout.readline()
            self.assertIn('http://127.0.0.1:', line)
            base = line.split('http://', 1)[1].strip()
            for path, marker in [('/', 'id="language"'), ('/i18n.js', 'Sprache')]:
                with urllib.request.urlopen('http://' + base + path) as response:
                    self.assertIn(marker, response.read().decode('utf-8'))
        finally:
            selector.close()
            process.terminate()
            process.communicate(timeout=10)

    def test_default_launch_uses_desktop_without_browser(self):
        import app
        run = Mock(return_value=0)
        fake = types.ModuleType('desktop')
        fake.run = run
        with patch.dict(sys.modules, {'desktop': fake}), patch.object(sys, 'argv', ['app.py']), patch('app.webbrowser.open') as browser:
            with self.assertRaises(SystemExit) as result:
                app.main()
            self.assertEqual(result.exception.code, 0)
            run.assert_called_once_with(None, 8765)
            browser.assert_not_called()

    def test_desktop_menu_entry(self):
        import install_desktop
        with patch.dict(os.environ, {'XDG_DATA_HOME': str(self.root / 'menu data')}):
            install_desktop.install()
            entry = self.root / 'menu data/applications/derli.desktop'
            text = entry.read_text('utf-8')
            self.assertIn('Terminal=false', text)
            self.assertIn('Exec=/usr/bin/python3 "', text)
            self.assertNotIn('--browser', text)

    def test_http_session_protection(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(self.app, 'test-token'))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with urllib.request.urlopen(base) as response:
                self.assertIn(b'test-token', response.read())
            req = urllib.request.Request(base+'/api/scan', data=b'{}', headers={'Content-Type':'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(req)
            self.assertEqual(error.exception.code, 403)
            req.add_header('X-App-Token', 'test-token')
            with urllib.request.urlopen(req) as response:
                self.assertEqual(json.load(response)['count'], 0)
            req = urllib.request.Request(base+'/api/scan', data=b'{}', headers={'X-App-Token':'test-token', 'Host':'attacker.example'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(req)
            self.assertEqual(error.exception.code, 403)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
