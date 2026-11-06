"""Install a per-user Ubuntu application menu entry after dependencies are installed."""
import os
from pathlib import Path


def install():
    root = Path(__file__).resolve().parent
    data = Path(os.environ.get('XDG_DATA_HOME') or Path.home() / '.local/share')
    if not data.is_absolute():
        data = Path.home() / '.local/share'
    target = data / 'applications' / 'derli.desktop'
    target.parent.mkdir(parents=True, exist_ok=True)
    def quote(value):
        escaped = str(value)
        for char in ('\\', '"', '`', '$'):
            escaped = escaped.replace(char, '\\' + char)
        return '"' + escaped.replace('%', '%%') + '"'
    target.write_text('[Desktop Entry]\nType=Application\nName=Derli\n'
                      'Comment=Smart File Organizer\n'
                      'Exec=/usr/bin/python3 ' + quote(root / 'app.py') + '\n'
                      'Icon=system-file-manager\nTerminal=false\nCategories=Utility;FileTools;\n', encoding='utf-8')
    target.chmod(0o644)
    print('Uygulamalar menüsüne eklendi / Zum Anwendungsmenü hinzugefügt: Derli')


if __name__ == '__main__':
    install()
