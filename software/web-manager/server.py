#!/usr/bin/env python3
"""Makit Compute LAN management and a persistent browser terminal."""

import argparse
import base64
import codecs
from collections import deque
from dataclasses import asdict
import errno
import fcntl
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
import mimetypes
import os
from pathlib import Path
import pwd
import re
import secrets
import select
import shutil
import signal
import socket
import struct
import subprocess
import sys
import termios
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from pam_auth import authenticate
from settings_client import settings_request

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "status-display"))
from telemetry import SystemMonitor

LOG = logging.getLogger("makit-web")
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
TMUX = ["tmux", "-L", "makit-web", "-f", "/dev/null"]


class Terminal:
    def __init__(self):
        self.start_lock = threading.Lock()
        self.condition = threading.Condition()
        self.chunks = deque()
        self.position = 0
        self.outgoing = bytearray()
        self.stopped = threading.Event()
        self.process = None
        self.fd = None
        self.thread = None

    def start(self):
        with self.start_lock:
            if self.process and self.process.poll() is None and not self.stopped.is_set():
                return
            self.close()
            self.stopped = threading.Event()
            with self.condition:
                self.chunks.clear()
                self.position = 0
                self.outgoing.clear()
            self._start()

    def _start(self):
        if subprocess.run(TMUX + ["has-session", "-t", "console"], capture_output=True).returncode:
            subprocess.run(TMUX + ["new-session", "-d", "-s", "console", "-x", "100", "-y", "28",
                                  "-c", str(Path.home()), pwd.getpwuid(os.getuid()).pw_shell + " -l"],
                           check=True, capture_output=True)
        subprocess.run(TMUX + ["set-option", "-t", "console", "status", "off"], check=True)
        master, slave = os.openpty()
        self.tty = os.ttyname(slave)
        try:
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 28, 100, 0, 0))
            environment = dict(os.environ, TERM="xterm-256color", LANG="C.UTF-8")
            self.process = subprocess.Popen(
                [sys.executable, str(ROOT / "server.py"), "--pty-child", str(slave)],
                pass_fds=(slave,), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, cwd=Path.home(), env=environment)
            os.set_blocking(master, False)
            self.fd = master
        except Exception:
            os.close(master)
            raise
        finally:
            os.close(slave)
        self.thread = threading.Thread(target=self.read, daemon=True, name="web-terminal")
        self.thread.start()

    def read(self):
        try:
            while not self.stopped.is_set():
                with self.condition:
                    writing = bool(self.outgoing)
                readable, writable, _ = select.select([self.fd], [self.fd] if writing else [], [], .1)
                if writable:
                    with self.condition:
                        try:
                            count = os.write(self.fd, self.outgoing[:65536])
                            del self.outgoing[:count]
                        except BlockingIOError:
                            pass
                if readable:
                    try:
                        data = os.read(self.fd, 65536)
                    except BlockingIOError:
                        continue
                    if not data:
                        break
                    with self.condition:
                        self.position += len(data)
                        self.chunks.append((self.position, data))
                        while self.chunks and self.position - self.chunks[0][0] > 1024 * 1024:
                            self.chunks.popleft()
                        self.condition.notify_all()
        except OSError as error:
            if not self.stopped.is_set() and error.errno != errno.EIO:
                LOG.exception("Terminal transport closed")
        finally:
            self.stopped.set()
            with self.condition:
                self.condition.notify_all()

    def send(self, data):
        with self.condition:
            if self.stopped.is_set():
                raise ValueError("终端连接已关闭，请重启管理服务")
            if len(self.outgoing) + len(data) > 262144:
                raise ValueError("输入过快，请稍后重试")
            self.outgoing.extend(data)

    def resize(self, columns, rows):
        if not 20 <= columns <= 300 or not 5 <= rows <= 120:
            raise ValueError("终端尺寸超出范围")
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, columns, 0, 0))

    def redraw(self):
        subprocess.run(TMUX + ["refresh-client", "-t", self.tty, "-R"],
                       capture_output=True, timeout=3)

    def command(self):
        result = subprocess.run(TMUX + ["display-message", "-p", "-t", "console", "#{pane_current_command}"],
                                capture_output=True, text=True, timeout=3)
        return result.stdout.strip()

    def close(self):
        self.stopped.set()
        if self.thread:
            self.thread.join(timeout=1)
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)


class CodexLogin:
    def __init__(self):
        self.lock = threading.Lock()
        self.process = None
        self.mode = "device"
        self.output = ""
        self.state = "idle"
        self.started = 0
        self.generation = 0
        self.status_at = 0
        self.logged_in = False
        result = subprocess.run(["codex", "--version"], capture_output=True, text=True, timeout=15)
        self.version = result.stdout.strip()

    def start(self, mode):
        if mode not in ("device", "browser"):
            raise ValueError("未知登录方式")
        with self.lock:
            if self.state == "running":
                return
            self.generation += 1
            generation = self.generation
            self.mode, self.output, self.state = mode, "", "running"
            self.started = time.time()
            args = ["codex", "login"] + (["--device-auth"] if mode == "device" else [])
            self.process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, start_new_session=True,
                                            env=dict(os.environ, NO_COLOR="1", BROWSER="/bin/true"))
            thread = threading.Thread(target=self.read, args=(self.process, generation), daemon=True)
            thread.start()

    def read(self, process, generation):
        decoder = codecs.getincrementaldecoder("utf-8")("replace")
        while True:
            chunk = process.stdout.read1(4096)
            if not chunk:
                break
            with self.lock:
                if generation == self.generation:
                    self.output = (self.output + decoder.decode(chunk))[-24576:]
        code = process.wait()
        process.stdout.close()
        with self.lock:
            if generation == self.generation:
                self.state = "complete" if code == 0 else "failed"
                self.status_at = 0

    def cancel(self):
        with self.lock:
            process = self.process
            self.generation += 1
            self.state, self.output = "idle", ""
        if process and process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def status(self):
        with self.lock:
            if time.monotonic() - self.status_at > 8:
                result = subprocess.run(["codex", "login", "status"], capture_output=True, timeout=15)
                self.logged_in = result.returncode == 0
                self.status_at = time.monotonic()
            output = ANSI.sub("", self.output).replace("\r", "")
            urls = re.findall(r"https://[^\s\x1b]+", output)
            urls = [url for url in urls if urllib.parse.urlsplit(url).hostname in
                    ("auth.openai.com", "chatgpt.com")]
            code = re.search(r"\b[A-Z0-9]{4}-[A-Z0-9]{4,6}\b", output)
            return dict(logged_in=self.logged_in, version=self.version, state=self.state,
                        mode=self.mode, output=output, url=urls[0] if urls else "",
                        code=code.group() if code else "", started=self.started)

    def callback(self, url):
        parsed = urllib.parse.urlsplit(url.strip())
        if (parsed.scheme != "http" or parsed.hostname not in ("localhost", "127.0.0.1")
                or parsed.port != 1455 or parsed.path != "/auth/callback"
                or parsed.username or parsed.password or len(url) > 16384):
            raise ValueError("请粘贴完整的 localhost 或 127.0.0.1:1455/auth/callback 回调地址")
        with self.lock:
            if self.state != "running" or self.mode != "browser":
                raise ValueError("请先发起浏览器授权")
        target = "http://127.0.0.1:1455/auth/callback?" + parsed.query
        # The CLI validates OAuth state and exchanges the authorization code itself.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            with opener.open(target, timeout=45) as response:
                status = response.status
        except urllib.error.HTTPError as error:
            status = error.code
        if status not in (200, 302, 303):
            raise ValueError("Codex 未接受回调，请查看登录详情后重新发起授权")


class Application:
    def __init__(self):
        self.username = pwd.getpwuid(os.getuid()).pw_name
        self.sessions = {}
        self.attempts = {}
        self.lock = threading.Lock()
        self.terminal = Terminal()
        self.login = CodexLogin()
        self.monitor = SystemMonitor()

    def session(self, handler):
        jar = cookies.SimpleCookie()
        try:
            jar.load(handler.headers.get("Cookie", ""))
            token = jar["makit_session"].value
        except (KeyError, cookies.CookieError):
            return None
        with self.lock:
            expires = self.sessions.get(token, 0)
            if expires > time.time():
                return token
            self.sessions.pop(token, None)
        return None

    def sign_in(self, address, username, password):
        with self.lock:
            now = time.monotonic()
            self.attempts = {key: [t for t in values if now - t < 60]
                             for key, values in self.attempts.items() if values and now - values[-1] < 60}
            attempts = self.attempts.setdefault(address, [])
            if len(attempts) >= 5:
                raise ValueError("尝试次数较多，请一分钟后重试")
            attempts.append(now)
        if username != self.username or not authenticate(username, password):
            raise PermissionError("账号或密码不正确")
        token = secrets.token_urlsafe(32)
        with self.lock:
            self.sessions = {key: value for key, value in self.sessions.items() if value > time.time()}
            if len(self.sessions) >= 128:
                self.sessions.pop(next(iter(self.sessions)))
            self.sessions[token] = time.time() + 43200
            self.attempts.pop(address, None)
        return token


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    @property
    def app(self):
        return self.server.app

    def log_message(self, *_):
        pass  # Keep terminal contents, credentials and OAuth query strings out of logs.

    def valid_host(self):
        hostname = urllib.parse.urlsplit("http://" + self.headers.get("Host", "")).hostname
        return hostname in {self.connection.getsockname()[0], "127.0.0.1", "localhost",
                            socket.gethostname(), socket.gethostname() + ".local"}

    def write_headers(self, status, content_type, length=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if length is not None:
            self.send_header("Content-Length", str(length))

    def json(self, value, status=200, cookie=None):
        data = json.dumps(value, ensure_ascii=False).encode()
        self.write_headers(status, "application/json; charset=utf-8", len(data))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            self.get()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except ValueError as error:
            self.json({"error": str(error)}, 503)
        except Exception:
            LOG.exception("GET failed")
            self.close_connection = True

    def get(self):
        if not self.valid_host():
            return self.json({"error": "无效的设备地址"}, 403)
        path = urllib.parse.urlsplit(self.path).path
        if path == "/api/public":
            return self.json(dict(username=self.app.username, hostname=socket.gethostname(),
                                  authenticated=bool(self.app.session(self))))
        if path.startswith("/api/"):
            token = self.app.session(self)
            if not token:
                return self.json({"error": "请先登录管理页面"}, 401)
            if path == "/api/status":
                return self.json(dict(metrics=asdict(self.app.monitor.snapshot()),
                                      terminal_command=self.app.terminal.command(), codex=self.app.login.status()))
            if path == "/api/settings":
                return self.json({"network": settings_request("network.status"),
                                  "bluetooth": settings_request("bluetooth.status")})
            if path == "/api/clash":
                return self.json(settings_request("clash.status"))
            if path == "/api/terminal/events":
                return self.events(token)
            return self.json({"error": "接口不存在"}, 404)
        if path == "/assets/inter.ttf":
            file = ROOT.parent / "status-display/fonts/Inter.ttf"
        else:
            relative = "index.html" if path == "/" else urllib.parse.unquote(path).lstrip("/")
            file = (ROOT / "static" / relative).resolve()
            if not file.is_relative_to(ROOT / "static"):
                return self.json({"error": "文件不存在"}, 404)
        if not file.is_file():
            return self.json({"error": "文件不存在"}, 404)
        data = file.read_bytes()
        self.write_headers(200, mimetypes.guess_type(file.name)[0] or "application/octet-stream", len(data))
        self.end_headers()
        self.wfile.write(data)

    def events(self, token):
        terminal = self.app.terminal
        terminal.start()
        self.write_headers(200, "text/event-stream; charset=utf-8")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        self.wfile.write(b"retry: 1500\n\n")
        self.wfile.flush()
        try:
            cursor = int(self.headers.get("Last-Event-ID", "-1"))
        except ValueError:
            cursor = -1
        while not terminal.stopped.is_set():
            with self.app.lock:
                if self.app.sessions.get(token, 0) <= time.time():
                    self.wfile.write(b"event: expired\ndata: {}\n\n")
                    self.wfile.flush()
                    break
            with terminal.condition:
                oldest = terminal.chunks[0][0] - len(terminal.chunks[0][1]) if terminal.chunks else terminal.position
                reset = cursor < oldest or cursor > terminal.position
                if reset:
                    cursor = terminal.position
                chunks = [(position, data) for position, data in terminal.chunks if position > cursor]
                if not reset and not chunks:
                    terminal.condition.wait(timeout=10)
            if reset:
                self.wfile.write(b"event: reset\ndata: {}\n\n")
                self.wfile.flush()
                terminal.redraw()
                continue
            for cursor, data in chunks:
                encoded = base64.b64encode(data).decode()
                event = f"id: {cursor}\nevent: output\ndata: {json.dumps(encoded)}\n\n"
                self.wfile.write(event.encode())
            self.wfile.write(b": heartbeat\n\n")
            self.wfile.flush()
        self.close_connection = True

    def do_POST(self):
        try:
            if not self.valid_host():
                raise PermissionError("无效的设备地址")
            origin = self.headers.get("Origin")
            if (self.headers.get("X-Makit-Request") != "1"
                    or origin and origin != "http://" + self.headers.get("Host")):
                raise PermissionError("请求来源不匹配")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 65536:
                raise ValueError("请求大小超出范围")
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError("请求格式不正确")
            path = urllib.parse.urlsplit(self.path).path
            if path == "/api/login":
                username, password = data.get("username", ""), data.get("password", "")
                if (not isinstance(username, str) or not isinstance(password, str)
                        or len(password) > 512 or "\0" in password):
                    raise ValueError("账号或密码格式不正确")
                token = self.app.sign_in(self.client_address[0], username, password)
                return self.json({"ok": True}, cookie=f"makit_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200")
            token = self.app.session(self)
            if not token:
                return self.json({"error": "请先登录管理页面"}, 401)
            if path == "/api/logout":
                with self.app.lock:
                    self.app.sessions.pop(token, None)
                return self.json({"ok": True}, cookie="makit_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0")
            if path.startswith("/api/settings/"):
                parts = path.split("/")
                if len(parts) != 5 or parts[3] not in ("network", "bluetooth", "clash"):
                    raise ValueError("未知系统设置接口")
                return self.json(settings_request(parts[3] + "." + parts[4], data))
            if path == "/api/terminal/input":
                self.app.terminal.send(base64.b64decode(data["data"], validate=True))
            elif path == "/api/terminal/resize":
                self.app.terminal.resize(int(data["columns"]), int(data["rows"]))
            elif path == "/api/terminal/codex":
                command = self.app.terminal.command()
                if command not in ("bash", "zsh", "sh", "fish", "-bash"):
                    raise ValueError("当前终端已有程序运行，请先退出到命令行")
                self.app.terminal.send(b"codex\r")
            elif path == "/api/codex/login":
                self.app.login.start(data.get("mode", "device"))
            elif path == "/api/codex/cancel":
                self.app.login.cancel()
            elif path == "/api/codex/callback":
                self.app.login.callback(data["url"])
            else:
                return self.json({"error": "接口不存在"}, 404)
            self.json({"ok": True})
        except PermissionError as error:
            self.json({"error": str(error)}, 403)
        except (ValueError, KeyError, TypeError) as error:
            self.json({"error": str(error)}, 400)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            LOG.exception("Management request failed")
            self.json({"error": "操作失败，请重试或查看管理服务日志"}, 500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not shutil.which("codex") or not shutil.which("tmux"):
        raise SystemExit("codex and tmux must be installed and on PATH")
    app = Application()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    server.daemon_threads = True
    server.app = app
    stopped = threading.Event()
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, lambda *_: stopped.set())
    server.timeout = .5
    try:
        app.monitor.start()
        app.terminal.start()
        LOG.info("Management server listening on %s:%s as %s", args.host, args.port, app.username)
        while not stopped.is_set():
            server.handle_request()
    finally:
        app.login.cancel()
        app.terminal.close()
        app.monitor.close()
        server.server_close()


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--pty-child":
        os.login_tty(int(sys.argv[2]))
        os.execvp("tmux", TMUX + ["attach-session", "-t", "console"])
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
