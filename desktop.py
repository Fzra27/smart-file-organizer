"""Ubuntu desktop shell using GTK 3 and WebKitGTK (no external browser)."""
import threading
import secrets
import sys
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit
from app import Organizer, make_handler


def run(folder=None, port=0):
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('WebKit2', '4.1')
        from gi.repository import Gtk, WebKit2, Gdk, GLib
    except (ImportError, ValueError) as error:
        print('Masaüstü bileşenleri eksik / Desktop-Komponenten fehlen.\n'
              'Ubuntu: sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1\n'
              'Ardından / Danach: sh Baslat.sh', file=sys.stderr)
        return 1
    if not Gtk.init_check()[0]:
        print('Grafik oturumu bulunamadı / Keine grafische Sitzung.\n'
              'Sunucu modu / Server-Modus: sh Baslat.sh --no-browser', file=sys.stderr)
        return 1
    engine = Organizer(folder)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(engine, secrets.token_urlsafe(32)))
    except OSError as error:
        print(str(error) + '\nEski uygulamayı kapat / Alte Anwendung schließen; veya / oder: sh Baslat.sh --port 0', file=sys.stderr)
        return 1
    threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Thread(target=engine.watch, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'
    settings = Gtk.Settings.get_default()
    settings.set_property('gtk-application-prefer-dark-theme', True)
    window = Gtk.Window(title='Derli — Smart File Organizer')
    window.set_default_size(1200, 820)
    window.set_size_request(390, 540)
    view = WebKit2.WebView()
    background = Gdk.RGBA()
    background.parse('#11171d')
    view.set_background_color(background)
    view.get_settings().set_property('enable-developer-extras', False)
    # Only the local application may navigate inside the desktop window.
    def navigation(webview, decision, kind):
        if kind == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            uri = decision.get_navigation_action().get_request().get_uri()
            parsed = urlsplit(uri)
            if parsed.scheme != 'http' or parsed.netloc != urlsplit(base).netloc:
                decision.ignore()
                return True
        return False
    view.connect('decide-policy', navigation)
    view.connect('create', lambda *_: None)
    window.add(view)
    window.connect('destroy', lambda *_: Gtk.main_quit())
    view.load_uri(base)
    window.show_all()
    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    finally:
        engine.auto = False
        server.shutdown()
        server.server_close()
    return 0
