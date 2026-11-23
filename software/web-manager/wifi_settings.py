"""Transactional Wi-Fi changes using the existing netplan WPA supplicant."""

import copy
import hashlib
import json
import logging
import os
from pathlib import Path
import re
import secrets
import socket
import subprocess
import threading
import time

import yaml


LOG = logging.getLogger("makit-wifi")
PENDING = {"preparing", "connecting", "awaiting_confirmation", "rolling_back"}


def atomic_write(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def unescape_ssid(value):
    def replace(match):
        if match[1]:
            return bytes([int(match[1], 16)])
        return {b"t": b"\t", b"n": b"\n", b"r": b"\r", b'"': b'"', b"\\": b"\\"}[match[2]]
    raw = re.sub(rb'\\x([a-fA-F0-9]{2})|\\([tnr"\\])', replace, value.encode())
    return raw.decode("utf-8", "replace")


class WPAControl:
    def __init__(self, interface="wlan0", runtime="/run/makit-settings"):
        self.interface = interface
        self.runtime = Path(runtime)

    def request(self, command):
        path = self.runtime / ("wpa-" + secrets.token_hex(6))
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.settimeout(4)
        try:
            client.bind(str(path))
            client.connect("/run/wpa_supplicant/" + self.interface)
            client.send(command.encode())
            reply = client.recv(65536).decode("utf-8", "replace").strip()
            if reply.startswith(("FAIL", "UNKNOWN COMMAND")):
                raise ValueError("Wi-Fi 控制操作失败")
            return reply
        finally:
            client.close()
            path.unlink(missing_ok=True)

    def status(self):
        return dict(line.split("=", 1) for line in self.request("STATUS").splitlines() if "=" in line)


class WiFiSettings:
    def __init__(self, storage="/var/lib/makit-settings", netplan="/etc/netplan", control=None,
                 connect_timeout=60, confirm_timeout=120,
                 cloud_config="/etc/cloud/cloud.cfg.d/99-makit-network-config.cfg"):
        self.storage = Path(storage)
        self.storage.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.netplan = Path(netplan)
        self.cloud_config = Path(cloud_config)
        self.control = control or WPAControl()
        self.connect_timeout = connect_timeout
        self.confirm_timeout = confirm_timeout
        self.lock = threading.RLock()
        self.cancel = threading.Event()
        self.state_file = self.storage / "wifi-transaction.json"
        self.profile_file = self.storage / "wifi-profiles.json"
        self.state = json.loads(self.state_file.read_text()) if self.state_file.exists() else {"phase": "idle"}
        self.profiles = json.loads(self.profile_file.read_text()) if self.profile_file.exists() else {}
        self.scan_lock = threading.Lock()
        self.networks = []
        self.scanning = False

    def files(self):
        return sorted(set(self.netplan.glob("*.yaml")) | set(self.netplan.glob("*.yml")))

    def known_profiles(self):
        profiles = copy.deepcopy(self.profiles)
        for path in self.files():
            config = yaml.safe_load(path.read_text()) or {}
            spec = config.get("network", {}).get("wifis", {}).get("wlan0", {})
            profiles.update(spec.get("access-points", {}))
        return profiles

    def update(self, **fields):
        with self.lock:
            self.state.update(fields)
            atomic_write(self.state_file, json.dumps(self.state).encode())

    def current(self):
        status = self.control.status()
        addresses = subprocess.run(["ip", "-j", "-4", "addr", "show", "dev", "wlan0"],
                                   capture_output=True, text=True, timeout=3, check=True)
        ipv4 = [entry["local"] for device in json.loads(addresses.stdout)
                for entry in device.get("addr_info", []) if entry.get("scope") == "global"]
        return {"ssid": unescape_ssid(status.get("ssid", "")), "connected": status.get("wpa_state") == "COMPLETED",
                "state": status.get("wpa_state", "DISCONNECTED"), "ipv4": ipv4,
                "frequency": status.get("freq", ""), "interface": "wlan0"}

    def status(self):
        try:
            current = self.current()
            available, error = True, ""
        except (OSError, ValueError, subprocess.SubprocessError):
            current, available, error = {}, False, "Wi-Fi 控制接口暂时不可用"
        with self.lock:
            transaction = {key: value for key, value in self.state.items() if key not in ("files", "backup")}
            transaction["remaining"] = max(0, round(self.state.get("deadline", 0) - time.time()))
            saved = [{"ssid": ssid, "security": self.security(profile or {}), "hidden": bool((profile or {}).get("hidden"))}
                     for ssid, profile in self.known_profiles().items()]
        with self.scan_lock:
            networks, scanning = list(self.networks), self.scanning
        links = []
        result = subprocess.run(["ip", "-j", "addr", "show"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            links = [{"name": item["ifname"], "state": item.get("operstate", ""),
                      "addresses": [a["local"] for a in item.get("addr_info", [])
                                    if a.get("family") == "inet" and a.get("scope") == "global"]}
                     for item in json.loads(result.stdout) if item["ifname"] != "lo"]
        return dict(available=available, error=error, current=current, saved=saved, networks=networks,
                    scanning=scanning, transaction=transaction, interfaces=links,
                    management_url="http://" + socket.gethostname() + ".local:8080/#settings")

    @staticmethod
    def security(profile):
        auth = profile.get("auth", {})
        if auth.get("key-management") == "sae":
            return "sae"
        if auth.get("key-management", "").startswith("eap"):
            return "enterprise"
        return "psk" if "password" in profile or "password" in auth else "none"

    def scan(self):
        with self.lock:
            if self.state.get("phase") in PENDING:
                raise ValueError("网络切换进行中，请等待完成后再扫描")
        with self.scan_lock:
            if self.scanning:
                return
            self.scanning = True
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        try:
            self.control.request("SCAN")
            time.sleep(4)
            found = {}
            for row in self.control.request("SCAN_RESULTS").splitlines()[1:]:
                fields = row.split("\t", 4)
                if len(fields) != 5 or not fields[4]:
                    continue
                _, frequency, signal, flags, raw_ssid = fields
                ssid = unescape_ssid(raw_ssid)
                security = self.scan_security(flags)
                item = dict(ssid=ssid, signal=int(signal), frequency=int(frequency), security=security)
                if ssid not in found or item["signal"] > found[ssid]["signal"]:
                    found[ssid] = item
            with self.scan_lock:
                self.networks = sorted(found.values(), key=lambda item: item["signal"], reverse=True)
        except (OSError, ValueError):
            LOG.info("Wi-Fi scan did not complete")
        finally:
            with self.scan_lock:
                self.scanning = False

    @staticmethod
    def scan_security(flags):
        for marker, security in (("PSK", "psk"), ("SAE", "sae"), ("EAP", "enterprise"),
                                 ("WEP", "unsupported"), ("OWE", "unsupported"),
                                 ("RSN", "unsupported"), ("WPA", "unsupported")):
            if marker in flags:
                return security
        return "none"

    def profile(self, data):
        ssid = data.get("ssid")
        if not isinstance(ssid, str) or not 1 <= len(ssid.encode()) <= 32 or "\0" in ssid:
            raise ValueError("Wi-Fi 名称须为1至32字节")
        if data.get("use_saved"):
            profiles = self.known_profiles()
            if ssid not in profiles:
                raise ValueError("尚未保存这个网络的密码")
            return ssid, copy.deepcopy(profiles[ssid] or {})
        security, password = data.get("security", "psk"), data.get("password", "")
        if security not in ("psk", "sae", "none") or not isinstance(password, str) or "\0" in password:
            raise ValueError("网络认证参数不正确")
        profile = {"hidden": bool(data.get("hidden", False))}
        if security == "psk":
            if re.fullmatch(r"[0-9a-fA-F]{64}", password):
                key = password
            elif 8 <= len(password.encode()) <= 63:
                key = hashlib.pbkdf2_hmac("sha1", password.encode(), ssid.encode(), 4096, 32).hex()
            else:
                raise ValueError("WPA/WPA2 密码须为8至63字节，或64位十六进制密钥")
            profile["auth"] = {"key-management": "psk", "password": key}
        elif security == "sae":
            if not 1 <= len(password.encode()) <= 63:
                raise ValueError("WPA3 密码须为1至63字节")
            profile["auth"] = {"key-management": "sae", "password": password}
        return ssid, profile

    def begin(self, data):
        with self.lock:
            if self.state.get("phase") in PENDING:
                raise ValueError("已有网络切换正在进行")
            ssid, profile = self.profile(data)
            if self.security(profile) == "enterprise":
                raise ValueError("企业 Wi-Fi 请通过终端配置")
            old = self.current()
            identifier = secrets.token_hex(8)
            backup = self.storage / ("wifi-backup-" + identifier)
            backup.mkdir(mode=0o700)
            files = self.files()
            for path in files:
                atomic_write(backup / path.name, path.read_bytes())
            if self.cloud_config.exists():
                atomic_write(backup / "cloud-init-network.cfg", self.cloud_config.read_bytes())
            self.profiles.update(self.known_profiles())
            atomic_write(self.profile_file, json.dumps(self.profiles).encode())
            self.state = {"id": identifier, "phase": "preparing", "target": ssid,
                          "previous": old.get("ssid", ""), "deadline": time.time() + self.confirm_timeout,
                          "backup": backup.name, "files": [path.name for path in files],
                          "cloud_config_existed": self.cloud_config.exists(),
                          "message": "正在准备新网络，旧连接配置已保存"}
            self.update()
            self.cancel = threading.Event()
            threading.Thread(target=self._switch, args=(identifier, ssid, profile, self.cancel), daemon=True).start()
            return identifier

    def _switch(self, transaction, ssid, profile, cancel):
        try:
            identifier = self.control.request("ADD_NETWORK")
            if not identifier.isdigit():
                raise ValueError("无法创建临时 Wi-Fi 连接")
            self.control.request(f"SET_NETWORK {identifier} ssid {ssid.encode().hex()}")
            security = self.security(profile)
            password = profile.get("password", profile.get("auth", {}).get("password", ""))
            if security == "none":
                self.control.request(f"SET_NETWORK {identifier} key_mgmt NONE")
            elif security == "sae":
                self.control.request(f"SET_NETWORK {identifier} key_mgmt SAE")
                self.control.request(f"SET_NETWORK {identifier} ieee80211w 2")
                self.control.request(f"SET_NETWORK {identifier} sae_password " + json.dumps(password, ensure_ascii=False))
            else:
                key = password if re.fullmatch(r"[0-9a-fA-F]{64}", password) else hashlib.pbkdf2_hmac(
                    "sha1", password.encode(), ssid.encode(), 4096, 32).hex()
                self.control.request(f"SET_NETWORK {identifier} key_mgmt WPA-PSK")
                self.control.request(f"SET_NETWORK {identifier} psk {key}")
            if profile.get("hidden"):
                self.control.request(f"SET_NETWORK {identifier} scan_ssid 1")
            self.pending_profile = profile
            self.update(phase="connecting", message="正在连接新网络，连接失败将自动恢复原网络")
            cancel.wait(1.5)  # Let the HTTP response reach the browser before switching radio.
            if not cancel.is_set():
                self.control.request("SELECT_NETWORK " + identifier)
            connect_deadline = time.monotonic() + self.connect_timeout
            while True:
                with self.lock:
                    phase, deadline = self.state["phase"], self.state["deadline"]
                    if self.state["id"] != transaction or phase == "connected":
                        return
                if cancel.is_set() or time.time() >= deadline:
                    break
                current = self.current()
                if current["connected"] and current["ssid"] == ssid and current["ipv4"]:
                    with self.lock:
                        if self.state["id"] != transaction or self.state["phase"] == "connected":
                            return
                        if self.state["phase"] != "awaiting_confirmation":
                            self.update(phase="awaiting_confirmation", addresses=current["ipv4"],
                                        message="新网络已连通，请确认保留；倒计时结束将恢复原网络")
                elif phase == "connecting" and time.monotonic() >= connect_deadline:
                    break
                cancel.wait(2)
            self.rollback("新网络连接失败、取消或确认超时", transaction)
        except Exception:
            LOG.exception("Wi-Fi transaction failed")
            self.rollback("网络切换未完成", transaction)

    def generate(self):
        result = subprocess.run(["netplan", "generate"], capture_output=True, timeout=30)
        if result.returncode:
            raise ValueError("Netplan 配置校验失败")

    def confirm(self, identifier):
        with self.lock:
            if (self.state.get("id") != identifier or self.state.get("phase") != "awaiting_confirmation"
                    or time.time() >= self.state["deadline"]):
                raise ValueError("这个网络切换已结束，或尚未连接成功")
            current = self.current()
            if not current["connected"] or current["ssid"] != self.state["target"] or not current["ipv4"]:
                raise ValueError("新网络连接尚未就绪")
            documents = [(path, yaml.safe_load(path.read_text()) or {}) for path in self.files()]
            candidates = []
            for path, config in documents:
                wifi = config.get("network", {}).get("wifis", {}).get("wlan0")
                if wifi is not None:
                    wifi["access-points"] = {}
                    candidates.append(wifi)
            if not candidates:
                raise ValueError("未找到 wlan0 的 Netplan 配置")
            candidates[-1]["access-points"] = {self.state["target"]: self.pending_profile}
            for path, config in documents:
                atomic_write(path, yaml.safe_dump(config, allow_unicode=True, sort_keys=False).encode())
            try:
                self.generate()
            except Exception:
                self.cancel.set()
                raise
            self.profiles[self.state["target"]] = self.pending_profile
            atomic_write(self.profile_file, json.dumps(self.profiles).encode())
            if self.cloud_config.parent.is_dir():
                atomic_write(self.cloud_config, b"# Network settings are managed by Makit Compute.\nnetwork:\n  config: disabled\n")
            self.update(phase="connected", message="新网络已保留，重启后将自动连接")

    def rollback(self, reason, transaction=None):
        with self.lock:
            if (self.state.get("phase") not in PENDING
                    or transaction is not None and self.state.get("id") != transaction):
                return
            self.update(phase="rolling_back", message="正在恢复原网络")
            backup = self.storage / self.state["backup"]
            try:
                for name in self.state["files"]:
                    atomic_write(self.netplan / name, (backup / name).read_bytes())
                if self.state.get("cloud_config_existed"):
                    atomic_write(self.cloud_config, (backup / "cloud-init-network.cfg").read_bytes())
                else:
                    self.cloud_config.unlink(missing_ok=True)
                self.generate()
                for attempt in range(10):
                    try:
                        self.control.request("RECONFIGURE")
                        break
                    except (OSError, ValueError):
                        if attempt == 9:
                            subprocess.run(["systemctl", "restart", "netplan-wpa-wlan0.service"],
                                           check=True, capture_output=True, timeout=20)
                        else:
                            time.sleep(1)
                try:
                    self.control.request("RECONNECT")
                except (OSError, ValueError):
                    pass  # RECONFIGURE also handles saved networks without an active selection.
                previous = self.state.get("previous", "")
            except Exception:
                LOG.exception("Wi-Fi configuration recovery failed")
                self.update(phase="rollback_failed", message="原配置已尝试恢复，请通过终端检查 Wi-Fi")
                return
        if not previous:
            self.update(phase="rolled_back", message=reason + "，已恢复原网络配置")
            return
        until = time.monotonic() + 35
        while time.monotonic() < until:
            try:
                current = self.current()
                if current["connected"] and current["ssid"] == previous and current["ipv4"]:
                    self.update(phase="rolled_back", message=reason + "，已恢复原网络")
                    return
            except (OSError, ValueError, subprocess.SubprocessError):
                pass
            time.sleep(2)
        self.update(phase="rollback_failed", message="原网络配置已恢复，正在等待原接入点和地址")

    def recover(self):
        if self.state.get("phase") in PENDING:
            self.rollback("检测到上次网络切换被中断")

    def cancel_change(self, identifier):
        with self.lock:
            if self.state.get("id") != identifier or self.state.get("phase") not in PENDING:
                raise ValueError("这个网络切换已结束")
            self.cancel.set()
