#!/bin/sh
# Run once on your Ubuntu computer to install the native window dependencies.
set -eu
sudo apt-get install python3 python3-gi gir1.2-gtk-3.0 gir1.2-webkit2-4.1
printf '\nHazır / Bereit: sh Baslat.sh\n'
cd -- "$(dirname -- "$0")"
/usr/bin/python3 install_desktop.py
