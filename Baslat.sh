#!/bin/sh
# Ubuntu / Linux desktop launcher (GTK + WebKitGTK).
set -eu
cd -- "$(dirname -- "$0")"
derli_python=python3
# Ubuntu GI packages belong to the system Python.
if [ -x /usr/bin/python3 ]; then derli_python=/usr/bin/python3; fi
if ! command -v "$derli_python" >/dev/null 2>&1; then
    echo 'Python 3 bulunamadı / Python 3 nicht gefunden.' >&2
    echo 'Ubuntu: sudo apt install python3' >&2
    exit 1
fi
if ! "$derli_python" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo 'Python 3.10+ gerekli / Python 3.10+ erforderlich.' >&2
    exit 1
fi
exec "$derli_python" app.py "$@"
