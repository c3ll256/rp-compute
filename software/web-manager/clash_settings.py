"""Allowlisted controls for the local Mihomo service."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import http.client
import json
import logging
import socket
import subprocess
import threading
import time
from urllib.parse import quote, urlencode


SERVICE = "makit-clash.service"
PROXY = "http://127.0.0.1:7890"
CONTROLLER = "/run/makit-clash/controller.sock"
MODES = ("rule", "global", "direct")
CONTROL_LOCK = threading.Lock()
LOG = logging.getLogger(__name__)
DELAY_URL = "https://api.openai.com/v1/models"
DELAY_TIMEOUT_MS = 5000
DELAY_WORKERS = 8
BUILTIN_PROXIES = {"Direct", "Reject", "RejectDrop", "Compatible", "Pass", "PassRule", "Dns", "DNS"}


class ControllerError(ValueError):
    def __init__(self, status):
        super().__init__("Clash 已拒绝此操作")
        self.status = status


class ControllerConnection(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect(CONTROLLER)


def request(method, path, data=None, *, timeout=4):
    connection = ControllerConnection("localhost", timeout=timeout)
    try:
        body = json.dumps(data).encode() if data is not None else None
        connection.request(method, path, body, {"Content-Type": "application/json"})
        response = connection.getresponse()
        if response.status not in (200, 204):
            raise ControllerError(response.status)
        body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError("Clash 响应过大")
        return json.loads(body) if body else {}
    except (OSError, http.client.HTTPException) as error:
        raise ValueError("Clash 控制接口暂时不可用") from error
    finally:
        connection.close()


def selectors():
    proxies = request("GET", "/proxies")["proxies"]
    return [{"name": name, "selected": info.get("now", ""), "options": info["all"]}
            for name, info in proxies.items() if info.get("type") == "Selector" and "all" in info]


def delay_targets():
    proxies = request("GET", "/proxies")["proxies"]
    targets = [(name, "", "/proxies/" + quote(name, safe="") + "/delay")
               for name, info in proxies.items() if "all" not in info and info.get("type") not in BUILTIN_PROXIES]
    providers = request("GET", "/providers/proxies")["providers"]
    for provider, info in providers.items():
        if info.get("vehicleType") == "Compatible":
            continue  # Mihomo also exposes the static group members here.
        for proxy in info["proxies"]:
            name = proxy["name"]
            path = "/providers/proxies/" + quote(provider, safe="") + "/" + quote(name, safe="") + "/healthcheck"
            targets.append((name, provider, path))
    return targets


def measure_delay(path):
    query = urlencode({"url": DELAY_URL, "timeout": DELAY_TIMEOUT_MS, "expected": "401"})
    try:
        delay = request("GET", path + "?" + query, timeout=7).get("delay")
    except ControllerError as error:
        return {"state": "timeout" if error.status == 504 else "failed"}
    except ValueError:
        return {"state": "failed"}
    if isinstance(delay, int) and delay > 0:
        return {"state": "ok", "delay": delay}
    return {"state": "failed"}


class DelayScan:
    def __init__(self):
        self.lock = threading.Lock()
        self.phase = "idle"
        self.results = []
        self.started = None
        self.finished = None
        self.interrupted = threading.Event()

    def snapshot(self):
        with self.lock:
            return {"phase": self.phase, "started": self.started, "finished": self.finished,
                    "results": list(self.results)}

    def start(self):
        with self.lock:
            if self.phase == "running":
                return
            targets = delay_targets()
            if not targets:
                raise ValueError("当前配置没有可测速的节点")
            self.results = [{"name": name, "provider": provider, "state": "waiting"}
                            for name, provider, _ in targets]
            self.phase = "running"
            self.started, self.finished = time.time(), None
            self.interrupted.clear()
            threading.Thread(target=self.run, args=(targets,), daemon=True, name="clash-delay").start()

    def run(self, targets):
        phase = "complete"
        try:
            with ThreadPoolExecutor(max_workers=DELAY_WORKERS) as pool:
                jobs = {pool.submit(self.measure, path): index for index, (_, _, path) in enumerate(targets)}
                for job in as_completed(jobs):
                    result = job.result()
                    if result is not None:
                        with self.lock:
                            index = jobs[job]
                            self.results[index] = {**self.results[index], **result}
        except Exception:
            LOG.exception("Clash delay scan failed")
            phase = "failed"
        finally:
            with self.lock:
                self.phase = "interrupted" if self.interrupted.is_set() else phase
                self.finished = time.time()

    def measure(self, path):
        if not self.interrupted.is_set():
            return measure_delay(path)


DELAY_SCAN = DelayScan()


def status():
    active = subprocess.run(["systemctl", "is-active", SERVICE], capture_output=True,
                            text=True, timeout=4).stdout.strip()
    result = {"state": active, "available": False, "address": PROXY, "groups": [],
              "delay_scan": DELAY_SCAN.snapshot()}
    if active != "active":
        return result
    try:
        result.update(version=request("GET", "/version")["version"],
                      mode=request("GET", "/configs")["mode"].lower(), groups=selectors(), available=True)
    except ValueError as error:
        result["error"] = str(error)
    return result


def dispatch(operation, data):
    if operation == "status":
        return status()
    if operation == "test":
        probe = subprocess.run(["curl", "--noproxy", "", "--proxy", PROXY, "--silent",
                                "--output", "/dev/null", "--write-out", "%{http_code}",
                                "--connect-timeout", "8", "--max-time", "15",
                                DELAY_URL],
                               capture_output=True, text=True, timeout=17)
        return {"reachable": probe.returncode == 0 and probe.stdout in ("200", "401"),
                "http_status": int(probe.stdout) if probe.stdout.isdigit() else 0}
    with CONTROL_LOCK:
        if operation in ("start", "stop", "restart"):
            if operation in ("stop", "restart"):
                DELAY_SCAN.interrupted.set()
            result = subprocess.run(["systemctl", operation, SERVICE], capture_output=True, timeout=20)
            if result.returncode:
                raise ValueError("Clash 服务操作失败")
        elif operation == "scan":
            DELAY_SCAN.start()
        elif operation == "mode":
            mode = data.get("mode")
            if mode not in MODES:
                raise ValueError("未知 Clash 代理模式")
            request("PATCH", "/configs", {"mode": mode})
        elif operation == "select":
            group, node = data.get("group"), data.get("node")
            if not isinstance(group, str) or not isinstance(node, str):
                raise ValueError("策略组或节点无效")
            choices = next((item["options"] for item in selectors() if item["name"] == group), None)
            if choices is None or node not in choices:
                raise ValueError("该策略组中没有这个节点")
            request("PUT", "/proxies/" + quote(group, safe=""), {"name": node})
        else:
            raise ValueError("未知 Clash 操作")
    return {"ok": True}
