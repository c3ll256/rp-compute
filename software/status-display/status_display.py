#!/usr/bin/env python3
"""Animated system companion for the rp-compute 400x240 Memory LCD."""

import argparse
from dataclasses import replace
import logging
import math
from pathlib import Path
import pwd
import signal
import sys
import threading
import time

from PIL import Image, ImageDraw

from telemetry import Snapshot, SystemMonitor
from codex_activity import Activity, CodexMonitor
from workroom import HEIGHT, WIDTH, Renderer, font
from terminal_mode import TerminalController


LOG = logging.getLogger("rp-status")


def boot_frame(elapsed, ready=False, preview=False):
    """Wake the companion on a clean brand screen while the service starts."""
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    awake = min(1, max(0, (elapsed - 0.25) / 0.8))
    awake = awake * awake * (3 - 2 * awake)
    settle = math.exp(-elapsed * 5)
    cx, cy = 200, 89 + 2 * math.sin(elapsed * math.tau * 0.65)
    radius_x, radius_y = 38 - 2 * settle, 38 + 2 * settle
    draw.ellipse((round(cx - radius_x), round(cy - radius_y),
                  round(cx + radius_x), round(cy + radius_y)), fill=0)
    blink = max(0, 1 - abs(elapsed - 2.7) / 0.09)
    angle = math.radians(75 - awake * 50)
    for x_factor, y_factor, length, width in ((0.21, -0.42, 16, 6), (0.63, -0.50, 14, 4)):
        x = cx + radius_x * x_factor + 2 * math.sin(elapsed * 1.5) ** 5
        y = cy + radius_y * y_factor
        stroke = max(2, round(width * (0.4 + 0.6 * awake) * (1 - blink * 0.6)))
        length *= 0.55 + 0.45 * awake
        segment = max(0, (length * (1 - blink * 0.8) - stroke) / 2)
        dx, dy = math.sin(angle) * segment, math.cos(angle) * segment
        points = ((round(x - dx), round(y - dy)), (round(x + dx), round(y + dy)))
        draw.line(points, fill=255, width=stroke)
        cap = (stroke - 1) / 2
        for point_x, point_y in points:
            draw.ellipse((round(point_x - cap), round(point_y - cap),
                          round(point_x + cap), round(point_y + cap)), fill=255)
    draw.text((200, 148), "Makit Compute", font=font(22, 780), fill=0, anchor="mt")
    draw.text((200, 184), "Ready" if ready else "Starting up",
              font=font(11, 650), fill=0, anchor="mt")
    for index in range(3):
        x = 188 + index * 12
        active = ready or index == int(elapsed * 3) % 3
        draw.ellipse((x - 2, 207, x + 2, 211), outline=0, fill=0 if active else 255)
    if preview:
        draw.text((12, 226), "Preview", font=font(9, 650), fill=0, anchor="lt")
    return image


def preview(path, showcase=False, boot_seconds=None):
    """Synthetic metrics are explicitly marked in the rendered header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    renderer = Renderer()
    now = 100.0
    snapshot = Snapshot(
        hostname="makit-compute", sampled_at=now, cpu_percent=18,
        memory_used=920 * 1024**2, memory_total=3840 * 1024**2,
        temperature=46, disk_used=3 * 1024**3, disk_total=14 * 1024**3,
        uptime=37250, interface="eth0", address="192.168.50.83",
        receive_rate=3400, transmit_rate=1200,
    )
    if boot_seconds is not None:
        if path.suffix.lower() != ".gif":
            boot_frame(min(1.5, boot_seconds), preview=True).save(path)
            return
        frames = []
        for index in range(math.ceil((boot_seconds + 1) * 20)):
            elapsed = index / 20
            if elapsed < boot_seconds:
                image = boot_frame(elapsed, ready=elapsed >= max(1, boot_seconds - 0.6), preview=True)
            else:
                image = renderer.render(snapshot, elapsed, now, preview=True,
                                        activity=Activity(state="idle"), wall_time=0)
            frames.append(image)
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=50,
                       loop=0, optimize=False, disposal=2)
        return
    if path.suffix.lower() != ".gif":
        renderer.render(snapshot, 0, now, preview=True,
                        activity=Activity("thinking", 1)).save(path)
        return
    frames = []
    wall_time = time.time()
    states = ("idle", "thinking", "working", "replying", "waiting", "done", "attention", "stopped")
    sequence = states if showcase else ("thinking", "working", "done")
    for index in range(len(sequence) * 40):
        elapsed = index / 20
        state = sequence[index // 40]
        active = state in ("thinking", "working", "waiting", "replying", "attention")
        sample = replace(snapshot, sampled_at=now + elapsed, cpu_percent=32 if active else 6)
        frames.append(renderer.render(sample, elapsed, now + elapsed, preview=True,
                                      wall_time=wall_time + elapsed, activity=Activity(state, int(active))))
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=50,
                   loop=0, optimize=False, disposal=2)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ignore-fault", action="store_true",
                        help="log a low FAULT_N signal and keep updating")
    parser.add_argument("--fps", type=float, default=60)
    parser.add_argument("--boot-seconds", type=float, default=4,
                        help="startup animation duration, 0 disables it")
    parser.add_argument("--duration", type=float, help="stop after this many seconds")
    parser.add_argument("--interface", help="network interface, default follows the route")
    parser.add_argument("--terminal-user", default="xonar", help="user for the keyboard terminal shell")
    parser.add_argument("--no-keyboard", action="store_true", help="leave physical keyboards with the system console")
    parser.add_argument("--codex-sessions", type=Path, help="Codex session directory for the terminal user")
    parser.add_argument("--preview", type=Path, help="save a synthetic PNG or animated GIF")
    parser.add_argument("--showcase", action="store_true", help="preview Codex activity states in a GIF")
    parser.add_argument("--boot-preview", action="store_true", help="preview the startup animation")
    args = parser.parse_args()
    if not math.isfinite(args.fps) or not 1 <= args.fps <= 60:
        parser.error("--fps must be between 1 and 60")
    if args.duration is not None and (not math.isfinite(args.duration) or args.duration <= 0):
        parser.error("--duration must be finite and positive")
    if not math.isfinite(args.boot_seconds) or args.boot_seconds < 0:
        parser.error("--boot-seconds must be finite and nonnegative")
    if args.boot_preview and (args.preview is None or args.showcase):
        parser.error("--boot-preview requires --preview and cannot combine with --showcase")
    if args.showcase and (args.preview is None or args.preview.suffix.lower() != ".gif"):
        parser.error("--showcase requires --preview with a .gif path")
    if args.preview:
        if args.preview.suffix.lower() not in (".png", ".gif"):
            parser.error("--preview must end with .png or .gif")
        preview(args.preview, args.showcase, args.boot_seconds if args.boot_preview else None)
        return 0

    # Reuse the driver that was verified on the physical LS027B7DH01A.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "display-test"))
    from display_test import Display

    stopped = threading.Event()
    for number in (signal.SIGINT, signal.SIGTERM):
        signal.signal(number, lambda *_: stopped.set())
    monitor = SystemMonitor(args.interface)
    account = pwd.getpwnam(args.terminal_user)
    session_dir = args.codex_sessions or Path(account.pw_dir) / ".codex/sessions"
    activity_monitor = CodexMonitor(session_dir, account.pw_uid)
    terminal = None if args.no_keyboard else TerminalController(args.terminal_user)
    display = None
    try:
        monitor.start()
        activity_monitor.start()
        if terminal is not None:
            terminal.start()
        display = Display(args.fps, ignore_fault=args.ignore_fault)
        display.start()
        renderer = Renderer()
        started = time.monotonic()
        next_report = 30.0
        next_frame = started
        previous_state = None
        boot_deadline = args.boot_seconds
        while not stopped.is_set():
            now = time.monotonic()
            elapsed = now - started
            if args.duration is not None and elapsed >= args.duration:
                break
            snapshot = monitor.snapshot()
            activity = activity_monitor.snapshot()
            if terminal is not None:
                terminal.update()
            if terminal is not None and terminal.active:
                boot_deadline = 0
                image = terminal.render(now)
                previous_state = "terminal", None
            elif elapsed < boot_deadline:
                ready = elapsed >= boot_deadline - 0.6 and bool(snapshot.sampled_at)
                image = boot_frame(elapsed, ready=ready)
                if previous_state is None:
                    LOG.info("Startup animation started, duration %.1f s", args.boot_seconds)
                    previous_state = "startup", None
            else:
                if previous_state == ("startup", None):
                    LOG.info("Startup animation complete")
                image = renderer.render(snapshot, elapsed, now, activity=activity,
                                        keyboard=bool(terminal and terminal.keyboard.attached))
                state = activity.state, renderer.mood
                if state != previous_state:
                    LOG.info("Codex state %s, companion %s", *state)
                    previous_state = state
            display.show(image)
            if elapsed >= next_report:
                LOG.info("Refresh %.2f fps, %d frames, metrics age %.2f s, max COM gap %.4f s",
                         display.frames / (time.monotonic() - started), display.frames,
                         now - snapshot.sampled_at, display.max_com_gap)
                next_report += 30
            next_frame += 1 / args.fps
            after_render = time.monotonic()
            # Drop missed presentation slots while keeping uptime/duration accurate.
            if next_frame < after_render - 1 / args.fps:
                next_frame = after_render
            stopped.wait(max(0, next_frame - after_render))
        display.check()
        return 0
    except Exception:
        LOG.exception("Status display failed")
        return 1
    finally:
        try:
            if terminal is not None:
                terminal.close()
        finally:
            try:
                if display is not None:
                    display.close()
            finally:
                try:
                    activity_monitor.close()
                finally:
                    monitor.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    raise SystemExit(main())
