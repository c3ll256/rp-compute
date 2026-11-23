"use strict";

let settingsTimer;
let settingsLoading = false;
let systemSettings;
let networkListSignature;
let bluetoothListSignature;
let pairingId;
const pendingNetworkPhases = ["preparing", "connecting", "awaiting_confirmation", "rolling_back"];

function stopSettings() {
  clearTimeout(settingsTimer);
}

function selectView(view) {
  history.replaceState(null, "", location.pathname + location.search + (view === "terminal" ? "" : "#" + view));
  for (const name of ["terminal", "settings", "clash"]) {
    const selected = name === view;
    $(name + "-view").hidden = !selected;
    $("view-" + name).classList.toggle("active", selected);
    if (selected) $("view-" + name).setAttribute("aria-current", "page");
    else $("view-" + name).removeAttribute("aria-current");
  }
  stopSettings();
  stopClash();
  if (view === "settings") refreshSettings();
  else if (view === "clash") refreshClash();
  else resizeTerminal().catch((error) => toast(error.message));
}

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function updatePasswordField() {
  const saved = systemSettings?.network.saved.find((item) => item.ssid === $("wifi-ssid").value);
  $("wifi-saved-label").hidden = !saved || saved.security === "none";
  if (!saved) $("wifi-saved").checked = false;
  $("wifi-security").disabled = $("wifi-saved").checked;
  $("wifi-hidden").disabled = $("wifi-saved").checked;
  if (saved && $("wifi-saved").checked) {
    $("wifi-security").value = saved.security;
    $("wifi-hidden").checked = saved.hidden;
  }
  const needsPassword = $("wifi-security").value !== "none" && !$("wifi-saved").checked;
  $("wifi-password-row").hidden = !needsPassword;
  $("wifi-password").required = needsPassword;
}

function chooseNetwork(network, saved) {
  $("wifi-ssid").value = network.ssid;
  $("wifi-security").value = network.security;
  $("wifi-saved").checked = saved;
  $("wifi-password").value = "";
  updatePasswordField();
  if (!$("wifi-password-row").hidden) $("wifi-password").focus();
}

function renderNetworks(network) {
  const signature = JSON.stringify([network.networks, network.saved]);
  if (signature === networkListSignature) return;
  networkListSignature = signature;
  const list = $("wifi-results");
  list.replaceChildren();
  const found = [...network.networks];
  for (const saved of network.saved) {
    if (!found.some((item) => item.ssid === saved.ssid)) found.push({ ...saved, signal: null });
  }
  for (const item of found) {
    const saved = network.saved.some((profile) => profile.ssid === item.ssid);
    const button = element("button", undefined, "network-option");
    button.type = "button";
    const label = element("span", item.ssid, "device-name");
    const meta = element("span", undefined, "small-text muted");
    const security = { psk: "WPA/WPA2", sae: "WPA3", none: "开放", enterprise: "企业认证", unsupported: "其他认证" }[item.security];
    meta.textContent = [saved ? "已保存" : security, item.signal === null ? "" : item.signal + " dBm"].filter(Boolean).join(" · ");
    button.append(label, meta);
    button.disabled = !["psk", "sae", "none"].includes(item.security);
    button.onclick = () => chooseNetwork(item, saved);
    list.append(button);
  }
}

function renderNetwork(network) {
  $("wifi-current").textContent = network.current.connected ? "已连接 " + network.current.ssid : network.error || "Wi-Fi 尚未连接";
  $("wifi-address").textContent = (network.current.ipv4 || []).join(" / ");
  const change = network.transaction;
  const pending = pendingNetworkPhases.includes(change.phase);
  $("wifi-transaction").hidden = !change.id;
  $("wifi-change-message").textContent = change.message || "";
  $("wifi-countdown").textContent = pending ? `目标网络 ${change.target} · 剩余 ${change.remaining} 秒` : "";
  $("wifi-progress").hidden = !pending;
  $("wifi-progress").value = change.remaining;
  $("wifi-confirm").hidden = change.phase !== "awaiting_confirmation";
  $("wifi-cancel").hidden = !pending || change.phase === "rolling_back";
  $("wifi-connect").disabled = pending || !network.available;
  $("wifi-scan").disabled = pending || network.scanning || !network.available;
  $("wifi-scan").textContent = network.scanning ? "扫描中…" : "扫描网络";
  $("wifi-management-link").href = network.management_url;
  $("wifi-management-link").hidden = false;
  $("network-interfaces").replaceChildren();
  for (const link of network.interfaces) {
    const row = element("div");
    row.append(element("span", link.name), element("span", link.addresses.join(" / ") || "未连接", "muted"));
    $("network-interfaces").append(row);
  }
  renderNetworks(network);
  updatePasswordField();
}

async function settingsAction(button, group, operation, data = {}) {
  await action(button, async () => {
    await api(`/api/settings/${group}/${operation}`, data);
    stopSettings();
    await refreshSettings();
  });
  if (systemSettings) {
    renderNetwork(systemSettings.network);
    renderBluetooth(systemSettings.bluetooth);
  }
}

function renderBluetooth(bluetooth) {
  $("bluetooth-status").textContent = bluetooth.available ? bluetooth.name + (bluetooth.powered ? " · 已开启" : " · 已关闭") : bluetooth.error;
  $("bluetooth-power").textContent = bluetooth.powered ? "关闭蓝牙" : "开启蓝牙";
  $("bluetooth-power").disabled = !bluetooth.available;
  $("bluetooth-scan").disabled = !bluetooth.powered || bluetooth.discovering;
  $("bluetooth-scan").textContent = bluetooth.discovering ? "搜索中…" : "搜索设备";
  $("bluetooth-discoverable").disabled = !bluetooth.powered;
  $("bluetooth-discoverable").textContent = bluetooth.discoverable ? "停止被发现" : "允许被发现";
  const busy = bluetooth.job?.state === "running";
  $("bluetooth-job").hidden = !bluetooth.job?.message;
  $("bluetooth-job").textContent = bluetooth.job?.message || "";
  const signature = JSON.stringify([bluetooth.devices, busy, bluetooth.powered]);
  if (signature !== bluetoothListSignature) {
    bluetoothListSignature = signature;
    const list = $("bluetooth-devices");
    list.replaceChildren();
    if (!bluetooth.devices.length) list.append(element("p", "搜索后会在这里显示设备。", "description"));
    for (const device of bluetooth.devices) {
      const row = element("div", undefined, "bluetooth-device");
      const info = element("div");
      info.append(element("span", device.name, "device-name"), element("span", device.connected ? "已连接" : device.paired ? "已配对" : device.address, "small-text muted"));
      const buttons = element("div", undefined, "device-actions");
      const operation = device.connected ? "disconnect" : device.paired ? "connect" : "pair";
      const button = element("button", { disconnect: "断开", connect: "连接", pair: "配对" }[operation], "secondary");
      button.disabled = busy || !bluetooth.powered;
      button.onclick = () => settingsAction(button, "bluetooth", operation, { address: device.address });
      buttons.append(button);
      if (device.paired) {
        const remove = element("button", "取消配对", "quiet");
        remove.disabled = busy;
        remove.onclick = () => settingsAction(remove, "bluetooth", "remove", { address: device.address });
        buttons.append(remove);
      }
      row.append(info, buttons);
      list.append(row);
    }
  }
  const prompt = bluetooth.prompt || {};
  $("bluetooth-prompt").hidden = !prompt.id;
  if (!prompt.id) { pairingId = null; return; }
  if (pairingId !== prompt.id) $("bluetooth-pin").value = "";
  pairingId = prompt.id;
  $("bluetooth-prompt-title").textContent = "配对 " + prompt.name;
  const instructions = {
    display: "请在蓝牙键盘上输入下方代码，再按回车。",
    confirm: "请核对另一台设备上显示的代码，确认一致后继续。",
    pin: "输入设备提供的 PIN。",
    passkey: "输入设备提供的6位配对码。",
    authorize: "设备请求与这台 Pi 建立蓝牙连接。"
  };
  $("bluetooth-prompt-description").textContent = instructions[prompt.kind];
  $("bluetooth-code").textContent = prompt.code;
  $("bluetooth-code").hidden = !prompt.code;
  const input = ["pin", "passkey"].includes(prompt.kind);
  $("bluetooth-pin-label").hidden = !input;
  $("bluetooth-pin").hidden = !input;
  $("bluetooth-pin").maxLength = prompt.kind === "passkey" ? 6 : 16;
  $("bluetooth-pin").inputMode = prompt.kind === "passkey" ? "numeric" : "text";
  $("bluetooth-accept").hidden = prompt.kind === "display";
}

async function refreshSettings() {
  if (!authenticated || $("settings-view").hidden || settingsLoading) return;
  settingsLoading = true;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    systemSettings = await api("/api/settings", undefined, controller.signal);
    $("settings-error").hidden = true;
    renderNetwork(systemSettings.network);
    renderBluetooth(systemSettings.bluetooth);
  } catch (error) {
    $("settings-error").hidden = false;
    $("settings-error").textContent = "设备暂时无法连接，可通过下方设备名称链接重新打开。网络切换的自动回退会在后台继续执行。";
  } finally {
    clearTimeout(timeout);
    settingsLoading = false;
    stopSettings();
    if (authenticated && !$("settings-view").hidden) settingsTimer = setTimeout(refreshSettings, 2500);
  }
}

$("view-terminal").onclick = () => selectView("terminal");
$("view-settings").onclick = () => selectView("settings");
$("wifi-ssid").oninput = updatePasswordField;
$("wifi-saved").onchange = updatePasswordField;
$("wifi-security").onchange = updatePasswordField;
$("wifi-scan").onclick = () => settingsAction($("wifi-scan"), "network", "scan");
$("wifi-form").onsubmit = async (event) => {
  event.preventDefault();
  await action($("wifi-connect"), async () => {
    await api("/api/settings/network/connect", {
      ssid: $("wifi-ssid").value, password: $("wifi-password").value,
      security: $("wifi-security").value, hidden: $("wifi-hidden").checked, use_saved: $("wifi-saved").checked
    });
    $("wifi-password").value = "";
    toast("已开始切换网络，自动回退已启用");
    stopSettings();
    await refreshSettings();
  });
  if (systemSettings) renderNetwork(systemSettings.network);
};
$("wifi-confirm").onclick = () => settingsAction($("wifi-confirm"), "network", "confirm", { id: systemSettings.network.transaction.id });
$("wifi-cancel").onclick = () => settingsAction($("wifi-cancel"), "network", "cancel", { id: systemSettings.network.transaction.id });
$("bluetooth-power").onclick = () => settingsAction($("bluetooth-power"), "bluetooth", "power", { enabled: !systemSettings.bluetooth.powered });
$("bluetooth-scan").onclick = () => settingsAction($("bluetooth-scan"), "bluetooth", "scan");
$("bluetooth-discoverable").onclick = () => settingsAction($("bluetooth-discoverable"), "bluetooth", "discoverable", { enabled: !systemSettings.bluetooth.discoverable });
$("bluetooth-accept").onclick = () => settingsAction($("bluetooth-accept"), "bluetooth", "answer", { id: pairingId, accepted: true, value: $("bluetooth-pin").value });
$("bluetooth-reject").onclick = () => settingsAction($("bluetooth-reject"), "bluetooth", "answer", { id: pairingId, accepted: false });
