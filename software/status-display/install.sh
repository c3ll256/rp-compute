#!/bin/sh
set -eu

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
target_dir=/opt/rp-compute/software/status-display
driver_dir=/opt/rp-compute/software/display-test

if [ "$(id -u)" -ne 0 ]; then
    echo 'Run this installer using sudo.' >&2
    exit 1
fi
python3 - "$source_dir/fonts/Inter.ttf" <<'PY'
import gpiod
import sys
from PIL import ImageFont
if not hasattr(gpiod, 'request_lines'):
    raise SystemExit('libgpiod 2.x is required')
face = ImageFont.truetype(sys.argv[1], 13)
face.set_variation_by_axes([14, 400])
PY
command -v dtc >/dev/null
command -v dtoverlay >/dev/null
command -v ip >/dev/null
for name in __init__.py bridge.py plugin.yaml; do
    test -r "$source_dir/hermes_display/$name"
done

systemctl stop rp-compute-display.service 2>/dev/null || true
install -d "$target_dir" "$driver_dir" "$target_dir/fonts"
install -d "$target_dir/hermes_display"
for name in status_display.py telemetry.py; do
    install -m 644 "$source_dir/$name" "$target_dir/$name"
done
for name in __init__.py bridge.py plugin.yaml; do
    install -m 644 "$source_dir/hermes_display/$name" "$target_dir/hermes_display/$name"
done
install -m 755 "$source_dir/prepare_display.sh" "$target_dir/prepare_display.sh"
install -m 644 "$source_dir/fonts/Inter.ttf" "$target_dir/fonts/Inter.ttf"
install -m 644 "$source_dir/fonts/OFL.txt" "$target_dir/fonts/OFL.txt"
install -m 644 "$source_dir/../display-test/display_test.py" "$driver_dir/display_test.py"
dtc -@ -I dts -O dtb -o "$target_dir/rp-lcd-test.dtbo" \
    "$source_dir/../display-test/rp-lcd-test-overlay.dts"
install -m 644 "$source_dir/rp-compute-display.service" \
    /etc/systemd/system/rp-compute-display.service
install -m 644 "$source_dir/rp-compute-display.conf" \
    /etc/modprobe.d/rp-compute-display.conf
systemctl daemon-reload
systemctl reenable rp-compute-display.service
systemctl start rp-compute-display.service
systemctl --no-pager --full status rp-compute-display.service
