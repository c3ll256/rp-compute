"""Pairing-code and consent regression tests without contacting nearby devices."""

from types import SimpleNamespace
import time
import unittest
from unittest.mock import Mock, patch

import dbus

from bluetooth_settings import Agent, BluetoothSettings


class PairingTests(unittest.TestCase):
    def setUp(self):
        self.manager = BluetoothSettings.__new__(BluetoothSettings)
        self.replies = []
        self.errors = []
        self.manager.prompt = {"id": "test-request", "kind": "confirm", "deadline": time.time() + 60,
                               "reply": lambda *args: self.replies.append(args), "error": self.errors.append}

    def test_confirmation_requires_explicit_boolean(self):
        with self.assertRaises(ValueError):
            self.manager.answer({"id": "test-request", "accepted": "false"})
        self.assertFalse(self.replies)
        self.manager.answer({"id": "test-request", "accepted": True})
        self.assertEqual(self.replies, [()])
        self.assertIsNone(self.manager.prompt)

    def test_decline_and_expiry(self):
        self.manager.answer({"id": "test-request", "accepted": False})
        self.assertEqual(len(self.errors), 1)
        self.assertFalse(self.replies)
        with self.assertRaises(ValueError):
            self.manager.answer({"id": "test-request", "accepted": True})

    def test_passkey_keeps_leading_zeroes_and_validates_length(self):
        self.manager.prompt["kind"] = "passkey"
        with self.assertRaises(ValueError):
            self.manager.answer({"id": "test-request", "accepted": True, "value": "123"})
        self.manager.answer({"id": "test-request", "accepted": True, "value": "000123"})
        self.assertEqual(int(self.replies[0][0]), 123)

    def test_agent_display_and_confirmation(self):
        calls = []
        agent = SimpleNamespace(manager=SimpleNamespace(ask=lambda *a, **kw: calls.append((a, kw))))
        Agent.DisplayPasskey(agent, "/test/device", 12, 2)
        self.assertEqual(calls[0][0], ("display", "/test/device", "000012"))
        self.assertEqual(calls[0][1], {"entered": 2})
        Agent.RequestConfirmation(agent, "/test/device", 34, "reply", "error")
        self.assertEqual(calls[1][0], ("confirm", "/test/device", "000034", "reply", "error"))

    def test_disappearing_device_releases_running_job(self):
        self.manager.job = {"state": "idle"}
        self.manager.adapter = lambda: "/org/bluez/hci0"
        self.manager.bus = SimpleNamespace(get_object=lambda *args: object())
        error = dbus.DBusException("Device disappeared", name="org.bluez.Error.DoesNotExist")
        device = SimpleNamespace(Pair=Mock(side_effect=error))
        with patch("bluetooth_settings.dbus.Interface", return_value=device):
            self.manager.device_action("pair", "AA:BB:CC:DD:EE:FF")
        self.assertEqual(self.manager.job["state"], "failed")


if __name__ == "__main__":
    unittest.main()
