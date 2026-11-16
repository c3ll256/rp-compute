"""Local Hermes activity snapshots shared by the plugin and LCD service."""

from dataclasses import asdict, dataclass, field
import json
import math
import os
from pathlib import Path
import socket
import threading
import time
import uuid


SOCKET_PATH = "/run/rp-compute/activity.sock"
STATES = ("disconnected", "idle", "thinking", "responding", "tool", "waiting",
          "retrying", "recovering", "done", "error", "stopped")
TERMINAL = ("done", "error", "stopped")
HOOKS = ("on_session_start", "pre_llm_call", "pre_api_request", "post_api_request",
         "api_request_error", "pre_tool_call", "post_tool_call", "post_llm_call",
         "on_session_end", "on_session_finalize", "on_human_input_request",
         "on_human_input_resolved")


@dataclass(frozen=True)
class Activity:
    state: str = "disconnected"
    tool: str = ""
    started: float = 0
    changed: float = 0
    tools_done: int = 0
    active_tasks: int = 0
    waiting_kind: str = ""


@dataclass
class Turn:
    started: float
    changed: float
    state: str = "thinking"
    tools_done: int = 0
    tools: dict = field(default_factory=dict)
    waits: dict = field(default_factory=dict)


class TaskState:
    """Keep concurrent sessions and parallel tool calls independently."""

    def __init__(self):
        self.turns = {}

    def event(self, event, data, now):
        session = str(data.get("session_id") or data.get("session_key") or "default")
        turn_id = str(data.get("turn_id") or "current")
        key = session, turn_id
        turn = self.turns.get(key)
        if turn is None and turn_id == "current":
            matches = [item for identity, item in self.turns.items()
                       if identity[0] == session and item.state not in TERMINAL]
            if len(matches) == 1:
                turn = matches[0]
        if event == "on_session_start":
            return
        if event == "on_session_finalize":
            for identity, item in self.turns.items():
                if identity[0] == session and item.state not in TERMINAL:
                    item.state, item.changed = "stopped", now
            return
        if event == "on_human_input_resolved":
            request = str(data.get("request_id") or "input")
            for item in self.turns.values():
                if request in item.waits and item.state not in TERMINAL:
                    item.waits.pop(request)
                    item.state, item.changed = "thinking", now
            return
        if event == "pre_llm_call" and (turn is None or turn.state in TERMINAL):
            turn = self.turns[key] = Turn(now, now)
        if turn is None:
            if event in ("on_session_end", "post_llm_call"):
                return
            turn = self.turns[key] = Turn(now, now)
        if turn.state in TERMINAL:
            return
        turn.changed = now
        if event == "on_session_end":
            if data.get("failed"):
                turn.state = "error"
            elif data.get("interrupted") or data.get("completed") is False:
                turn.state = "stopped"
            elif data.get("completed") is True:
                turn.state = "done"
            else:
                turn.state = "stopped"
        elif event == "post_llm_call":
            turn.state = "done"
        elif event == "on_human_input_request":
            request = str(data.get("request_id") or "input")
            turn.waits[request] = str(data.get("kind") or "clarify")
        elif event == "pre_tool_call":
            name = str(data.get("tool_name") or "tool")[:48]
            call = str(data.get("tool_call_id") or uuid.uuid4().hex)
            turn.tools[call] = name
            turn.state = "tool"
        elif event == "post_tool_call":
            call = data.get("tool_call_id")
            if call is None:
                name = str(data.get("tool_name") or "tool")[:48]
                call = next((key for key, value in turn.tools.items() if value == name), None)
            else:
                call = str(call)
            turn.tools.pop(call, None)
            turn.tools_done += 1
            turn.state = "recovering" if data.get("status") in ("error", "blocked", "cancelled") else "thinking"
        elif event == "api_request_error":
            turn.state = "retrying" if data.get("retryable") else "recovering"
        elif event == "post_api_request":
            if data.get("assistant_tool_call_count") == 0:
                turn.state = "responding"
        else:
            turn.state = "thinking"
        # Finished turns remain briefly visible, then are discarded.
        self.turns = {identity: item for identity, item in self.turns.items()
                      if item.state not in TERMINAL or now - item.changed < 30}

    def snapshot(self, now):
        active = [item for item in self.turns.values() if item.state not in TERMINAL]
        if active:
            # Waiting for a person takes priority, followed by the oldest task.
            turn = min(active, key=lambda item: (not bool(item.waits), item.started))
            state = "waiting" if turn.waits else ("tool" if turn.tools else turn.state)
        else:
            recent = [item for item in self.turns.values() if now - item.changed < 8]
            if not recent:
                return Activity(state="idle")
            turn = max(recent, key=lambda item: item.changed)
            state = turn.state
        return Activity(state=state, tool=next(iter(turn.tools.values()), ""),
                        started=turn.started, changed=turn.changed,
                        tools_done=turn.tools_done, active_tasks=len(active),
                        waiting_kind=next(iter(turn.waits.values()), ""))


class Publisher:
    """Non-blocking local snapshots with a heartbeat and reconnect replay."""

    def __init__(self, path=SOCKET_PATH):
        self.path = path
        self.source = uuid.uuid4().hex
        self.sequence = 0
        self.state = TaskState()
        self.lock = threading.Lock()
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, name="lcd-activity", daemon=True)

    def start(self):
        self.thread.start()

    def event(self, event, **kwargs):
        with self.lock:
            self.state.event(event, kwargs, time.monotonic())
            self.send()

    def send(self):
        self.sequence += 1
        payload = {"schema": 1, "source": self.source, "sequence": self.sequence,
                   "activity": asdict(self.state.snapshot(time.monotonic()))}
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
                client.setblocking(False)
                client.sendto(json.dumps(payload).encode(), self.path)
        except OSError:
            pass

    def run(self):
        while not self.stopped.is_set():
            with self.lock:
                self.send()
            self.stopped.wait(1)

    def close(self):
        self.stopped.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=2)


class ActivityMonitor:
    """Receive validated snapshots without putting I/O on the frame loop."""

    def __init__(self, path=SOCKET_PATH):
        self.path = Path(path)
        self.lock = threading.Lock()
        self.stopped = threading.Event()
        self.sources = {}
        self.socket = None
        self.owns_path = False
        self.thread = threading.Thread(target=self.run, name="hermes-activity", daemon=True)

    def start(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as probe:
                try:
                    probe.connect(str(self.path))
                except ConnectionRefusedError:
                    self.path.unlink()
                else:
                    raise RuntimeError(f"Activity socket is already in use: {self.path}")
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            self.socket.bind(str(self.path))
            self.owns_path = True
            os.chmod(self.path, 0o666)
            self.socket.settimeout(0.5)
            self.thread.start()
        except Exception:
            self.socket.close()
            if self.owns_path:
                self.path.unlink(missing_ok=True)
                self.owns_path = False
            raise

    def receive(self, payload, now):
        packet = json.loads(payload)
        if not isinstance(packet, dict) or packet.get("schema") != 1:
            return
        source, sequence, data = packet.get("source"), packet.get("sequence"), packet.get("activity")
        if not isinstance(source, str) or len(source) > 64 or not isinstance(sequence, int):
            return
        if not isinstance(data, dict) or data.get("state") not in STATES:
            return
        fields = {name: data.get(name, default) for name, default in asdict(Activity()).items()}
        for name in ("started", "changed", "tools_done", "active_tasks"):
            value = fields[name]
            if not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
                return
        if fields["started"] > now + 1 or fields["changed"] > now + 1:
            return
        for name in ("tool", "waiting_kind"):
            if not isinstance(fields[name], str) or len(fields[name]) > 48:
                return
        fields["tool"] = "".join(c for c in fields["tool"] if c.isascii() and c.isprintable())
        activity = Activity(**fields)
        with self.lock:
            previous = self.sources.get(source)
            if previous is None or sequence > previous[0]:
                self.sources[source] = sequence, now, activity
            self.sources = {key: value for key, value in self.sources.items() if now - value[1] < 10}

    def snapshot(self):
        now = time.monotonic()
        with self.lock:
            live = [value for value in self.sources.values() if now - value[1] < 10]
        if not live:
            return Activity()
        priority = {"waiting": 0, "tool": 1, "thinking": 1, "responding": 1,
                    "retrying": 1, "recovering": 1, "error": 3, "stopped": 4,
                    "done": 4, "idle": 5, "disconnected": 6}
        def order(item):
            activity = item[2]
            timestamp = activity.started if activity.active_tasks else -activity.changed
            return priority[activity.state], timestamp
        _, _, activity = min(live, key=order)
        total = sum(item[2].active_tasks for item in live)
        return Activity(**{**asdict(activity), "active_tasks": total})

    def run(self):
        while not self.stopped.is_set():
            try:
                payload = self.socket.recv(4096)
                self.receive(payload, time.monotonic())
            except socket.timeout:
                continue
            except (ValueError, TypeError, UnicodeError, OverflowError):
                continue
            except OSError:
                if not self.stopped.is_set():
                    self.stopped.wait(0.1)

    def close(self):
        self.stopped.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=1)
        if self.socket is not None:
            self.socket.close()
        if self.owns_path:
            self.path.unlink(missing_ok=True)
            self.owns_path = False
