#!/bin/sh
set -eu

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target_dir=/opt/rp-compute/software/web-manager
if [ "$(id -u)" -ne 0 ]; then
    echo 'Run this installer using sudo.' >&2
    exit 1
fi
command -v tmux >/dev/null
test -r /opt/rp-compute/software/status-display/telemetry.py
test -r /opt/rp-compute/software/status-display/fonts/Inter.ttf
test -x /home/xonar/.local/bin/codex
python3 - "$source_dir" <<'PY'
import ast
import ctypes.util
from pathlib import Path
import sys
import yaml
import dbus
from gi.repository import GLib
if not ctypes.util.find_library('pam'):
    raise SystemExit('libpam is required')
for name in ('server.py', 'pam_auth.py', 'settings_client.py', 'settings_daemon.py', 'wifi_settings.py',
             'bluetooth_settings.py', 'clash_settings.py'):
    ast.parse((Path(sys.argv[1]) / name).read_text())
PY
systemctl stop makit-web.service 2>/dev/null || true
install -d "$target_dir"
install -m 644 "$source_dir/server.py" "$source_dir/pam_auth.py" "$target_dir/"
install -m 644 "$source_dir/settings_client.py" "$source_dir/settings_daemon.py" \
    "$source_dir/wifi_settings.py" "$source_dir/bluetooth_settings.py" "$source_dir/clash_settings.py" "$target_dir/"
install -d "$target_dir/static/vendor"
install -m 644 "$source_dir/static/index.html" "$source_dir/static/app.js" \
    "$source_dir/static/style.css" "$source_dir/static/settings.js" "$source_dir/static/clash.js" "$target_dir/static/"
install -m 644 "$source_dir/static/vendor/"* "$target_dir/static/vendor/"
install -m 644 "$source_dir/makit-web.service" /etc/systemd/system/makit-web.service
install -m 644 "$source_dir/makit-settings.service" /etc/systemd/system/makit-settings.service
systemctl daemon-reload
systemctl enable --now bluetooth.service avahi-daemon.service
systemctl enable makit-settings.service
systemctl restart makit-settings.service
systemctl enable --now makit-web.service
systemctl --no-pager --full status makit-web.service
