"""Persistent unprivileged PTY shell and a monochrome terminal renderer."""

import errno
import fcntl
from functools import lru_cache
import logging
import os
from pathlib import Path
import pwd
import queue
import signal
import struct
import subprocess
import sys
import termios
import time

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from keyboard_input import KeyboardInput


LOG = logging.getLogger("rp-terminal")
COLUMNS, ROWS = 49, 15
CELL_WIDTH, CELL_HEIGHT = 8, 14
MONO_FONTS = Path("/usr/share/fonts/truetype/dejavu")
CJK_FONTS = Path("/usr/share/fonts/opentype/noto")
BITMAP_FONTS = Path(__file__).resolve().parent / "fonts" / "terminus"


@lru_cache(maxsize=16)
def terminal_font(size=11, cjk=False, bold=True, italic=False):
    if size == 14 and not cjk:
        if not italic:
            weight = "b" if bold else "n"
            return ImageFont.truetype(str(BITMAP_FONTS / f"ter-u14{weight}_unicode.otb"), 14)
        size = 11
    if cjk:
        path = CJK_FONTS / f"NotoSansCJK-{'Bold' if bold else 'Regular'}.ttc"
    else:
        suffix = {(False, False): "", (True, False): "-Bold",
                  (False, True): "-Oblique", (True, True): "-BoldOblique"}[bold, italic]
        path = MONO_FONTS / f"DejaVuSansMono{suffix}.ttf"
    return ImageFont.truetype(str(path), size, index=2 if cjk else 0)


@lru_cache(maxsize=1)
def ansi_palette():
    from pyte.graphics import FG_ANSI, FG_BG_256
    names = {FG_ANSI[30 + index]: FG_BG_256[index] for index in range(8)}
    names.update({"bright" + FG_ANSI[30 + index]: FG_BG_256[index + 8] for index in range(8)})
    names["bfightmagenta"] = names["brightmagenta"]  # pyte 0.8 background-color alias.
    return names


def color_rgb(color, default):
    value = default if color == "default" else ansi_palette().get(color, color)
    value = value.removeprefix("#")
    try:
        if len(value) != 6:
            raise ValueError("Expected RGB")
        rgb = tuple(bytes.fromhex(value))
        if len(rgb) != 3:
            raise ValueError("Expected three color channels")
        return rgb
    except ValueError:
        return tuple(bytes.fromhex(default))


@lru_cache(maxsize=2048)
def terminal_colors(foreground, background, reverse):
    explicit_colors = foreground != "default" and background != "default"
    default_foreground = (background if reverse else foreground) == "default"
    foreground = color_rgb(foreground, "000000")
    background = color_rgb(background, "ffffff")
    if reverse:
        foreground, background = background, foreground
    def luminance(rgb):
        return round(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])
    bg = luminance(background)
    if explicit_colors and foreground == background:
        return bg, bg
    if default_foreground:
        return (0 if bg >= 128 else 255), bg
    fg = luminance(foreground)
    # Preserve brightness ordering while keeping small text sufficiently distinct.
    if bg >= 128:
        fg = round(fg * min(48, bg - 96) / 255)
    else:
        minimum = max(207, bg + 96)
        fg = round(minimum + fg * (255 - minimum) / 255)
    return fg, bg


@lru_cache(maxsize=1)
def dither_threshold():
    bayer = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
    threshold = Image.new("L", (400, 240))
    threshold.putdata([bayer[y % 4][x % 4] * 16 + 8 for y in range(240) for x in range(400)])
    return threshold


def monochrome(image):
    """Static ordered dithering anchored to physical screen coordinates."""
    difference = ImageChops.subtract(image, dither_threshold(), scale=1, offset=128)
    return difference.point([0] * 128 + [255] * 128, mode="1")


def key_bytes(key, application_cursor=False):
    name, text, shift, alt, control = key
    modifier = 1 + int(shift) + 2 * int(alt) + 4 * int(control)
    name = name.removeprefix("KP_")
    arrows = {"Up": "A", "Down": "B", "Right": "C", "Left": "D", "Home": "H", "End": "F"}
    tilde = {"Insert": 2, "Delete": 3, "Page_Up": 5, "Page_Down": 6,
             "F5": 15, "F6": 17, "F7": 18, "F8": 19, "F9": 20, "F10": 21, "F11": 23, "F12": 24}
    if name in arrows:
        if modifier > 1:
            return f"\x1b[1;{modifier}{arrows[name]}".encode()
        return ("\x1bO" if application_cursor else "\x1b[").encode() + arrows[name].encode()
    if name in tilde:
        suffix = f";{modifier}" if modifier > 1 else ""
        return f"\x1b[{tilde[name]}{suffix}~".encode()
    if name in ("F1", "F2", "F3", "F4"):
        suffix = chr(ord("P") + int(name[1]) - 1)
        return (f"\x1b[1;{modifier}{suffix}" if modifier > 1 else f"\x1bO{suffix}").encode()
    special = {"Return": "\r", "Enter": "\r", "Tab": "\t", "ISO_Left_Tab": "\x1b[Z",
               "BackSpace": "\x7f", "Escape": "\x1b"}
    value = special.get(name, text)
    if not value:
        return b""
    return (("\x1b" if alt else "") + value).encode("utf-8")


class TerminalBuffer:
    """Route parser events to normal history or an alternate application screen."""

    def __init__(self, send):
        import pyte
        self.normal = pyte.HistoryScreen(COLUMNS, ROWS, history=1000)
        self.alternate = pyte.Screen(COLUMNS, ROWS)
        self.current = self.normal
        self.normal.write_process_input = send
        self.alternate.write_process_input = send
        self.stream = pyte.ByteStream(self)

    def __getattr__(self, name):
        value = getattr(self.current, name)
        if callable(value):
            def dispatch(*args, **kwargs):
                return getattr(self.current, name)(*args, **kwargs)
            return dispatch
        return value

    def select_graphic_rendition(self, *attributes):
        # Normalize bright colors to palette entries, including older pyte builds.
        normalized = []
        index = 0
        while index < len(attributes):
            attribute = attributes[index]
            if attribute in (38, 48) and index + 1 < len(attributes) and attributes[index + 1] in (2, 5):
                count = 5 if attributes[index + 1] == 2 else 3
                normalized.extend(attributes[index:index + count])
                index += count
                continue
            if 90 <= attribute <= 97:
                normalized.extend((38, 5, attribute - 90 + 8))
            elif 100 <= attribute <= 107:
                normalized.extend((48, 5, attribute - 100 + 8))
            else:
                normalized.append(attribute)
            index += 1
        self.current.select_graphic_rendition(*normalized)

    def set_mode(self, *modes, **kwargs):
        if kwargs.get("private") and any(mode in (47, 1047, 1049) for mode in modes):
            if self.current is self.normal:
                self.normal.save_cursor()
                self.alternate.reset()
                self.current = self.alternate
            self.current.dirty.update(range(ROWS))
        remaining = [mode for mode in modes if mode not in (47, 1047, 1049) or not kwargs.get("private")]
        self.current.set_mode(*remaining, **kwargs)

    def reset_mode(self, *modes, **kwargs):
        if kwargs.get("private") and any(mode in (47, 1047, 1049) for mode in modes):
            if self.current is self.alternate:
                self.current = self.normal
                self.normal.restore_cursor()
            self.current.dirty.update(range(ROWS))
        remaining = [mode for mode in modes if mode not in (47, 1047, 1049) or not kwargs.get("private")]
        self.current.reset_mode(*remaining, **kwargs)


class TerminalSession:
    def __init__(self, username):
        self.account = pwd.getpwnam(username)
        self.process = None
        self.fd = None
        self.outgoing = bytearray()
        self.buffer = TerminalBuffer(lambda value: self.outgoing.extend(value.encode()))
        self.canvas = Image.new("L", (400, 240), 255)

    def start(self):
        master, slave = os.openpty()
        try:
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLUMNS, 0, 0))
            os.set_blocking(master, False)
            account = self.account
            credentials = {}
            if os.geteuid() == 0:
                os.fchown(slave, account.pw_uid, account.pw_gid)
                credentials = {"user": account.pw_uid, "group": account.pw_gid,
                               "extra_groups": os.getgrouplist(account.pw_name, account.pw_gid)}
            elif account.pw_uid != os.geteuid():
                raise PermissionError("A non-root display process can only open its own user shell")
            shell = account.pw_shell or "/bin/bash"
            environment = {"HOME": account.pw_dir, "USER": account.pw_name, "LOGNAME": account.pw_name,
                           "SHELL": shell, "TERM": "xterm-256color", "LANG": "C.UTF-8",
                           "PATH": f"{account.pw_dir}/.local/bin:/usr/local/bin:/usr/bin:/bin"}
            self.process = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--pty-child", str(slave)],
                pass_fds=(slave,), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, cwd=account.pw_dir, env=environment, **credentials)
            self.fd = master
        except Exception:
            os.close(master)
            raise
        finally:
            os.close(slave)
        LOG.info("Terminal session started as %s, pid %d, %dx%d", account.pw_name,
                 self.process.pid, COLUMNS, ROWS)

    def write(self, data):
        if self.process is not None and self.process.poll() is None:
            self.outgoing.extend(data)

    def update(self):
        if self.fd is None:
            return False
        if self.outgoing:
            try:
                count = os.write(self.fd, self.outgoing)
                del self.outgoing[:count]
            except BlockingIOError:
                pass
            except OSError as error:
                if error.errno != errno.EIO:
                    raise
        # Bound parsing work so a noisy command keeps the LCD and hotkey responsive.
        deadline = time.perf_counter() + 0.003
        for _ in range(16):
            try:
                data = os.read(self.fd, 256)
                if not data:
                    break
                self.buffer.stream.feed(data)
                if time.perf_counter() >= deadline:
                    break
            except BlockingIOError:
                break
            except OSError as error:
                if error.errno == errno.EIO:
                    break
                raise
        return self.process.poll() is not None

    @staticmethod
    @lru_cache(maxsize=2048)
    def glyph(data, foreground, background, bold, italic, underscore, strike):
        from wcwidth import wcswidth
        width = max(1, min(2, wcswidth(data))) * CELL_WIDTH
        mask = Image.new("1", (width, CELL_HEIGHT), 0)
        draw = ImageDraw.Draw(mask)
        cjk = any(ord(char) >= 0x2e80 for char in data)
        face = terminal_font(12 if cjk else 14, cjk=cjk, bold=bold, italic=italic)
        x = max(0, round((width - face.getlength(data)) / 2))
        draw.text((x, 12 - face.getmetrics()[0]), data, font=face, fill=255, anchor="la")
        if underscore:
            draw.line((0, 12, width - 1, 12), fill=255)
        if strike:
            draw.line((0, 7, width - 1, 7), fill=255)
        image = Image.new("L", (width, CELL_HEIGHT), background)
        # Keep character strokes solid when the background is dithered to 1 bit.
        if foreground != background:
            foreground = 0 if foreground < background else 255
        if 0 < background < 255 and data.strip() and foreground != background:
            halo = mask.convert("L").filter(ImageFilter.MaxFilter(3))
            image.paste(255 if foreground < background else 0, (0, 0), halo)
        image.paste(foreground, (0, 0), mask)
        return image

    def render(self, now):
        screen = self.buffer.current
        for row in sorted(screen.dirty):
            if not 0 <= row < ROWS:
                continue
            self.canvas.paste(255, (0, 20 + row * CELL_HEIGHT, 400, 20 + (row + 1) * CELL_HEIGHT))
            for column in range(COLUMNS):
                char = screen.buffer[row][column]
                if char.data == "":
                    continue  # The second cell of a double-width character.
                foreground, background = terminal_colors(char.fg, char.bg, char.reverse)
                if char.data != " " or background != 255 or char.underscore or char.strikethrough:
                    self.canvas.paste(self.glyph(char.data, foreground, background, char.bold,
                                                char.italics, char.underscore, char.strikethrough),
                                      (4 + column * CELL_WIDTH, 20 + row * CELL_HEIGHT))
        screen.dirty.clear()
        image = monochrome(self.canvas)
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 399, 18), fill=0)
        draw.text((4, 3), "Makit Compute", font=terminal_font(), fill=255, anchor="lt")
        draw.text((396, 3), f"Terminal / {self.account.pw_name}", font=terminal_font(10), fill=255, anchor="rt")
        draw.line((0, 230, 399, 230), fill=0)
        draw.text((4, 232), "Ctrl+Alt+T dashboard", font=terminal_font(8), fill=0, anchor="lt")
        draw.text((396, 232), "Shift+PgUp/PgDn history", font=terminal_font(8), fill=0, anchor="rt")
        history_visible = (screen is self.buffer.normal and screen.history.position < screen.history.size)
        if not history_visible and not screen.cursor.hidden and int(now * 2) % 2 == 0:
            x, y = screen.cursor.x, screen.cursor.y
            if 0 <= x < COLUMNS and 0 <= y < ROWS:
                left, top = 4 + x * CELL_WIDTH, 20 + (y + 1) * CELL_HEIGHT - 2
                cursor = ImageChops.invert(image.crop((left, top, left + CELL_WIDTH - 1, top + 2)))
                image.paste(cursor, (left, top))
        return image

    def close(self):
        if self.process is not None and self.process.poll() is None:
            try:
                foreground = os.tcgetpgrp(self.fd)
                if foreground > 0 and foreground != os.getpgrp():
                    os.killpg(foreground, signal.SIGHUP)
                self.process.send_signal(signal.SIGHUP)
                self.process.wait(timeout=1)
            except (ProcessLookupError, OSError, subprocess.TimeoutExpired):
                if self.process.poll() is None:
                    self.process.kill()
                    self.process.wait(timeout=1)
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


class TerminalController:
    def __init__(self, username="xonar"):
        self.username = username
        self.keyboard = KeyboardInput()
        self.session = None
        self.active = False

    def start(self):
        self.keyboard.start()

    def update(self):
        for _ in range(256):
            try:
                action, value = self.keyboard.actions.get_nowait()
            except queue.Empty:
                break
            if action == "toggle":
                if not self.active and self.session is None:
                    try:
                        self.session = TerminalSession(self.username)
                        self.session.start()
                    except Exception:
                        if self.session is not None:
                            self.session.close()
                        self.session = None
                        LOG.exception("Could not start terminal")
                        continue
                self.active = not self.active
                LOG.info("Display mode %s", "terminal" if self.active else "dashboard")
            elif self.active and self.session is not None:
                name, _, shift, alt, control = value
                screen = self.session.buffer.current
                if shift and not alt and not control and name in ("Page_Up", "Page_Down"):
                    if screen is self.session.buffer.normal:
                        (screen.prev_page if name == "Page_Up" else screen.next_page)()
                else:
                    self.session.write(key_bytes(value, application_cursor=32 in screen.mode))
        if self.session is not None and self.session.update():
            LOG.info("Terminal session exited, code %s", self.session.process.returncode)
            self.session.close()
            self.session = None
            self.active = False

    def render(self, now):
        return self.session.render(now)

    def close(self):
        self.keyboard.close()
        if self.session is not None:
            self.session.close()


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "--pty-child":
        raise SystemExit("This module is launched by the LCD terminal controller")
    os.login_tty(int(sys.argv[2]))
    shell = os.environ["SHELL"]
    os.execvpe(shell, ["-" + Path(shell).name], os.environ)
