"""Observe local Codex CLI turn activity without forwarding session content."""

from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import stat
import threading
import time


LOG = logging.getLogger(__name__)
ACTIVE_WINDOW = 15 * 60
RESULT_WINDOW = 8
READ_SIZE = 256 * 1024
CALLS = {"function_call", "custom_tool_call"}
RESULTS = {"function_call_output", "custom_tool_call_output"}
END_EVENTS = {"task_complete": "done", "turn_aborted": "stopped"}


@dataclass(frozen=True)
class Activity:
    state: str = "idle"
    active_tasks: int = 0


@dataclass
class Session:
    inode: int
    offset: int = 0
    partial: bytes = b""
    skipping: bool = False
    state: str = "idle"
    changed: float = 0
    turn: str | None = None
    calls: dict = field(default_factory=dict)

    def update(self, record):
        kind, payload = record.get("type"), record.get("payload")
        if not isinstance(payload, dict) or not isinstance(record.get("timestamp"), str):
            return
        try:
            changed = datetime.fromisoformat(record["timestamp"]).timestamp()
        except (ValueError, OverflowError, OSError):
            return
        event = payload.get("type")
        if not isinstance(event, str):
            return
        if kind == "event_msg" and event == "task_started":
            self.turn = payload.get("turn_id")
            self.calls.clear()
            self.state, self.changed = "thinking", changed
        elif kind == "event_msg" and event in END_EVENTS and self.turn is not None:
            if payload.get("turn_id") not in (None, self.turn):
                return
            self.turn = None
            self.calls.clear()
            self.state, self.changed = END_EVENTS[event], changed
        elif self.turn is not None and kind == "response_item":
            call = payload.get("call_id")
            if event in CALLS and isinstance(call, str):
                name = payload.get("name")
                self.calls[call] = isinstance(name, str) and name.split("__")[-1] == "request_user_input"
                self.state, self.changed = "working", changed
            elif event in RESULTS and isinstance(call, str):
                self.calls.pop(call, None)
                self.state, self.changed = "thinking", changed
            elif event == "message" and payload.get("role") == "assistant":
                self.state, self.changed = "replying", changed
        elif self.turn is not None and kind == "event_msg" and event == "error":
            self.state, self.changed = "attention", changed

    def read(self, fd, size):
        if self.offset == 0 and size > READ_SIZE * 4:
            self.offset = size - READ_SIZE * 4
            self.skipping = True
        os.lseek(fd, self.offset, os.SEEK_SET)
        chunk = os.read(fd, READ_SIZE)
        if not chunk:
            return
        self.offset += len(chunk)
        lines = (self.partial + chunk).split(b"\n")
        self.partial = lines.pop()
        if self.skipping and lines:
            del lines[0]
            self.skipping = False
        if len(self.partial) > READ_SIZE:
            self.partial = b""
            self.skipping = True
        for line in lines:
            # World-state entries, prompts and outputs never leave the reader.
            if b'"event_msg"' not in line and b'"response_item"' not in line:
                continue
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError, RecursionError):
                continue
            if isinstance(record, dict):
                self.update(record)

    def active_state(self):
        if any(self.calls.values()):
            return "waiting"
        if self.calls:
            return "working"
        return self.state


class CodexMonitor:
    def __init__(self, directory, uid):
        self.directory = Path(directory)
        self.uid = uid
        self.sessions = {}
        self.latest = Activity()
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, name="codex-activity", daemon=True)

    def start(self):
        self.thread.start()

    def close(self):
        self.stopped.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=2)

    def snapshot(self):
        return self.latest

    def open_rollouts(self):
        proc = Path("/proc")
        if not proc.is_dir():
            return None
        live = set()
        for process in proc.iterdir():
            if not process.name.isdigit():
                continue
            try:
                if process.stat().st_uid != self.uid or (process / "comm").read_text().strip() != "codex":
                    continue
                for descriptor in (process / "fd").iterdir():
                    try:
                        if Path(os.readlink(descriptor)).name.startswith("rollout-"):
                            live.add(descriptor.stat().st_ino)
                    except OSError:
                        continue
            except OSError:
                continue
        return live

    def scan(self, now):
        known = {}
        for path in self.directory.glob("*/*/*/rollout-*.jsonl"):
            try:
                file = path.lstat()
                if (not stat.S_ISREG(file.st_mode) or file.st_uid != self.uid
                        or now - file.st_mtime > ACTIVE_WINDOW):
                    continue
                session = self.sessions.get(path)
                if session is None or session.inode != file.st_ino or session.offset > file.st_size:
                    session = Session(file.st_ino)
                known[path] = session
                if session.offset == file.st_size:
                    continue
                fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                try:
                    opened = os.fstat(fd)
                    if opened.st_uid == self.uid and stat.S_ISREG(opened.st_mode) and opened.st_ino == file.st_ino:
                        session.read(fd, opened.st_size)
                finally:
                    os.close(fd)
            except OSError:
                continue
        self.sessions = known
        active = [s for s in known.values() if s.turn is not None and 0 <= now - s.changed < ACTIVE_WINDOW]
        if any(now - session.changed > 3 for session in active):
            live = self.open_rollouts()
            if live is not None:
                active = [session for session in active if session.inode in live or now - session.changed <= 3]
        if active:
            front = max(active, key=lambda s: (s.active_state() == "waiting", s.changed))
            return Activity(front.active_state(), len(active))
        recent = [s for s in known.values() if s.state in END_EVENTS.values()
                  and 0 <= now - s.changed < RESULT_WINDOW]
        return Activity(max(recent, key=lambda s: s.changed).state) if recent else Activity()

    def run(self):
        while not self.stopped.is_set():
            try:
                self.latest = self.scan(time.time())
            except OSError:
                LOG.debug("Codex session directory unavailable")
            self.stopped.wait(.5)
