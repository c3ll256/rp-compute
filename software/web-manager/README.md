# Makit Compute 网页管理

在树莓派上提供局域网管理页面，默认监听 `0.0.0.0:8080`。当前样机地址为 `http://192.168.50.83:8080`，使用 `xonar` 的现有 Linux 密码通过 PAM 登录。登录会话有效期为12小时。

## 功能

- 可复制、粘贴和调整尺寸的 xterm.js 网页终端。tmux 保留会话，关闭或刷新浏览器后可以继续操作。网页终端独立于 LCD 显示服务运行，登录凭据由同一用户的 Codex CLI 管理。
- Codex 设备码登录，单独展示可复制的一次性代码与授权链接，并显示真实 CLI 登录输出。
- Codex 浏览器授权。完成 OpenAI 授权后，如果浏览器停在无法访问的 `localhost:1455/auth/callback`，将完整地址粘贴到管理页的回调框，交由 Pi 上的 CLI 校验 OAuth state 并完成令牌交换。
- CPU、内存、磁盘、温度和运行时间，复用显示程序的系统采样逻辑。
- 系统设置页提供 Wi-Fi 扫描、隐藏网络、WPA/WPA2、WPA3、开放网络和已保存密码的连接管理，显示无线及有线接口地址。
- 蓝牙开关、15秒设备搜索、120秒可发现模式、配对确认及PIN输入、连接、断开与取消配对。配对通过 BlueZ D-Bus Agent 接收网页上的明确确认。
- Clash 页控制 Mihomo 的启停、重启、代理模式和策略组，并通过当前代理测试 OpenAI 连通性。

终端使用用户 `xonar` 的 shell，tmux socket 名称为 `makit-web`，会话名称为 `console`。可通过 SSH 执行 `tmux -L makit-web attach -t console` 进入同一会话。

## 安装

需要已安装的显示程序、Codex CLI、`tmux` 和系统 `libpam`。系统设置使用现有 Netplan、systemd-networkd、wpa_supplicant，并需要 `bluez`、`avahi-daemon`、`python3-dbus`、`python3-gi` 和 `python3-yaml`。网页服务器使用 Python 标准库，静态终端依赖随代码打包。xterm.js 版本为6.0.0，addon-fit版本为0.11.0，各自许可证位于 `static/vendor`。网页字体复用显示程序的 Inter。

```sh
sudo sh software/web-manager/install.sh
```

安装后 `makit-web.service` 开机自启动，以 `xonar` 运行，读取该用户的登录 shell 环境以使用已有的电脑代理。独立的 `makit-settings.service` 以 root 运行，通过只允许root及xonar访问的 Unix socket 执行固定的系统设置操作。

```sh
systemctl status makit-web.service
journalctl -u makit-web.service -n 50 --no-pager
```

管理页通过 HTTP 在局域网内提供完整用户终端，登录密码和终端内容会经过该网络连接。管理接口要求密码会话，使用 HttpOnly、SameSite=Strict Cookie，校验 Host 和写请求来源。服务日志省略访问查询参数、终端内容和登录凭据。实际账号授权需要用户在 OpenAI 页面完成。

## Clash 系统代理

Mihomo 通过 `makit-clash.service` 开机启动，HTTP/SOCKS 混合代理监听 `127.0.0.1:7890`。Makit Compute 的 `/#clash` 页面沿用管理页登录，后端经本机 Unix socket 操作 Clash。节点选择会保存，代理模式在服务重启后按配置文件恢复。停止服务期间，使用该代理的程序会暂停联网。

「一键测速」在 Pi 后台通过每个节点请求 OpenAI API，以 HTTP 401 作为匿名请求连通的信号。每批最多并行 8 个节点，单节点超时 5 秒。页面显示进度及各节点延迟，刷新后可以继续查看本轮结果。测速期间仍使用原有的策略和节点选择。

首次部署时，用校验过的 ARM64 二进制、Clash YAML 和 `country.mmdb` 执行安装脚本。输入 YAML 的原件和实际运行配置存放在 `/etc/makit-clash`，凭据只在 Pi 上保存。安装脚本将代理监听限制到本机，将节点 DNS 中的本机地址改为系统 DNS，并启用策略选择缓存。

```sh
sudo python3 software/web-manager/install_clash.py /path/to/mihomo /path/to/config.yaml /path/to/country.mmdb
sudo python3 software/web-manager/install_clash.py --enable-system-proxy
```

系统代理配置覆盖新登录终端、Codex 和 APT。常见局域网地址绕过代理。已有终端可重新登录以刷新环境变量。

## Wi-Fi 切换与回退

1. 在“系统设置”扫描并选择网络，输入密码或使用已保存的密码。企业认证网络可以通过终端配置。
2. 后台服务先以root专属权限备份当前配置，并通过 WPA 控制接口创建临时连接。新连接尝试最多60秒。
3. 新SSID连接成功且获得IPv4地址后，页面显示“保留此网络”。切换与确认共120秒，点击后配置保存到Netplan，并通过 `99-makit-network-config.cfg` 关闭cloud-init的网络配置重新生成。
4. 连接失败、取消或确认超时均自动恢复原配置并重新连接旧网络。网页关闭、SSH中断和网页服务重启后，独立设置服务继续处理回退。设置服务意外退出或Pi在确认前重启时，下次启动先恢复待定事务中的原网络配置。

IP改变后，可以在同一局域网通过 `http://makit-compute.local:8080` 重新进入管理页并登录确认。连接成功的判断使用SSID关联、IPv4地址和用户确认，适用于局域网使用。

备份、保存的网络凭据和事务记录位于 `/var/lib/makit-settings`，目录权限0700、文件权限0600。网络接口当前对应样机内置的 `wlan0`。

## 回归检查

```sh
cd software/web-manager
python3 -m unittest -v test_wifi_settings.py test_bluetooth_settings.py
```

覆盖连接失败、确认超时、取消、连续切换、服务中断、启动时控制接口延迟、保存校验失败、原配置完整恢复、配对拒绝和配对码校验。实机测试已验证不存在网络连接失败后约72秒恢复 `608_5G`，原Netplan文件逐字节一致，并已验证当前SSID的连接确认与配置保存、设置服务被SIGKILL后的独立恢复、Wi-Fi扫描、蓝牙开关及设备搜索。新蓝牙设备的实际配对需要实物设备进入配对模式。
