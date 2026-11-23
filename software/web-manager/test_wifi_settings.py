"""Regression coverage for the Wi-Fi rollback transaction, using an isolated fake radio."""

import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import yaml

from wifi_settings import WiFiSettings


class FakeRadio:
    def __init__(self):
        self.ssid = "old-network"
        self.configured_ssid = "old-network"
        self.target = ""
        self.connects = True
        self.reconfigure_failures = 0
        self.commands = []

    def request(self, command):
        self.commands.append(command)
        if command == "ADD_NETWORK":
            return "1"
        if command.startswith("SET_NETWORK 1 ssid "):
            self.target = bytes.fromhex(command.split()[-1]).decode()
        if command == "SELECT_NETWORK 1":
            self.ssid = self.target if self.connects else ""
        if command == "RECONFIGURE":
            if self.reconfigure_failures:
                self.reconfigure_failures -= 1
                raise FileNotFoundError("simulated early-boot control socket")
            self.ssid = self.configured_ssid
        return "OK"


class FakeWiFi(WiFiSettings):
    fail_generation_once = False

    def current(self):
        return {"ssid": self.control.ssid, "connected": bool(self.control.ssid),
                "ipv4": ["192.0.2.10"] if self.control.ssid else [], "state": "COMPLETED"}

    def generate(self):
        if self.fail_generation_once:
            self.fail_generation_once = False
            raise ValueError("simulated validation failure")
        config = yaml.safe_load(next(self.netplan.glob('*.yaml')).read_text())
        self.control.configured_ssid = next(iter(config['network']['wifis']['wlan0'].get('access-points', {})), '')


class WiFiTransactionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        self.netplan = self.root / "netplan"
        self.netplan.mkdir()
        self.original = b'# original configuration\nnetwork:\n  version: 2\n  ethernets:\n    eth0:\n      dhcp4: true\n  wifis:\n    wlan0:\n      dhcp4: true\n      access-points:\n        old-network:\n          password: old-password\n'
        self.config = self.netplan / "50-cloud-init.yaml"
        self.config.write_bytes(self.original)
        self.radio = FakeRadio()
        self.cloud_config = self.root / "cloud" / "99-makit-network-config.cfg"
        self.cloud_config.parent.mkdir()
        self.manager = FakeWiFi(self.root / "state", self.netplan, self.radio,
                                connect_timeout=.05, confirm_timeout=5, cloud_config=self.cloud_config)

    def tearDown(self):
        if self.manager.state.get("phase") in ("preparing", "connecting", "awaiting_confirmation"):
            self.manager.cancel.set()
            self.wait("rolled_back")
        self.directory.cleanup()

    def wait(self, phase):
        until = time.monotonic() + 8
        while time.monotonic() < until:
            if self.manager.state["phase"] == phase:
                return
            time.sleep(.01)
        self.fail("Transaction did not reach " + phase + ": " + self.manager.state["phase"])

    def begin(self):
        return self.manager.begin({"ssid": "new-network", "password": "new-password", "security": "psk"})

    def test_failed_connection_restores_exact_old_files(self):
        self.radio.connects = False
        self.begin()
        self.wait("rolled_back")
        self.assertEqual(self.radio.ssid, "old-network")
        self.assertEqual(self.config.read_bytes(), self.original)

    def test_no_browser_confirmation_rolls_back(self):
        self.manager.confirm_timeout = 2
        self.begin()
        self.wait("awaiting_confirmation")
        self.wait("rolled_back")
        self.assertEqual(self.radio.ssid, "old-network")

    def test_confirmation_persists_new_network_and_retains_saved_old(self):
        identifier = self.begin()
        self.wait("awaiting_confirmation")
        self.assertEqual(self.config.read_bytes(), self.original)
        self.manager.confirm(identifier)
        self.assertEqual(self.manager.state["phase"], "connected")
        config = yaml.safe_load(self.config.read_text())["network"]
        self.assertTrue(config["ethernets"]["eth0"]["dhcp4"])
        self.assertIn("new-network", config["wifis"]["wlan0"]["access-points"])
        self.assertIn("old-network", self.manager.known_profiles())
        self.assertEqual(yaml.safe_load(self.cloud_config.read_text())["network"]["config"], "disabled")
        self.assertNotIn("new-password", self.config.read_text())
        self.assertNotIn("password", json.dumps(self.manager.state))

    def test_cancel_and_duplicate_transaction(self):
        identifier = self.begin()
        with self.assertRaises(ValueError):
            self.begin()
        with self.assertRaises(ValueError):
            self.manager.confirm("stale-transaction")
        self.manager.cancel_change(identifier)
        self.wait("rolled_back")

    def test_immediate_next_transaction_has_its_own_worker(self):
        identifier = self.begin()
        self.wait("awaiting_confirmation")
        self.manager.confirm(identifier)
        confirmed = self.config.read_bytes()
        self.radio.connects = False
        self.manager.begin({"ssid": "third-network", "password": "another-password", "security": "psk"})
        self.wait("rolled_back")
        self.assertEqual(self.radio.ssid, "new-network")
        self.assertEqual(self.config.read_bytes(), confirmed)

    def test_restart_recovers_partially_written_configuration(self):
        with patch("threading.Thread.start"):
            self.begin()
        self.config.write_text("network: {version: 2, wifis: {}}\n")
        self.cloud_config.write_text("network: {config: disabled}\n")
        recovered = FakeWiFi(self.root / "state", self.netplan, self.radio, cloud_config=self.cloud_config)
        recovered.recover()
        self.assertEqual(recovered.state["phase"], "rolled_back")
        self.assertEqual(self.config.read_bytes(), self.original)
        self.assertFalse(self.cloud_config.exists())
        self.manager = recovered

    def test_validation_failure_during_confirmation_restores_old(self):
        identifier = self.begin()
        self.wait("awaiting_confirmation")
        self.manager.fail_generation_once = True
        with self.assertRaises(ValueError):
            self.manager.confirm(identifier)
        self.wait("rolled_back")
        self.assertEqual(self.config.read_bytes(), self.original)

    def test_unicode_ssid_and_password_validation(self):
        ssid, profile = self.manager.profile({"ssid": '中文 " Wi-Fi', "password": "valid-password"})
        self.assertEqual(ssid, '中文 " Wi-Fi')
        self.assertEqual(len(profile["auth"]["password"]), 64)
        with self.assertRaises(ValueError):
            self.manager.profile({"ssid": "network", "password": "short"})
        self.assertEqual(self.manager.state["phase"], "idle")

    def test_recovery_waits_for_early_boot_control_socket(self):
        with patch("threading.Thread.start"):
            self.begin()
        self.radio.reconfigure_failures = 2
        self.manager.recover()
        self.assertEqual(self.manager.state["phase"], "rolled_back")

    def test_scan_security_keeps_unsupported_networks_distinct(self):
        for flags, expected in (("[WPA2-PSK+SAE-CCMP]", "psk"), ("[SAE-CCMP]", "sae"),
                                ("[WPA2-EAP-CCMP]", "enterprise"), ("[WEP][ESS]", "unsupported"),
                                ("[OWE-CCMP]", "unsupported"), ("[ESS]", "none")):
            self.assertEqual(self.manager.scan_security(flags), expected)


if __name__ == "__main__":
    unittest.main()
