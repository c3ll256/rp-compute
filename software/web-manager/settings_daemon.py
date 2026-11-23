#!/usr/bin/env python3
"""Privileged, narrowly scoped system-settings service for Makit Compute."""

import json
import logging
import os
from pathlib import Path
import pwd
import signal
import socket
import socketserver
import struct
import threading

from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib, GLibUnix

from bluetooth_settings import BluetoothSettings
from clash_settings import dispatch as clash_dispatch
from wifi_settings import WiFiSettings


SOCKET = Path("/run/makit-settings/control.sock")
LOG = logging.getLogger("makit-settings")


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.connection.settimeout(45)
        _, uid, _ = struct.unpack("3i", self.connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
        if uid not in (0, self.server.allowed_uid):
            return
        try:
            raw = self.rfile.readline(65537)
            if len(raw) > 65536:
                raise ValueError("设置请求过大")
            data = json.loads(raw)
            action = data.pop("action")
            wifi = self.server.wifi
            if action == "network.status":
                result = wifi.status()
            elif action == "network.scan":
                wifi.scan()
                result = {"ok": True}
            elif action == "network.connect":
                result = {"id": wifi.begin(data)}
            elif action == "network.confirm":
                wifi.confirm(data.get("id"))
                result = {"ok": True}
            elif action == "network.cancel":
                wifi.cancel_change(data.get("id"))
                result = {"ok": True}
            elif action.startswith("bluetooth."):
                result = self.server.bluetooth.call(action.split(".", 1)[1], data)
            elif action.startswith("clash."):
                result = clash_dispatch(action.split(".", 1)[1], data)
            else:
                raise ValueError("未知系统设置操作")
            response = {"result": result}
        except (ValueError, KeyError, TypeError) as error:
            response = {"error": str(error)}
        except Exception:
            LOG.exception("System settings request failed")
            response = {"error": "系统设置操作失败，请查看设置服务日志"}
        try:
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode() + b"\n")
        except (BrokenPipeError, ConnectionResetError):
            pass


class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


def main():
    if os.getuid() != 0:
        raise SystemExit("The settings service must run as root")
    DBusGMainLoop(set_as_default=True)
    account = pwd.getpwnam("xonar")
    SOCKET.parent.mkdir(mode=0o750, exist_ok=True)
    os.chown(SOCKET.parent, 0, account.pw_gid)
    SOCKET.unlink(missing_ok=True)
    wifi = WiFiSettings()
    wifi.recover()  # A previous interrupted transaction is restored before requests are accepted.
    server = Server(str(SOCKET), Handler)
    os.chown(SOCKET, 0, account.pw_gid)
    os.chmod(SOCKET, 0o660)
    server.allowed_uid = account.pw_uid
    server.wifi = wifi
    server.bluetooth = BluetoothSettings()
    loop = GLib.MainLoop()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    def stop():
        loop.quit()
        return False
    for number in (signal.SIGTERM, signal.SIGINT):
        GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, number, stop)
    LOG.info("System settings service ready")
    try:
        loop.run()
    finally:
        server.shutdown()
        server.server_close()
        SOCKET.unlink(missing_ok=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
