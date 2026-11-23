"use strict";

const $ = (id) => document.getElementById(id);
let terminal;
let fit;
let events;
let poll;
let toastTimer;
let inputQueue = "";
let inputRunning = false;
let resizeTimer;
let authenticated = false;
let lastCodexState;

function toast(message) {
  $("toast").textContent = message;
  $("toast").hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $("toast").hidden = true; }, 3500);
}

async function api(path, data, signal) {
  const options = { credentials: "same-origin", signal };
  if (data !== undefined) {
    options.method = "POST";
    options.headers = { "Content-Type": "application/json", "X-Makit-Request": "1" };
    options.body = JSON.stringify(data);
  }
  const response = await fetch(path, options);
  const result = await response.json();
  if (response.status === 401 && authenticated) leave();
  if (!response.ok) throw new Error(result.error || "请求失败，请重试");
  return result;
}

async function action(button, callback) {
  button.disabled = true;
  try { await callback(); } catch (error) { toast(error.message); }
  finally { button.disabled = false; }
}

async function copyText(text) {
  if (!text) return toast("暂无可复制的内容");
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      const field = document.createElement("textarea");
      field.value = text;
      field.style.position = "fixed";
      field.style.left = "-10000px";
      document.body.appendChild(field);
      field.select();
      field.setSelectionRange(0, text.length);
      const copied = document.execCommand("copy");
      field.remove();
      if (!copied) throw new Error("copy denied");
    }
    toast("已复制");
  } catch (_) {
    $("paste-panel").hidden = false;
    $("paste-text").value = text;
    $("paste-text").focus();
    $("paste-text").select();
    toast("文字已选中，请按复制快捷键或长按复制");
  }
}

function encode(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  for (const value of bytes) binary += String.fromCharCode(value);
  return btoa(binary);
}

async function sendInput(text) {
  inputQueue += text;
  if (inputRunning) return;
  inputRunning = true;
  try {
    while (inputQueue) {
      let count = Math.min(4000, inputQueue.length);
      if (count < inputQueue.length && /[\uD800-\uDBFF]/.test(inputQueue[count - 1])) count--;
      const chunk = inputQueue.slice(0, count);
      await api("/api/terminal/input", { data: encode(chunk) });
      inputQueue = inputQueue.slice(count);
    }
  } catch (error) {
    inputQueue = "";
    toast(error.message);
  } finally { inputRunning = false; }
}

function setConnection(connected) {
  $("connection").classList.toggle("connected", connected);
  $("connection").lastChild.textContent = connected ? "设备在线" : "正在重连";
}

async function resizeTerminal() {
  if (!terminal || !authenticated || $("terminal-view").hidden) return;
  fit.fit();
  $("terminal-size").textContent = `${terminal.cols} × ${terminal.rows}`;
  await api("/api/terminal/resize", { columns: terminal.cols, rows: terminal.rows });
}

async function openTerminal() {
  terminal = new Terminal({
    fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
    fontSize: window.innerWidth < 760 ? 12 : 13,
    lineHeight: 1.3,
    fontWeight: "400",
    fontWeightBold: "700",
    cursorBlink: true,
    cursorStyle: "bar",
    scrollback: 5000,
    convertEol: false,
    theme: {
      background: "#ffffff", foreground: "#292923", cursor: "#252520",
      selectionBackground: "#d8e1e4", black: "#272721", red: "#a83b32", green: "#426347",
      yellow: "#8c6b22", blue: "#3c6083", magenta: "#79577d", cyan: "#3c7373", white: "#d8d8d0",
      brightBlack: "#85857c", brightRed: "#a83b32", brightGreen: "#387047", brightYellow: "#8b6d20",
      brightBlue: "#3d6a94", brightMagenta: "#7c547c", brightCyan: "#327c82", brightWhite: "#eeeeea"
    }
  });
  fit = new FitAddon.FitAddon();
  terminal.loadAddon(fit);
  terminal.open($("terminal"));
  terminal.onData(sendInput);
  terminal.attachCustomKeyEventHandler((event) => {
    if (event.type === "keydown" && (event.metaKey || event.ctrlKey && event.shiftKey)
        && event.key.toLowerCase() === "c" && terminal.hasSelection()) {
      copyText(terminal.getSelection());
      return false;
    }
    return true;
  });
  await resizeTerminal();
  events = new EventSource("/api/terminal/events");
  events.onopen = () => setConnection(true);
  events.onerror = () => setConnection(false);
  events.addEventListener("reset", () => terminal.reset());
  events.addEventListener("expired", () => { leave(); toast("登录已过期，请重新登录"); });
  events.addEventListener("output", (event) => {
    const binary = atob(JSON.parse(event.data));
    terminal.write(Uint8Array.from(binary, (char) => char.charCodeAt(0)));
  });
  terminal.focus();
}

function percent(used, total) { return total ? Math.round(used / total * 100) : null; }
function metric(id, value, suffix = "%") {
  $(id + "-value").textContent = value === null ? "—" : value + suffix;
  if ($(id + "-bar")) $(id + "-bar").value = value || 0;
}

function renderLogin(login) {
  lastCodexState = login;
  $("codex-version").textContent = login.version;
  $("codex-state").textContent = login.logged_in ? "已登录" : "未登录";
  const active = login.state === "running" || login.state === "failed";
  $("codex-login-options").hidden = login.logged_in || active;
  $("codex-active").hidden = login.logged_in || !active;
  $("codex-ready").hidden = !login.logged_in;
  $("auth-output").textContent = login.output;
  $("device-code-row").hidden = !login.code || login.mode !== "device";
  $("device-code").value = login.code;
  $("auth-link").hidden = !login.url;
  $("copy-auth-link").hidden = !login.url;
  if (login.url) $("auth-link").href = login.url;
  $("callback-form").hidden = login.mode !== "browser" || login.state !== "running" || !login.url;
  $("cancel-auth").textContent = login.state === "failed" ? "重新选择登录方式" : "取消登录";
  if (login.state === "failed") {
    $("auth-message").textContent = "登录未完成。可查看详情，或改用浏览器授权。";
    $("auth-details").open = true;
  } else if (login.mode === "browser") {
    $("auth-message").textContent = login.url ? "打开授权页面，使用你的 ChatGPT 账号登录。" : "正在准备授权链接…";
  } else {
    $("auth-message").textContent = login.code ? "复制下方代码，再打开授权页面填写。代码有效期为 15 分钟。" : "正在向 OpenAI 申请一次性代码…";
  }
}

async function refreshStatus() {
  try {
    const data = await api("/api/status");
    const m = data.metrics;
    $("host-label").textContent = `${m.hostname} / ${m.address || location.hostname}`;
    $("device-hostname").textContent = m.hostname;
    $("device-address").textContent = m.address || "";
    $("terminal-command").textContent = data.terminal_command || "终端";
    $("launch-codex").disabled = !["bash", "zsh", "sh", "fish", "-bash"].includes(data.terminal_command);
    metric("cpu", m.cpu_percent === null ? null : Math.round(m.cpu_percent));
    metric("memory", percent(m.memory_used, m.memory_total));
    metric("disk", percent(m.disk_used, m.disk_total));
    metric("temperature", m.temperature === null ? null : Math.round(m.temperature), "°C");
    const minutes = Math.floor((m.uptime || 0) / 60);
    $("uptime-value").textContent = minutes >= 1440 ? `${Math.floor(minutes / 1440)} 天 ${Math.floor(minutes % 1440 / 60)} 小时`
      : minutes >= 60 ? `${Math.floor(minutes / 60)} 小时 ${minutes % 60} 分` : `${minutes} 分钟`;
    renderLogin(data.codex);
  } catch (error) { setConnection(false); }
  finally { if (authenticated) poll = setTimeout(refreshStatus, 2000); }
}

async function enter() {
  authenticated = true;
  $("sign-in").hidden = true;
  $("workspace").hidden = false;
  const view = location.hash.slice(1);
  selectView(["settings", "clash"].includes(view) ? view : "terminal");
  try { await openTerminal(); } catch (error) { toast(error.message); }
  refreshStatus();
}

function leave() {
  authenticated = false;
  if (typeof stopSettings === "function") stopSettings();
  stopClash();
  clearTimeout(poll);
  events?.close();
  terminal?.dispose();
  terminal = null;
  $("terminal").replaceChildren();
  $("workspace").hidden = true;
  $("sign-in").hidden = false;
}

$("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("login-error").textContent = "";
  $("sign-in-button").disabled = true;
  try {
    await api("/api/login", { username: $("username").value, password: $("password").value });
    $("password").value = "";
    await enter();
  } catch (error) { $("login-error").textContent = error.message; }
  finally { $("sign-in-button").disabled = false; }
});

$("sign-out").onclick = () => action($("sign-out"), async () => { await api("/api/logout", {}); leave(); });
$("launch-codex").onclick = () => action($("launch-codex"), async () => { await api("/api/terminal/codex", {}); terminal.focus(); });
$("interrupt").onclick = () => { sendInput("\x03"); terminal?.focus(); };
$("paste-open").onclick = () => { $("paste-panel").hidden = false; $("paste-text").value = ""; $("paste-text").focus(); };
$("paste-cancel").onclick = () => { $("paste-panel").hidden = true; terminal?.focus(); };
$("paste-send").onclick = () => {
  if (terminal) terminal.paste($("paste-text").value);
  $("paste-panel").hidden = true;
  $("paste-text").value = "";
  terminal?.focus();
};
$("copy-terminal").onclick = () => {
  if (!terminal) return;
  if (terminal.hasSelection()) return copyText(terminal.getSelection());
  const buffer = terminal.buffer.active;
  let text = "";
  for (let index = 0; index < buffer.length; index++) {
    const line = buffer.getLine(index);
    text += (line.isWrapped ? "" : "\n") + line.translateToString(true);
  }
  copyText(text.trim());
};

async function startLogin(mode, button) {
  await action(button, async () => {
    await api("/api/codex/login", { mode });
    $("auth-details").open = false;
    $("callback-url").value = "";
    clearTimeout(poll);
    await refreshStatus();
  });
}
$("device-login").onclick = () => startLogin("device", $("device-login"));
$("browser-login").onclick = () => startLogin("browser", $("browser-login"));
$("copy-code").onclick = () => copyText($("device-code").value);
$("copy-auth-link").onclick = () => copyText(lastCodexState?.url);
$("cancel-auth").onclick = () => action($("cancel-auth"), async () => {
  await api("/api/codex/cancel", {});
  clearTimeout(poll);
  await refreshStatus();
});
$("callback-form").onsubmit = (event) => {
  event.preventDefault();
  action($("callback-send"), async () => {
    await api("/api/codex/callback", { url: $("callback-url").value });
    $("callback-url").value = "";
    toast("回调已交给 Codex，正在确认登录状态");
    clearTimeout(poll);
    await refreshStatus();
  });
};

window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => resizeTerminal().catch((error) => toast(error.message)), 150);
});

(async () => {
  try {
    const data = await api("/api/public");
    $("username").value = data.username;
    if (data.authenticated) await enter();
  } catch (_) { $("login-error").textContent = "设备暂时无法连接，请刷新重试"; }
})();
