"""Local Linux metrics for the rp-compute screen."""

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import socket
import subprocess
import threading
import time


LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class Snapshot:
    hostname: str = "rp-compute"
    sampled_at: float = 0
    cpu_percent: float | None = None
    memory_used: int | None = None
    memory_total: int | None = None
    temperature: float | None = None
    disk_used: int | None = None
    disk_total: int | None = None
    uptime: float | None = None
    interface: str | None = None
    address: str | None = None
    receive_rate: float | None = None
    transmit_rate: float | None = None


def optional_read(reader):
    try:
        return reader()
    except (OSError, ValueError, KeyError, IndexError, subprocess.SubprocessError):
        LOG.debug("Metric unavailable", exc_info=True)
        return None


class SystemSampler:
    def __init__(self, interface=None, proc_root="/proc", sys_root="/sys", disk_path="/"):
        self.interface = interface
        self.proc = Path(proc_root)
        self.sys = Path(sys_root)
        self.disk_path = disk_path
        self.previous_cpu = None
        self.previous_network = None

    def cpu(self):
        fields = (self.proc / "stat").read_text().splitlines()[0].split()
        if fields[0] != "cpu" or len(fields) < 5:
            raise ValueError("Missing aggregate CPU counters")
        # guest/guest_nice are already included in user/nice.
        counters = [int(value) for value in fields[1:9]]
        total = sum(counters)
        idle = counters[3] + (counters[4] if len(counters) > 4 else 0)
        previous = self.previous_cpu
        self.previous_cpu = total, idle
        if previous is None or total <= previous[0]:
            return None
        busy = 1 - (idle - previous[1]) / (total - previous[0])
        return min(100, max(0, busy * 100))

    def memory(self):
        values = {}
        for line in (self.proc / "meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            values[key] = int(value.split()[0]) * 1024
        total = values["MemTotal"]
        available = values.get("MemAvailable")
        if available is None:
            available = sum(values.get(key, 0) for key in
                            ("MemFree", "Buffers", "Cached", "SReclaimable"))
            available -= values.get("Shmem", 0)
        if total <= 0:
            raise ValueError("Invalid total memory")
        return min(total, max(0, total - available)), total

    def temperature(self):
        value = int((self.sys / "class/thermal/thermal_zone0/temp").read_text()) / 1000
        if not -40 <= value <= 150:
            raise ValueError("Invalid thermal reading")
        return value

    def disk(self):
        info = os.statvfs(self.disk_path)
        return ((info.f_blocks - info.f_bfree) * info.f_frsize,
                info.f_blocks * info.f_frsize)

    def active_interface(self):
        if self.interface:
            return self.interface
        for line in (self.proc / "net/route").read_text().splitlines()[1:]:
            fields = line.split()
            if len(fields) >= 4 and fields[1] == "00000000" and int(fields[3], 16) & 1:
                return fields[0]
        for path in sorted((self.sys / "class/net").iterdir()):
            if path.name != "lo" and optional_read(lambda: (path / "operstate").read_text().strip()) == "up":
                return path.name
        return None

    def ipv4(self, interface):
        result = subprocess.run(
            ["ip", "-j", "-4", "addr", "show", "dev", interface],
            capture_output=True, text=True, timeout=2, check=True,
        )
        for device in json.loads(result.stdout):
            for address in device.get("addr_info", []):
                if address.get("family") == "inet" and address.get("scope") == "global":
                    return address["local"]
        return None

    def network_rates(self, interface, now):
        root = self.sys / "class/net" / interface / "statistics"
        received = int((root / "rx_bytes").read_text())
        sent = int((root / "tx_bytes").read_text())
        previous = self.previous_network
        self.previous_network = interface, now, received, sent
        if previous is None or previous[0] != interface or now <= previous[1]:
            return None, None
        if received < previous[2] or sent < previous[3]:
            return None, None
        elapsed = now - previous[1]
        return (received - previous[2]) / elapsed, (sent - previous[3]) / elapsed

    def sample(self):
        cpu = optional_read(self.cpu)
        memory = optional_read(self.memory) or (None, None)
        temperature = optional_read(self.temperature)
        disk = optional_read(self.disk) or (None, None)
        uptime = optional_read(lambda: float((self.proc / "uptime").read_text().split()[0]))
        interface = optional_read(self.active_interface)
        address = None
        rates = None, None
        now = time.monotonic()
        if interface:
            address = optional_read(lambda: self.ipv4(interface))
            rates = optional_read(lambda: self.network_rates(interface, now)) or (None, None)
        else:
            self.previous_network = None
        return Snapshot(
            hostname=socket.gethostname(), sampled_at=time.monotonic(), cpu_percent=cpu,
            memory_used=memory[0], memory_total=memory[1], temperature=temperature,
            disk_used=disk[0], disk_total=disk[1], uptime=uptime,
            interface=interface, address=address, receive_rate=rates[0], transmit_rate=rates[1],
        )


class SystemMonitor:
    def __init__(self, interface=None):
        self.sampler = SystemSampler(interface)
        self.lock = threading.Lock()
        self.stopped = threading.Event()
        self.latest = Snapshot(hostname=socket.gethostname())
        self.thread = threading.Thread(target=self.run, name="system-metrics", daemon=True)

    def start(self):
        self.thread.start()

    def snapshot(self):
        with self.lock:
            return self.latest

    def run(self):
        while not self.stopped.is_set():
            try:
                snapshot = self.sampler.sample()
                with self.lock:
                    self.latest = snapshot
            except Exception:
                # The renderer marks the previous snapshot stale after 5 seconds.
                LOG.exception("System metric collection failed")
            self.stopped.wait(1)

    def close(self):
        self.stopped.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=3)
