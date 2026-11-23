"""Hot-plugged Linux keyboards routed to the LCD interface."""

import logging
from pathlib import Path
import queue
import selectors
import shlex
import threading
import time


LOG = logging.getLogger("rp-keyboard")


class Keymap:
    def __init__(self, device):
        from evdev import ecodes as e
        from xkbcommon import xkb

        self.xkb = xkb
        names = {"rules": "evdev", "model": "pc105", "layout": "us"}
        path = Path("/etc/default/keyboard")
        if path.exists():
            for line in path.read_text().splitlines():
                key, separator, value = line.partition("=")
                if separator and key in ("XKBMODEL", "XKBLAYOUT", "XKBVARIANT", "XKBOPTIONS"):
                    values = shlex.split(value)
                    names[key[3:].lower()] = values[0] if values else ""
        self.context = xkb.Context()
        self.keymap = self.context.keymap_new_from_names(**names)
        self.state = self.keymap.state_new()
        self.compose = self.context.compose_table_new_from_locale("C.UTF-8").compose_state_new()
        leds = device.leds()
        for led, code in ((e.LED_CAPSL, e.KEY_CAPSLOCK), (e.LED_NUML, e.KEY_NUMLOCK)):
            if led in leds:
                self.state.update_key(code + 8, xkb.KeyDirection.XKB_KEY_DOWN)
                self.state.update_key(code + 8, xkb.KeyDirection.XKB_KEY_UP)
        for code in device.active_keys():
            self.state.update_key(code + 8, xkb.KeyDirection.XKB_KEY_DOWN)

    def event(self, event):
        xkb = self.xkb
        key = event.code + 8
        if event.value != 2:
            direction = xkb.KeyDirection.XKB_KEY_DOWN if event.value else xkb.KeyDirection.XKB_KEY_UP
            self.state.update_key(key, direction)
        if event.value == 0:
            return None
        component = xkb.StateComponent.XKB_STATE_MODS_EFFECTIVE
        shift = self.state.mod_name_is_active("Shift", component)
        alt = self.state.mod_name_is_active("Mod1", component)
        control = self.state.mod_name_is_active("Control", component)
        symbol = self.state.key_get_one_sym(key)
        name = xkb.keysym_get_name(symbol).removeprefix("KP_")
        name = {"Prior": "Page_Up", "Next": "Page_Down"}.get(name, name)
        text = self.state.key_get_string(key)
        if not control and not alt:
            self.compose.feed(symbol)
            status = self.compose.get_status()
            if status == xkb.ComposeStatus.XKB_COMPOSE_COMPOSING:
                text = ""
            elif status == xkb.ComposeStatus.XKB_COMPOSE_COMPOSED:
                text = self.compose.get_utf8()
                self.compose.reset()
            elif status == xkb.ComposeStatus.XKB_COMPOSE_CANCELLED:
                text = ""
                self.compose.reset()
        return name, text, shift, alt, control


class KeyboardInput:
    def __init__(self):
        self.actions = queue.Queue(maxsize=2048)
        self.attached = 0
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, name="lcd-keyboards", daemon=True)

    def start(self):
        # Validate the optional Linux dependencies before starting the worker.
        import evdev
        from xkbcommon import xkb
        self.thread.start()

    def put(self, action):
        try:
            self.actions.put_nowait(action)
        except queue.Full:
            LOG.warning("Keyboard input queue full")

    def run(self):
        from evdev import InputDevice, ecodes as e, list_devices

        devices = {}
        rejected = set()
        dropped = set()
        selector = selectors.DefaultSelector()

        def remove(path):
            device, _ = devices.pop(path)
            selector.unregister(device)
            device.close()  # Closing also releases the exclusive grab.
            dropped.discard(path)
            self.attached = len(devices)
            LOG.info("Keyboard disconnected: %s", path)

        next_scan = 0
        try:
            while not self.stopped.is_set():
                if time.monotonic() >= next_scan:
                    paths = set(list_devices())
                    for path in list(devices):
                        if path not in paths:
                            remove(path)
                    rejected.intersection_update(paths)
                    for path in paths - devices.keys():
                        device = None
                        try:
                            device = InputDevice(path)
                            keys = device.capabilities().get(e.EV_KEY, [])
                            if not {e.KEY_A, e.KEY_ENTER, e.KEY_SPACE}.issubset(keys):
                                device.close()
                                continue
                            device.grab()
                            keymap = Keymap(device)
                            selector.register(device, selectors.EVENT_READ)
                            devices[path] = device, keymap
                            self.attached = len(devices)
                            rejected.discard(path)
                            LOG.info("Keyboard connected: %s (%s)", device.name, path)
                        except Exception as error:
                            if device is not None:
                                device.close()
                            if path not in rejected:
                                LOG.warning("Keyboard unavailable %s: %s", path, error)
                                rejected.add(path)
                    next_scan = time.monotonic() + 1
                for selected, _ in selector.select(timeout=0.1):
                    device = selected.fileobj
                    path = device.path
                    try:
                        for event in device.read():
                            if event.type == e.EV_SYN and event.code == e.SYN_DROPPED:
                                dropped.add(path)
                            elif path in dropped:
                                if event.type == e.EV_SYN and event.code == e.SYN_REPORT:
                                    devices[path] = device, Keymap(device)
                                    dropped.remove(path)
                            elif event.type == e.EV_KEY:
                                keymap = devices[path][1]
                                key = keymap.event(event)
                                if key is None:
                                    continue
                                _, _, _, alt, control = key
                                if event.code == e.KEY_T and alt and control:
                                    keymap.compose.reset()
                                    if event.value == 1:
                                        self.put(("toggle", None))
                                elif key[0] not in ("Shift_L", "Shift_R", "Control_L", "Control_R",
                                                   "Alt_L", "Alt_R", "ISO_Level3_Shift", "Caps_Lock", "Num_Lock"):
                                    self.put(("key", key))
                                if event.code in (e.KEY_CAPSLOCK, e.KEY_NUMLOCK) and event.value == 1:
                                    component = keymap.xkb.StateComponent.XKB_STATE_MODS_EFFECTIVE
                                    try:
                                        device.set_led(e.LED_CAPSL, int(keymap.state.mod_name_is_active("Lock", component)))
                                        device.set_led(e.LED_NUML, int(keymap.state.mod_name_is_active("Mod2", component)))
                                    except OSError:
                                        pass
                    except BlockingIOError:
                        continue
                    except OSError:
                        remove(path)
                    except Exception:
                        LOG.exception("Keyboard event failed: %s", path)
                        remove(path)
        finally:
            for path in list(devices):
                remove(path)
            selector.close()

    def close(self):
        self.stopped.set()
        if self.thread.ident is not None:
            self.thread.join(timeout=2)
