#!/usr/bin/env python3
"""Bring-up patterns for the rp-compute LS027B7DH01 / LS027B7DH01A."""

import argparse
import ctypes
import fcntl
from functools import lru_cache
import logging
import math
import os
from pathlib import Path
import signal
import struct
import threading
import time

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 400, 240
COM, FAULT, POWER, DISP = 12, 16, 24, 25  # BCM GPIO numbering
REVERSED = bytes(int(f"{value:08b}"[::-1], 2) for value in range(256))
LOG = logging.getLogger("rp-lcd-test")


@lru_cache(maxsize=3)
def font(size):
    return ImageFont.load_default(size=size)


def frame_packets(image, rows_per_packet=60):
    """MSB-first SPI bytes, with Sharp command/address bytes bit-reversed."""
    if image.mode != "1" or image.size != (WIDTH, HEIGHT):
        raise ValueError("Expected a 400x240 mode-1 image")
    if not 1 <= rows_per_packet <= HEIGHT:
        raise ValueError("rows_per_packet must be between 1 and 240")
    pixels = image.tobytes()
    # 60 rows fit 4096 bytes. Full-frame transfers need a 16384-byte buffer.
    for start in range(0, HEIGHT, rows_per_packet):
        packet = bytearray([0x80])  # M0=1 is the first bit on the wire.
        for row in range(start, min(start + rows_per_packet, HEIGHT)):
            packet.append(REVERSED[row + 1])
            # PIL packs the leftmost pixel into bit 7. 1 means white.
            packet.extend(pixels[row * 50:(row + 1) * 50])
            packet.append(0)
        packet.append(0)
        yield bytes(packet)


class SpiTransfer(ctypes.Structure):
    """Linux uapi struct spi_ioc_transfer (32 bytes on 32/64-bit hosts)."""

    _fields_ = [
        ("tx_buf", ctypes.c_uint64), ("rx_buf", ctypes.c_uint64),
        ("length", ctypes.c_uint32), ("speed_hz", ctypes.c_uint32),
        ("delay_usecs", ctypes.c_uint16), ("bits_per_word", ctypes.c_uint8),
        ("cs_change", ctypes.c_uint8), ("tx_nbits", ctypes.c_uint8),
        ("rx_nbits", ctypes.c_uint8), ("word_delay_usecs", ctypes.c_uint8),
        ("pad", ctypes.c_uint8),
    ]


class Display:
    def __init__(self, fps=2, spi_hz=None):
        import gpiod
        from gpiod.line import Direction, Value

        self.low, self.high = Value.INACTIVE, Value.ACTIVE
        self.fd = None
        self.lines = None
        self.clock_stop = threading.Event()
        self.clock_thread = None
        self.clock_error = None
        self.powered = False
        self.last_transfer = 0.0
        self.frames = 0
        self.transfers = 0
        self.com_edges = 0
        self.max_com_gap = 0.0
        self.rows_per_packet = 240 if fps > 2 else 60
        self.speed_hz = spi_hz or (2_000_000 if fps > 2 else 1_000_000)
        self.minimum_interval = 0.050 if fps > 2 else 0.060
        if fps > 20:
            self.speed_hz = spi_hz or 10_000_000
            self.minimum_interval = 0.000001
        if fps > 20 or self.speed_hz > 2_000_000:
            LOG.warning("Experimental timing, target %.1f Hz, SPI %.1f MHz. "
                        "Published Sharp timing range is up to 20 Hz / 2 MHz.",
                        fps, self.speed_hz / 1_000_000)
        required_buffer = 2 + self.rows_per_packet * 52
        buffer_size = int(Path("/sys/module/spidev/parameters/bufsiz").read_text())
        if buffer_size < required_buffer:
            raise RuntimeError(
                f"SPI buffer {buffer_size} is smaller than {required_buffer} bytes. "
                "Stop SPI users, then run sudo modprobe -r spidev && "
                "sudo modprobe spidev bufsiz=16384")
        with gpiod.Chip("/dev/gpiochip0") as chip:
            info = chip.get_info()
            if info.label not in ("pinctrl-bcm2835", "pinctrl-bcm2711"):
                raise RuntimeError(f"Unexpected GPIO controller {info.label}")
            if chip.get_line_info(8).active_low:
                raise RuntimeError("GPIO8 SCS needs the supplied active-high overlay")
        self.lines = gpiod.request_lines(
            "/dev/gpiochip0", consumer="rp-lcd-test",
            config={
                (COM, POWER, DISP): gpiod.LineSettings(
                    direction=Direction.OUTPUT, output_value=self.low),
                FAULT: gpiod.LineSettings(direction=Direction.INPUT),
            },
        )
        try:
            self.fd = os.open("/dev/spidev0.0", os.O_RDWR | os.O_CLOEXEC)
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            # GPIO-CS polarity is set by device tree on modern kernels.
            fcntl.ioctl(self.fd, 0x40016B01, bytes([0]))  # mode 0, MSB first
            fcntl.ioctl(self.fd, 0x40016B03, bytes([8]))  # 8-bit words
            fcntl.ioctl(self.fd, 0x40046B04, struct.pack("=I", self.speed_hz))
        except BaseException:
            self.close()
            raise

    def transfer(self, packet):
        # Standard timing uses 50-ms frame intervals. Experimental high-rate
        # operation is paced by the main loop and keeps SCS inactive >= 1 us.
        time.sleep(max(0, self.last_transfer + self.minimum_interval - time.monotonic()))
        payload = ctypes.create_string_buffer(packet)
        transfers = (SpiTransfer * 2)()
        # Keep SCS asserted across a 10-us setup delay and the actual data.
        transfers[0].delay_usecs = 10
        transfers[1].tx_buf = ctypes.addressof(payload)
        transfers[1].length = len(packet)
        transfers[1].speed_hz = self.speed_hz
        transfers[1].bits_per_word = 8
        transfers[1].delay_usecs = 10  # hold before SCS falls
        request = 0x40006B00 | (ctypes.sizeof(transfers) << 16)
        self.last_transfer = time.monotonic()
        sent = fcntl.ioctl(self.fd, request, bytearray(transfers), True)
        if sent != len(packet):
            raise OSError(f"Short SPI transfer {sent}/{len(packet)}")
        self.transfers += 1

    def check(self):
        if self.clock_error is not None:
            raise RuntimeError("COM generator failed") from self.clock_error
        if self.lines.get_value(FAULT) == self.low:
            raise RuntimeError("FAULT_N is low (LCD/module power-limit fault)")

    def clock(self):
        try:
            value = self.low
            previous = time.monotonic()
            deadline = previous
            while not self.clock_stop.is_set():
                value = self.high if value == self.low else self.low
                self.lines.set_value(COM, value)
                now = time.monotonic()
                self.max_com_gap = max(self.max_com_gap, now - previous)
                previous = now
                self.com_edges += 1
                self.check()
                deadline += 0.5  # 1-Hz EXTCOMIN, internal VCOM inversion on rising edges
                if self.clock_stop.wait(max(0, deadline - time.monotonic())):
                    break
                if time.monotonic() - deadline > 0.25:
                    raise RuntimeError("COM scheduling delayed by more than 250 ms")
        except BaseException as error:
            self.clock_error = error
            # Blank and isolate the panel immediately on a clock/power fault.
            self.lines.set_values({DISP: self.low, COM: self.low, POWER: self.low})

    def start(self):
        self.check()
        self.lines.set_value(POWER, self.high)
        self.powered = True
        time.sleep(0.1)
        self.check()
        self.transfer(bytes([0x20, 0]))  # M2=1 clears the pixel memories.
        time.sleep(1.1)  # T2 >= one vertical period for both panel variants
        self.lines.set_value(DISP, self.high)
        time.sleep(0.001)
        self.clock_thread = threading.Thread(target=self.clock, daemon=True)
        self.clock_thread.start()
        time.sleep(0.001)
        self.check()
        LOG.info("Panel enabled, SPI %.1f MHz, %d rows/transaction, SCS active-high, "
                 "EXTCOMIN 1 Hz, FAULT_N high", self.speed_hz / 1_000_000,
                 self.rows_per_packet)

    def show(self, image):
        for packet in frame_packets(image, self.rows_per_packet):
            self.check()
            self.transfer(packet)
        self.frames += 1

    def close(self):
        try:
            if self.powered and self.fd is not None and self.clock_error is None:
                self.transfer(bytes([0x20, 0]))
                time.sleep(1.1)  # T5, clear while COM is still running
        finally:
            if self.lines is not None:
                self.lines.set_value(DISP, self.low)
                self.clock_stop.set()
                if self.clock_thread is not None:
                    self.clock_thread.join()
                self.lines.set_value(COM, self.low)
                if self.powered:
                    time.sleep(1.1)  # T6, discharge initialization before 5 V falls
                self.lines.set_value(POWER, self.low)
                self.lines.release()
                self.lines = None
            if self.fd is not None:
                os.close(self.fd)
                self.fd = None
            LOG.info("LCD cleared/disabled, power off, GPIO released")


PATTERNS = ("white", "black", "checkerboard", "vertical", "horizontal", "text")


def pattern(name, elapsed=0, target_fps=2, measured_fps=0):
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    if name == "black":
        draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), fill=0)
    elif name == "checkerboard":
        for y in range(0, HEIGHT, 16):
            for x in range(0, WIDTH, 16):
                if (x // 16 + y // 16) % 2 == 0:
                    draw.rectangle((x, y, x + 15, y + 15), fill=0)
    elif name == "vertical":
        for x in range(0, WIDTH, 2):
            draw.line((x, 0, x, HEIGHT - 1), fill=0)
    elif name == "horizontal":
        for y in range(0, HEIGHT, 2):
            draw.line((0, y, WIDTH - 1, y), fill=0)
    elif name == "text":
        draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0)
        draw.line((0, 34, WIDTH - 1, 34), fill=0)
        heading = font(22)
        body = font(16)
        draw.text((12, 7), "rp-compute LCD TEST", font=heading, fill=0)
        for y, text in zip((46, 74, 102, 130, 158), (
            "SHARP Memory LCD  400 x 240",
            "SPI0 / CE0    1 MHz",
            "EXTCOMIN 1 Hz    GPIO12",
            "0123456789  ABCDEFGHIJKLMNOP",
            f"Elapsed {int(elapsed):5d} s   {time.strftime('%H:%M:%S')}",
        )):
            draw.text((12, y), text, font=body, fill=0)
        x = 12 + int(elapsed * 20) % 344
        draw.rectangle((12, 201, 387, 225), outline=0)
        draw.rectangle((x, 205, x + 20, 221), fill=0)
        draw.text((3, 228), "BOTTOM LEFT", font=font(9), fill=0)
    elif name == "motion":
        body = font(16)
        draw.text((10, 8), "rp-compute MOTION TEST", font=body, fill=0)
        draw.text((10, 32), f"Target {target_fps:g} Hz  Measured {measured_fps:.2f} fps",
                  font=body, fill=0)
        draw.rectangle((0, 60, WIDTH - 1, HEIGHT - 1), outline=0)
        # Constant-speed motion exposes judder and slow pixel transitions.
        x = 2 + int(elapsed * 120) % (WIDTH - 44)
        draw.rectangle((x, 80, x + 39, 145), fill=0)
        for column in range(2, WIDTH - 2):
            if (column + int(elapsed * 60)) % 24 < 12:
                draw.line((column, 175, column, 219), fill=0)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--duration", type=float, default=120,
                        help="total running seconds, default 120")
    parser.add_argument("--pattern-seconds", type=float, default=8,
                        help="seconds per test pattern, default 8")
    parser.add_argument("--fps", type=float, default=2,
                        help="target full-frame rate 1-60 Hz, above 20 is experimental")
    parser.add_argument("--spi-hz", type=int,
                        help="SPI clock override, up to 10000000; default 10 MHz above 20 Hz")
    parser.add_argument("--pattern", choices=(*PATTERNS, "motion"),
                        help="keep one pattern on screen")
    parser.add_argument("--preview-dir", type=Path,
                        help="save PNG patterns without accessing hardware")
    args = parser.parse_args()
    if not math.isfinite(args.duration) or args.duration <= 0:
        parser.error("--duration must be finite and positive")
    if not math.isfinite(args.pattern_seconds) or args.pattern_seconds < 1:
        parser.error("--pattern-seconds must be at least 1")
    if not math.isfinite(args.fps) or not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60 Hz")
    if args.spi_hz is not None and not 1 <= args.spi_hz <= 10_000_000:
        parser.error("--spi-hz must be between 1 and 10000000")
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        for name in (*PATTERNS, "motion"):
            pattern(name).save(args.preview_dir / f"{name}.png")
        return 0

    stop = threading.Event()
    for signum in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signum, lambda *_: stop.set())
    display = None
    try:
        display = Display(args.fps, args.spi_hz)
        display.start()
        started = time.monotonic()
        previous = None
        next_report = 5.0
        while not stop.is_set():
            tick = time.monotonic()
            elapsed = tick - started
            if elapsed >= args.duration:
                break
            name = args.pattern or PATTERNS[int(elapsed / args.pattern_seconds) % len(PATTERNS)]
            if name != previous:
                LOG.info("Pattern %s, elapsed %.1f s", name, elapsed)
                previous = name
            measured_fps = display.frames / elapsed if elapsed > 0 else 0
            display.show(pattern(name, elapsed, args.fps, measured_fps))
            if elapsed >= next_report:
                LOG.info("Refresh %.2f fps, target %.2f Hz, %d frames, FAULT_N high",
                         display.frames / (time.monotonic() - started), args.fps,
                         display.frames)
                next_report += 5.0
            stop.wait(max(0, started + display.frames / args.fps - time.monotonic()))
        display.check()
        LOG.info("Completed %d frames, %d SPI transactions, %d COM edges, max COM gap %.4f s",
                 display.frames, display.transfers, display.com_edges, display.max_com_gap)
        LOG.info("Average refresh %.2f fps, target %.2f Hz",
                 display.frames / (time.monotonic() - started), args.fps)
        return 0
    except Exception:
        LOG.exception("Display test failed")
        return 1
    finally:
        if display is not None:
            display.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raise SystemExit(main())
