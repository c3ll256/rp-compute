#!/bin/sh
set -eu

base_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
driver=/sys/bus/platform/drivers/spi-bcm2835
device=fe204000.spi

if [ "$(id -u)" -ne 0 ]; then
    echo 'Display preparation needs root access.' >&2
    exit 1
fi
if [ ! -e "$driver/$device" ]; then
    echo 'Expected Raspberry Pi 4 SPI0 controller is unavailable.' >&2
    exit 1
fi

needs_polarity=$(python3 - <<'PY'
import gpiod
with gpiod.Chip('/dev/gpiochip0') as chip:
    if chip.get_info().label not in ('pinctrl-bcm2711', 'pinctrl-bcm2835'):
        raise SystemExit('Unexpected GPIO controller')
    print(int(chip.get_line_info(8).active_low))
PY
)

if [ "$needs_polarity" -eq 1 ]; then
    # dtoverlay's /tmp cache can survive a reboot after the live overlay is lost.
    if [ ! -e /proc/device-tree/soc/spi@7e204000/spidev@0/spi-cs-high ]; then
        dtoverlay -d "$base_dir" rp-lcd-test
    fi
    printf '%s' "$device" > "$driver/unbind"
    # Restore binding even if a later shell operation fails.
    trap 'printf "%s" "$device" > "$driver/bind" || true' EXIT
    printf '%s' "$device" > "$driver/bind"
    trap - EXIT
fi

if [ ! -r /sys/module/spidev/parameters/bufsiz ]; then
    modprobe spidev bufsiz=16384
fi
buffer_size=$(cat /sys/module/spidev/parameters/bufsiz)
if [ "$buffer_size" -lt 12482 ]; then
    modprobe -r spidev
    modprobe spidev bufsiz=16384
fi
buffer_size=$(cat /sys/module/spidev/parameters/bufsiz)
if [ "$buffer_size" -lt 12482 ]; then
    echo "SPI buffer is still too small: $buffer_size" >&2
    exit 1
fi

python3 - <<'PY'
import gpiod
with gpiod.Chip('/dev/gpiochip0') as chip:
    if chip.get_line_info(8).active_low:
        raise SystemExit('LCD chip select is still active-low')
PY
