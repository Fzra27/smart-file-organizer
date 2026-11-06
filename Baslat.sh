#!/bin/sh
# Ubuntu / Linux launcher. No extra Python packages required.
set -eu
cd -- "$(dirname -- "$0")"
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Python 3 bulunamadı / Python 3 nicht gefunden.' >&2
    echo 'Ubuntu: sudo apt install python3' >&2
    exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo 'Python 3.10+ gerekli / Python 3.10+ erforderlich.' >&2
    exit 1
fi
exec python3 app.py "$@"
