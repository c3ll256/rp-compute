"""Install a verified Mihomo binary and a supplied Clash configuration on the Pi."""

import grp
import ipaddress
import os
from pathlib import Path
import pwd
import re
import socket
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit

import yaml


CONFIG = Path("/etc/makit-clash")
DATA = Path("/var/lib/makit-clash")
BINARY = "/usr/local/bin/mihomo"
UNIT = "makit-clash.service"
PROXY = "http://127.0.0.1:7890"
BYPASS = ("localhost,127.0.0.1,::1,.local,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12")
PROXY_KEYS = ("http_proxy", "https_proxy", "all_proxy", "no_proxy")
ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?([a-zA-Z_][a-zA-Z_0-9]*)\s*=")


def write(path, contents, uid=0, gid=0, mode=0o644):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        tmp = Path(stream.name)
        try:
            os.fchmod(stream.fileno(), mode)
            os.fchown(stream.fileno(), uid, gid)
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(tmp, path)
        finally:
            tmp.unlink(missing_ok=True)


def runtime_config(source):
    config = yaml.safe_load(source)
    if not isinstance(config, dict) or not config.get("proxies"):
        raise SystemExit("The supplied configuration has no Clash proxies")
    for key in ("external-controller", "external-controller-tls", "external-controller-pipe",
                "external-ui", "external-ui-url", "external-ui-name", "listeners", "tunnels",
                "redir-port", "tproxy-port", "port", "socks-port"):
        config.pop(key, None)
    config.update({"allow-lan": False, "bind-address": "127.0.0.1", "mixed-port": 7890,
                   "external-controller-unix": "/run/makit-clash/controller.sock",
                   "tun": {"enable": False}})
    dns = config.get("dns", {})
    if dns.get("listen"):
        dns["listen"] = "127.0.0.1:1053"
    resolvers = dns.get("proxy-server-nameserver", [])
    adapted = []
    for server in resolvers:
        url = urlsplit(server if "://" in server else "//" + server)
        try:
            loopback = ipaddress.ip_address(url.hostname).is_loopback
        except ValueError:
            loopback = url.hostname == "localhost"
        adapted.append("system" if loopback else server)
    if resolvers:
        dns["proxy-server-nameserver"] = list(dict.fromkeys(adapted))
    config.setdefault("profile", {})["store-selected"] = True
    return yaml.safe_dump(config, allow_unicode=True, sort_keys=False).encode()


def proxy_assignments(export=False):
    prefix = "export " if export else ""
    return "".join(f'{prefix}{name}="{BYPASS if key == "no_proxy" else PROXY}"\n'
                   for key in PROXY_KEYS for name in (key, key.upper()))


def set_environment(path, backup, account=None, shell=False):
    uid, gid, mode = (account.pw_uid, account.pw_gid, 0o600) if account else (0, 0, 0o644)
    current = path.read_text() if path.exists() else ""
    if current and not backup.exists():
        write(backup, current.encode(), mode=0o600)
    def managed(line):
        match = ASSIGNMENT.match(line)
        return match and match[1].lower() in PROXY_KEYS
    retained = "".join(line for line in current.splitlines(keepends=True) if not managed(line)).rstrip()
    text = (retained + "\n" if retained else "") + proxy_assignments(shell)
    write(path, text.encode(), uid, gid, mode)


def install(binary, supplied, geo):
    origin = supplied.read_bytes()
    config = runtime_config(origin)
    try:
        account = pwd.getpwnam("makit-clash")
    except KeyError:
        subprocess.run(["useradd", "--system", "--user-group", "--home-dir", str(DATA),
                        "--shell", "/usr/sbin/nologin", "makit-clash"], check=True)
        account = pwd.getpwnam("makit-clash")
    gid = grp.getgrnam("makit-clash").gr_gid
    CONFIG.mkdir(mode=0o750, exist_ok=True)
    os.chown(CONFIG, 0, gid)
    subprocess.run(["install", "-d", "-m", "700", "-o", account.pw_name, str(DATA)], check=True)
    write(DATA / "country.mmdb", geo.read_bytes(), account.pw_uid, gid, 0o600)
    write(Path(BINARY), binary.read_bytes(), mode=0o755)
    candidate = CONFIG / "candidate.yaml"
    write(candidate, config, gid=gid, mode=0o640)
    try:
        check = subprocess.run(["runuser", "-u", account.pw_name, "--", BINARY, "-t", "-d", str(DATA),
                                "-f", str(candidate)], capture_output=True, timeout=45)
        if check.returncode:
            raise SystemExit("Mihomo rejected the supplied configuration during validation")
        write(CONFIG / "nexi.yaml", origin, mode=0o600)
        os.replace(candidate, CONFIG / "config.yaml")
    finally:
        candidate.unlink(missing_ok=True)
    unit = Path(__file__).with_name(UNIT)
    write(Path("/etc/systemd/system") / UNIT, unit.read_bytes())
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", UNIT], check=True)
    subprocess.run(["systemctl", "restart", UNIT], check=True)


def enable_system_proxy():
    for _ in range(12):
        try:
            with socket.create_connection(("127.0.0.1", 7890), timeout=1):
                break
        except OSError:
            time.sleep(1)
    else:
        raise SystemExit("Mihomo did not open its local proxy port")
    probe = subprocess.run(["curl", "--noproxy", "", "--proxy", PROXY, "--silent",
                            "--output", "/dev/null", "--write-out", "%{http_code}",
                            "--max-time", "20", "https://api.openai.com/v1/models"],
                           capture_output=True, text=True, timeout=22)
    if probe.returncode or probe.stdout not in ("200", "401"):
        raise SystemExit("Local Clash proxy did not reach OpenAI; previous system proxy retained")
    xonar = pwd.getpwnam("xonar")
    home = Path(xonar.pw_dir)
    backup = CONFIG / "previous-environment"
    backup.mkdir(mode=0o700, exist_ok=True)
    set_environment(Path("/etc/environment"), backup / "environment")
    write(Path("/etc/profile.d/makit-clash.sh"), proxy_assignments(export=True).encode())
    set_environment(home / ".config/makit/proxy.sh", backup / "proxy.sh", xonar, shell=True)
    set_environment(home / ".codex/.env", backup / "codex.env", xonar)
    write(Path("/etc/apt/apt.conf.d/81makit-clash"), (
        f'Acquire::http::Proxy "{PROXY}";\nAcquire::https::Proxy "{PROXY}";\n').encode())
    print(f"System proxy enabled; OpenAI returned HTTP {probe.stdout}")


if __name__ == "__main__":
    if os.getuid() != 0:
        raise SystemExit("Run this installer using sudo")
    if sys.argv[1:] == ["--enable-system-proxy"]:
        enable_system_proxy()
    elif len(sys.argv) == 4:
        install(*(Path(value) for value in sys.argv[1:]))
    else:
        raise SystemExit("Usage: install_clash.py MIHOMO_BINARY CONFIG_YAML COUNTRY_MMDB")
