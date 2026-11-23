"use strict";

let clashTimer;
let clashGroups = [];
let clashSignature;
let clashMode;
let clashLoading = false;
let clashChanging = false;
let clashReady = false;
let clashStatus;
let delayScan;
let delaySignature;
let delayStarting = false;

function stopClash() {
  clearTimeout(clashTimer);
}

function selectedGroup() {
  return clashGroups.find((group) => group.name === $("clash-group").value);
}

function renderClashNodes() {
  const group = selectedGroup();
  const options = group?.options || [];
  $("clash-node").replaceChildren(...options.map((name) => new Option(name, name)));
  $("clash-node").value = group?.selected || "";
  $("clash-routing-status").textContent = group ? "当前选择：" + (group.selected || "—") : "暂无可切换的策略组";
  renderClashControlState();
}

function renderClashControlState() {
  const group = selectedGroup();
  $("clash-mode").disabled = !clashReady || clashChanging;
  $("clash-apply-mode").disabled = !clashReady || clashChanging || $("clash-mode").value === clashMode;
  $("clash-group").disabled = !clashReady || clashChanging || !clashGroups.length;
  $("clash-node").disabled = !clashReady || clashChanging || !group;
  $("clash-apply-node").disabled = !clashReady || clashChanging || !group || $("clash-node").value === group.selected;
}

function renderClash(data) {
  clashStatus = data;
  const running = data.state === "active";
  const starting = data.state === "activating" || data.state === "deactivating";
  $("clash-state").textContent = running ? "运行中" : starting ? "切换中" : data.state === "failed" ? "启动失败" : "已停止";
  $("clash-version").textContent = data.version ? "Mihomo " + data.version : "";
  $("clash-address").textContent = data.address;
  $("clash-message").textContent = data.error || (running ? "代理随 Pi 开机启动。" : "启动后，使用系统代理的应用将恢复连接。");
  $("clash-start").disabled = running || starting || clashChanging;
  $("clash-restart").disabled = !running || starting || clashChanging;
  $("clash-stop").disabled = !running || starting || clashChanging;
  $("clash-test").disabled = !data.available || clashChanging;
  clashReady = data.available;
  if (clashMode !== data.mode) {
    clashMode = data.mode;
    if (clashMode) $("clash-mode").value = clashMode;
  }
  const signature = JSON.stringify(data.groups);
  if (data.available && signature !== clashSignature) {
    const previousGroup = $("clash-group").value;
    clashGroups = data.groups;
    clashSignature = signature;
    $("clash-group").replaceChildren(...clashGroups.map(({ name }) => new Option(name, name)));
    if (clashGroups.some(({ name }) => name === previousGroup)) $("clash-group").value = previousGroup;
    else if (clashGroups.some(({ name }) => name === "Proxies")) $("clash-group").value = "Proxies";
    renderClashNodes();
  }
  renderClashControlState();
  renderDelayScan(data.delay_scan);
}

function renderDelayRows() {
  const filter = $("clash-delay-filter").value.trim().toLowerCase();
  const results = delayScan.results.filter(({ name, provider }) =>
    name.toLowerCase().includes(filter) || provider.toLowerCase().includes(filter));
  const rank = { ok: 0, waiting: 1, timeout: 2, failed: 3 };
  results.sort((a, b) => rank[a.state] - rank[b.state] ||
    (a.delay || 0) - (b.delay || 0) || a.name.localeCompare(b.name));
  const rows = results.map((result) => {
    const row = document.createElement("tr");
    const node = document.createElement("td");
    node.textContent = result.name;
    if (result.provider) {
      const provider = document.createElement("small");
      provider.textContent = result.provider;
      node.append(provider);
    }
    const delay = document.createElement("td");
    delay.dataset.state = result.state;
    const waiting = delayScan.phase === "running" ? "待测" : "未测";
    delay.textContent = result.state === "ok" ? result.delay + " ms" :
      { waiting, timeout: "超时", failed: "未连通" }[result.state];
    row.append(node, delay);
    return row;
  });
  if (!rows.length) {
    const row = document.createElement("tr");
    const empty = document.createElement("td");
    empty.colSpan = 2;
    empty.textContent = "没有匹配的节点";
    row.append(empty);
    rows.push(row);
  }
  $("clash-delay-rows").replaceChildren(...rows);
}

function renderDelayScan(scan) {
  delayScan = scan || { phase: "idle", results: [] };
  const { phase, results } = delayScan;
  const running = phase === "running";
  $("clash-scan").disabled = !clashReady || running || delayStarting;
  $("clash-scan").textContent = running || delayStarting ? "测速中…" : "一键测速";
  $("clash-delay-progress").hidden = !running;
  $("clash-delay-results").hidden = !results.length;
  $("clash-delay-summary").hidden = phase === "idle";
  const signature = JSON.stringify(delayScan);
  if (signature === delaySignature) return;
  delaySignature = signature;
  const counts = { waiting: 0, ok: 0, failed: 0, timeout: 0 };
  for (const result of results) counts[result.state]++;
  const done = results.length - counts.waiting;
  $("clash-delay-progress").max = Math.max(1, results.length);
  $("clash-delay-progress").value = done;
  const label = { running: "测速中", complete: "测速完成", interrupted: "测速已中断", failed: "测速未完成" }[phase];
  if (label) {
    $("clash-delay-summary").textContent =
      `${label} · ${done}/${results.length} · ${counts.ok} 个可用 · ${counts.timeout} 个超时 · ${counts.failed} 个未连通`;
  }
  if (results.length) renderDelayRows();
}

async function startDelayScan() {
  if (!clashReady || delayStarting || delayScan.phase === "running") return;
  delayStarting = true;
  renderDelayScan(delayScan);
  try {
    await api("/api/settings/clash/scan", {}, AbortSignal.timeout(12000));
  } catch (error) {
    toast(error.message);
  } finally {
    delayStarting = false;
    await refreshClash();
  }
}

async function refreshClash() {
  if (!authenticated || $("clash-view").hidden || clashLoading) return;
  clashLoading = true;
  try {
    renderClash(await api("/api/clash", undefined, AbortSignal.timeout(8000)));
  } catch (error) {
    $("clash-message").textContent = error.message;
  } finally {
    clashLoading = false;
    stopClash();
    if (authenticated && !$("clash-view").hidden) {
      clashTimer = setTimeout(refreshClash, delayScan?.phase === "running" ? 2000 : 4000);
    }
  }
}

async function clashAction(operation, data = {}) {
  if (clashChanging) return;
  clashChanging = true;
  renderClash(clashStatus);
  $("clash-test-result").hidden = operation !== "test";
  if (operation === "test") $("clash-test-result").textContent = "正在通过当前代理请求 OpenAI…";
  try {
    const result = await api("/api/settings/clash/" + operation, data, AbortSignal.timeout(26000));
    if (operation === "test") {
      $("clash-test-result").textContent = result.reachable ? "已连通 OpenAI" :
        (result.http_status ? "OpenAI 返回 HTTP " + result.http_status : "代理请求未连通");
    } else {
      toast("已应用 Clash 设置");
    }
  } catch (error) {
    if (operation === "test") $("clash-test-result").textContent = error.message;
    else toast(error.message);
  } finally {
    clashChanging = false;
    renderClash(clashStatus);
    await refreshClash();
  }
}

$("view-clash").onclick = () => selectView("clash");
$("clash-mode").onchange = renderClashControlState;
$("clash-group").onchange = () => renderClashNodes();
$("clash-node").onchange = renderClashControlState;
$("clash-scan").onclick = startDelayScan;
$("clash-delay-filter").oninput = renderDelayRows;
for (const operation of ["start", "restart", "stop", "test"]) {
  $("clash-" + operation).onclick = () => clashAction(operation);
}
$("clash-mode-form").onsubmit = (event) => {
  event.preventDefault();
  clashAction("mode", { mode: $("clash-mode").value });
};
$("clash-group-form").onsubmit = (event) => {
  event.preventDefault();
  clashAction("select", { group: $("clash-group").value, node: $("clash-node").value });
};
