"""BlueZ adapter, devices and browser-mediated pairing prompts."""

from concurrent.futures import Future
import re
import secrets
import struct
import time

import dbus
import dbus.service
from gi.repository import GLib


class Rejected(dbus.DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"


class Agent(dbus.service.Object):
    PATH = "/com/makit/Agent"

    def __init__(self, bus, manager):
        super().__init__(bus, self.PATH)
        self.manager = manager

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Release(self):
        self.manager.registered = False

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="s", async_callbacks=("reply", "error"))
    def RequestPinCode(self, device, reply, error):
        self.manager.ask("pin", device, "", reply, error)

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="u", async_callbacks=("reply", "error"))
    def RequestPasskey(self, device, reply, error):
        self.manager.ask("passkey", device, "", reply, error)

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="")
    def DisplayPinCode(self, device, pin):
        self.manager.ask("display", device, str(pin))

    @dbus.service.method("org.bluez.Agent1", in_signature="ouq", out_signature="")
    def DisplayPasskey(self, device, passkey, entered):
        self.manager.ask("display", device, f"{int(passkey):06d}", entered=int(entered))

    @dbus.service.method("org.bluez.Agent1", in_signature="ou", out_signature="", async_callbacks=("reply", "error"))
    def RequestConfirmation(self, device, passkey, reply, error):
        self.manager.ask("confirm", device, f"{int(passkey):06d}", reply, error)

    @dbus.service.method("org.bluez.Agent1", in_signature="o", out_signature="", async_callbacks=("reply", "error"))
    def RequestAuthorization(self, device, reply, error):
        self.manager.ask("authorize", device, "", reply, error)

    @dbus.service.method("org.bluez.Agent1", in_signature="os", out_signature="", async_callbacks=("reply", "error"))
    def AuthorizeService(self, device, uuid, reply, error):
        properties = self.manager.properties(str(device), "org.bluez.Device1")
        if properties.get("Trusted"):
            reply()
        else:
            self.manager.ask("authorize", device, "", reply, error)

    @dbus.service.method("org.bluez.Agent1", in_signature="", out_signature="")
    def Cancel(self):
        self.manager.clear_prompt()


class BluetoothSettings:
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.agent = Agent(self.bus, self)
        self.registered = False
        self.prompt = None
        self.job = {"state": "idle"}
        self.scan_timer = None
        self.bus.add_signal_receiver(self.owner_changed, signal_name="NameOwnerChanged",
                                     dbus_interface="org.freedesktop.DBus", arg0="org.bluez")

    def owner_changed(self, name, old, new):
        self.registered = False

    def call(self, action, data):
        future = Future()
        def perform():
            try:
                future.set_result(self.dispatch(action, data))
            except Exception as error:
                future.set_exception(ValueError(str(error)))
            return False
        GLib.idle_add(perform)
        return future.result(timeout=35)

    def properties(self, path, interface):
        return dbus.Interface(self.bus.get_object("org.bluez", path),
                              "org.freedesktop.DBus.Properties").GetAll(interface, timeout=5)

    def objects(self):
        return dbus.Interface(self.bus.get_object("org.bluez", "/"),
                              "org.freedesktop.DBus.ObjectManager").GetManagedObjects(timeout=5)

    def register(self):
        if not self.registered:
            manager = dbus.Interface(self.bus.get_object("org.bluez", "/org/bluez"), "org.bluez.AgentManager1")
            manager.RegisterAgent(Agent.PATH, "KeyboardDisplay", timeout=5)
            manager.RequestDefaultAgent(Agent.PATH, timeout=5)
            self.registered = True

    def adapter(self):
        for path, interfaces in self.objects().items():
            if "org.bluez.Adapter1" in interfaces:
                return str(path)
        raise ValueError("未发现蓝牙控制器")

    def status(self):
        try:
            self.register()
            objects = self.objects()
            adapter = self.adapter()
            properties = objects[adapter]["org.bluez.Adapter1"]
        except (dbus.DBusException, ValueError):
            return {"available": False, "error": "蓝牙控制器或 BlueZ 服务暂时不可用", "devices": []}
        devices = []
        for path, interfaces in objects.items():
            device = interfaces.get("org.bluez.Device1")
            if device is None or not str(path).startswith(adapter + "/"):
                continue
            devices.append({"address": str(device["Address"]), "name": str(device.get("Alias", device["Address"])),
                            "paired": bool(device.get("Paired", False)), "connected": bool(device.get("Connected", False)),
                            "trusted": bool(device.get("Trusted", False)), "signal": int(device.get("RSSI", -100)),
                            "icon": str(device.get("Icon", "bluetooth"))})
        devices.sort(key=lambda d: (not d["connected"], not d["paired"], -d["signal"], d["name"]))
        prompt = {key: value for key, value in (self.prompt or {}).items() if key not in ("reply", "error")}
        return {"available": True, "powered": bool(properties.get("Powered", False)),
                "discovering": bool(properties.get("Discovering", False)),
                "discoverable": bool(properties.get("Discoverable", False)),
                "name": str(properties.get("Alias", "Makit Compute")), "devices": devices,
                "prompt": prompt, "job": self.job}

    def ask(self, kind, device, code, reply=None, error=None, entered=0):
        if self.prompt and self.prompt.get("device") == str(device) and kind == "display":
            self.prompt.update(code=code, entered=entered)
            return
        self.clear_prompt()
        self.prompt = {"id": secrets.token_hex(8), "kind": kind, "device": str(device),
                       "name": str(self.properties(str(device), "org.bluez.Device1").get("Alias", device)),
                       "code": code, "entered": entered, "deadline": time.time() + 90,
                       "reply": reply, "error": error}
        identifier = self.prompt["id"]
        def expire():
            if self.prompt and self.prompt["id"] == identifier:
                self.clear_prompt()
            return False
        GLib.timeout_add_seconds(90, expire)

    def clear_prompt(self):
        prompt, self.prompt = self.prompt, None
        if prompt and prompt.get("error"):
            prompt["error"](Rejected("用户取消或配对请求已过期"))

    def answer(self, data):
        prompt = self.prompt
        if not prompt or prompt["id"] != data.get("id") or time.time() >= prompt["deadline"]:
            raise ValueError("配对请求已结束")
        if not isinstance(data.get("accepted"), bool):
            raise ValueError("配对确认参数不正确")
        if not data["accepted"]:
            if prompt["kind"] == "display":
                try:
                    dbus.Interface(self.bus.get_object("org.bluez", prompt["device"]),
                                   "org.bluez.Device1").CancelPairing(timeout=5)
                except dbus.DBusException:
                    pass
            self.clear_prompt()
            return
        kind = prompt["kind"]
        value = str(data.get("value", ""))
        if kind == "pin" and (not 1 <= len(value) <= 16 or "\0" in value):
            raise ValueError("PIN 须为1至16个字符")
        if kind == "passkey" and not re.fullmatch(r"[0-9]{6}", value):
            raise ValueError("请输入6位配对码")
        self.prompt = None
        if kind == "pin":
            prompt["reply"](value)
        elif kind == "passkey":
            prompt["reply"](dbus.UInt32(int(value)))
        elif kind in ("confirm", "authorize"):
            prompt["reply"]()

    def set_property(self, path, name, value):
        dbus.Interface(self.bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties").Set(
            "org.bluez.Adapter1", name, value, timeout=5)

    def finish(self, state, message):
        self.job = {**self.job, "state": state, "message": message}
        self.clear_prompt()

    def device_action(self, action, address):
        if not isinstance(address, str) or not re.fullmatch(r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", address):
            raise ValueError("蓝牙设备地址不正确")
        if self.job.get("state") == "running":
            raise ValueError("蓝牙操作正在进行，请稍候")
        adapter = self.adapter()
        path = adapter + "/dev_" + address.upper().replace(":", "_")
        device = dbus.Interface(self.bus.get_object("org.bluez", path), "org.bluez.Device1")
        self.job = {"state": "running", "action": action, "address": address, "message": "正在处理蓝牙设备"}
        def failed(error):
            if error.get_dbus_name() == "org.bluez.Error.AlreadyConnected" and action in ("pair", "connect"):
                self.finish("complete", "蓝牙设备已连接")
                return
            self.finish("failed", str(error))
        def connected():
            self.finish("complete", "蓝牙设备已连接")
        def connect():
            device.Connect(reply_handler=connected, error_handler=failed, timeout=45)
        def paired():
            try:
                dbus.Interface(self.bus.get_object("org.bluez", path), "org.freedesktop.DBus.Properties").Set(
                    "org.bluez.Device1", "Trusted", dbus.Boolean(True), timeout=5)
                connect()
            except dbus.DBusException as error:
                failed(error)
        try:
            if action == "pair":
                device.Pair(reply_handler=paired, error_handler=failed, timeout=100)
            elif action == "connect":
                connect()
            elif action == "disconnect":
                device.Disconnect(reply_handler=lambda: self.finish("complete", "蓝牙设备已断开"), error_handler=failed, timeout=20)
            elif action == "remove":
                interface = dbus.Interface(self.bus.get_object("org.bluez", adapter), "org.bluez.Adapter1")
                interface.RemoveDevice(path, reply_handler=lambda: self.finish("complete", "配对记录已移除"), error_handler=failed, timeout=20)
        except dbus.DBusException as error:
            failed(error)

    def dispatch(self, action, data):
        if action == "status":
            return self.status()
        self.register()
        if action == "answer":
            self.answer(data)
            return {"ok": True}
        adapter = self.adapter()
        interface = dbus.Interface(self.bus.get_object("org.bluez", adapter), "org.bluez.Adapter1")
        if action == "power":
            if not isinstance(data.get("enabled"), bool):
                raise ValueError("蓝牙开关参数不正确")
            if data["enabled"]:
                with open("/dev/rfkill", "wb", buffering=0) as rfkill:
                    rfkill.write(struct.pack("IBBBB", 0, 2, 3, 0, 0))
            self.set_property(adapter, "Powered", dbus.Boolean(data["enabled"]))
        elif action == "discoverable":
            if not isinstance(data.get("enabled"), bool):
                raise ValueError("可发现开关参数不正确")
            self.set_property(adapter, "DiscoverableTimeout", dbus.UInt32(120))
            self.set_property(adapter, "Pairable", dbus.Boolean(True))
            self.set_property(adapter, "Discoverable", dbus.Boolean(data["enabled"]))
        elif action == "scan":
            interface.StartDiscovery(timeout=5)
            if self.scan_timer:
                GLib.source_remove(self.scan_timer)
            def stop():
                try:
                    interface.StopDiscovery(timeout=5)
                except dbus.DBusException:
                    pass
                self.scan_timer = None
                return False
            self.scan_timer = GLib.timeout_add_seconds(15, stop)
        elif action in ("pair", "connect", "disconnect", "remove"):
            self.device_action(action, data.get("address"))
        else:
            raise ValueError("未知蓝牙操作")
        return {"ok": True}
