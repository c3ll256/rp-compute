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
import evdev
import pyte
import sys
from pathlib import Path
from xkbcommon import xkb
from PIL import ImageFont
if not hasattr(gpiod, 'request_lines'):
    raise SystemExit('libgpiod 2.x is required')
face = ImageFont.truetype(sys.argv[1], 13)
face.set_variation_by_axes([14, 400])
ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf', 11)
ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 11)
ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', 11, index=2)
ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 11, index=2)
for weight in ('n', 'b'):
    path = Path(sys.argv[1]).parent / 'terminus' / f'ter-u14{weight}_unicode.otb'
    ImageFont.truetype(str(path), 14)
PY
command -v dtc >/dev/null
command -v dtoverlay >/dev/null
command -v ip >/dev/null

systemctl stop rp-compute-display.service 2>/dev/null || true
install -d "$target_dir" "$driver_dir" "$target_dir/fonts"
for name in status_display.py workroom.py codex_activity.py telemetry.py keyboard_input.py terminal_mode.py; do
    install -m 644 "$source_dir/$name" "$target_dir/$name"
done
install -m 755 "$source_dir/prepare_display.sh" "$target_dir/prepare_display.sh"
install -m 644 "$source_dir/fonts/Inter.ttf" "$target_dir/fonts/Inter.ttf"
install -m 644 "$source_dir/fonts/OFL.txt" "$target_dir/fonts/OFL.txt"
install -d "$target_dir/fonts/terminus"
install -m 644 "$source_dir/fonts/terminus/"* "$target_dir/fonts/terminus/"
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
