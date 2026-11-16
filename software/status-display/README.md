# rp-compute 状态与动态角色

400×240 黑白状态屏，面向当前 Pi 4B 基板及实物 Sharp LS027B7DH01A。复用 `../display-test/display_test.py` 中已完成上机测试的电源、SPI、COM 与清屏逻辑。

顶部固定显示 Makit Compute，右侧展示 Hermes 任务阶段、工具名称、任务耗时、已完成工具数和并行任务数。CPU、内存、温度和根分区占用缩为底部四个分段条形图，并附小号数值，左下方显示 IPv4 地址。指标每秒采样，角色默认按 60fps 目标绘制。系统采样与 Hermes 事件接收分别在独立线程执行。指标缺失显示 `--`，采样超过 5 秒时显示 Metrics unavailable。

## 角色与状态

角色依据用户提供的 Grok Bot 图片重绘为圆形黑色主体，两只不同大小的白色胶囊眼睛位于右上部，默认倾斜约 25°。角色动作由 Hermes 的实际任务阶段驱动，空闲时根据系统低负载情况进入休息状态。不同状态使用不同的起伏节奏、轻微拉伸、摇摆、视线、眨眼与小型状态特效。[官方动效参考](https://x.ai/news/designing-grok-bot#what-are-they-doing)

界面采用左侧房间场景与右侧任务状态。房间包含深色纹理墙面、窗帘、城市窗景与月牙、挂历、书架、绿植、透视木地板、地毯、台灯、抽屉柜和带键盘的电脑桌。桌上有小风扇和咖啡杯，绿植缓慢摇摆，风扇根据角色动作的连续相位运转，忙碌时加速，休息时减速。咖啡热气在清醒状态下缓慢飘动。

桌面显示器会根据角色状态显示终端、传输箭头、月亮或告警，终端下方进度条对应实际 CPU 使用率。背景仅使用黑白像素，墙面、地板和窗景纹理保持静止，场景底图预先缓存，房间绘制限定在左侧区域。

顶部显示 Makit Compute 与时间，底部采用黑底白字显示图形指标。任务标题使用 780 字重，顶部标题与耗时使用 750 字重，时钟使用 700 字重，底部图形指标使用 650 字重。屏幕字体使用随程序打包的 Inter，字体许可位于 `fonts/OFL.txt`。视觉排版参考 OpenAI 官网及 ChatGPT 产品界面，并依据用户提供的房间场景图片补充背景。[OpenAI 官网](https://openai.com/)、[ChatGPT](https://chatgpt.com/)、[字体来源](https://github.com/google/fonts/tree/main/ofl/inter)

| 任务状态 | Hermes 事件 | 屏幕反馈 |
| --- | --- | --- |
| Connect Hermes | 尚无插件心跳，或心跳中断10秒 | 等待连接 |
| Ready | 插件已连接且无任务 | 呼吸、眨眼，持续低负载后闭眼休息 |
| Thinking | pre_llm_call / pre_api_request | 张望思索、环绕点、风扇加速 |
| Replying | post_api_request 明确返回零个工具调用 | 专注动作 |
| Using tools | pre_tool_call 至对应 post_tool_call | 显示工具名、敲击效果、完成次数，多个任务时动作更忙 |
| Needs you | on_human_input_request 至 resolved | 面向用户、问号气泡，说明审批、密码或输入请求 |
| Retrying | api_request_error 且 retryable | 等待动效 |
| Recovering | 工具错误或非重试 API 错误，任务仍在执行 | 等待后续处理 |
| Done | post_llm_call 或 completed=true 的 on_session_end | 开心小跳、屏幕勾号，显示本次耗时 |
| Failed | on_session_end 且 failed=true | 警觉与告警 |
| Stopped | on_session_end 且 interrupted=true 或 completed=false | 停止状态 |

连接基于 NousResearch Hermes Agent 的 Python 插件事件。每个进程保留独立会话与任务状态，工具调用通过 tool_call_id 配对，缺少 ID 的旧载荷按名称逐个配对。等待用户输入优先展示，其余优先展示最早开始的任务。完成反馈保留8秒。模型或工具的内部错误会展示重试或恢复状态，最终结果依据任务结束事件判断。[接口参考](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/observer-hooks.md)

插件每秒经本机 Unix datagram socket `/run/rp-compute/activity.sock` 发送完整状态快照，事件到来时立即发送。显示服务重启后通过下一次心跳恢复当前状态，10秒未收到心跳则显示等待连接。传输内容包括阶段、工具名称、时间和计数。回调返回 None。模型提示词、工具参数、工具返回值和用户输入内容均未纳入快照。底部 RAM/DISK≥90%、温度≥75°C 时显示额外告警线，温度条形图的量程为0–85°C。

## 接入 Hermes

先安装并配置 NousResearch Hermes Agent，再将随显示程序安装的插件复制到当前 Hermes 配置目录并启用。默认配置目录为 `~/.hermes`，自定义 profile 请使用对应的 HERMES_HOME。

```sh
mkdir -p ~/.hermes/plugins/rp-compute-display
cp /opt/rp-compute/software/status-display/hermes_display/{__init__.py,bridge.py,plugin.yaml} ~/.hermes/plugins/rp-compute-display/
hermes plugins enable rp-compute-display
hermes plugins doctor rp-compute-display
```

重新启动 Hermes CLI 会话或 gateway 后生效。插件使用 Python 标准库，可用于 CLI 和 gateway。显示程序与插件的 socket 可通过 `--activity-socket` 和插件进程的 `RP_COMPUTE_ACTIVITY_SOCKET` 环境变量同时调整。显示服务使用 systemd RuntimeDirectory 创建 `/run/rp-compute`。

## 开机动画与启动时机

显示服务启动时默认播放4秒 Makit Compute 动画，包含角色睁眼、轻微呼吸、眨眼和启动指示点，然后自动进入任务状态界面。临近动画结束时，系统关键指标已就绪则显示 Ready。可用 `--boot-seconds 0` 关闭动画，或设置其他非负秒数。`--duration` 包含动画播放时间。

服务安装到 `sysinit.target`，在所需挂载点、根文件系统重挂载、模块加载和 udev 服务启动后运行，关闭默认的 basic.target 排序依赖，并在关机时先完成屏幕清理。每次重启显示服务也会播放动画。动画开始于 Linux 的早期用户空间，上电至首帧的时间仍包含固件、内核、initrd 和屏幕初始化阶段。

```sh
python3 status_display.py --boot-preview --preview boot.gif
python3 status_display.py --boot-preview --preview boot.png
```

默认开机预览 GIF 为4秒动画加1秒主界面，合计5秒，并标注 Preview。

## 本地预览

预览使用明确标注的模拟数据，可在安装 Pillow 的 macOS/Linux 上运行。

```sh
python3 status_display.py --preview preview.png
python3 status_display.py --preview preview.gif
python3 status_display.py --preview states.gif --showcase
```

PNG 为400×240，默认 GIF 为20fps的6秒任务动画。`--showcase` 生成连接、思考、执行工具、等待输入、回复、重试、恢复、完成、失败、停止与休息等状态的30秒演示。预览使用标注 Preview 的模拟事件和指标。

## 树莓派前台运行

将整个 `software` 目录复制到机器上，保留 `display-test` 与 `status-display` 两个相邻目录。依赖与屏幕连接设置沿用显示测试说明。默认 60fps 使用此前上机成功的 10MHz SPI 参数，该参数超出公开原厂 2MHz/20Hz 时序范围。

```sh
sudo apt-get update
sudo apt-get install -y python3-libgpiod python3-pil gpiod device-tree-compiler iproute2
cd software/status-display
sudo python3 status_display.py --fps 60
```

默认持续运行，Ctrl-C/SIGTERM 会先清屏、关闭 DISP 和 COM，再关闭显示电源。按指定时间结束或指定网卡时，可使用下面的参数。

```sh
sudo python3 status_display.py --fps 60 --duration 120 --interface eth0
```

`--fps 20` 使用 2MHz SPI。显示电源故障或 COM 线程异常会退出，日志记录错误，驱动关闭显示电源。

## 开机自启

装配完成并连接显示屏后，安装脚本将代码放入 `/opt/rp-compute/software`，编译高有效片选 overlay，安装并启动 `rp-compute-display.service`。

```sh
cd software/status-display
sudo sh install.sh
```

服务启动准备脚本按需加载临时高有效片选 overlay，并将 spidev 缓冲设为 16384 字节。安装器同时将 `options spidev bufsiz=16384` 写入 `/etc/modprobe.d/rp-compute-display.conf`，使开机 udev 自动加载与手动加载使用一致参数，避免并发加载恢复4096字节缓冲后额外重试。准备脚本会在加载后复查缓冲大小。

脚本检查实际设备树中的 `spi-cs-high` 属性，避免重启后 `/tmp` 中残留的 dtoverlay 缓存影响判断。服务每次启动都会检查，因此重启后自动重新准备。启动前需结束原来的显示测试程序，使 SPI/GPIO 可被独占。服务异常退出后自动重启，60 秒内最多尝试 5 次。首次安装所需的 dtc、dtoverlay、libgpiod 与 Pillow 会在复制前检查。

```sh
sudo systemctl status rp-compute-display
sudo journalctl -u rp-compute-display -f
sudo systemctl restart rp-compute-display
sudo systemctl stop rp-compute-display
sudo systemctl disable --now rp-compute-display
```

## 历次样机验证

2026-11-16 已部署至 `192.168.50.82`，安装目录为 `/opt/rp-compute/software`，systemd 服务已启用开机启动。

- 实时采集主机名、CPU、内存、温度、磁盘、eth0 地址及网络流量，数据显示正常。
- 使用2、3、4个独立 CPU 负载进程逐级运行，每级12秒，实际触发 Computing、Working、Very busy。负载停止后触发 All clear、Ready，持续低负载后进入 Taking it easy。
- 在局域网经 SSH 传输约25MiB测试数据，实际触发 Transferring，结束后返回 All clear 和 Ready。
- 第一段连续运行约4分17秒，累计刷新约59.9fps，SPI错误、超时均为0，COM最大软件边沿间隔约0.5088秒，服务无异常重启。
- 停止服务后确认清屏、关闭显示电源。卸载实时 overlay、恢复默认低有效片选后，再启动服务，准备脚本成功重新加载高有效片选配置，程序恢复运行。
- 加粗字体与房间背景版已更新至样机，首轮30秒统计为59.93fps、1799帧，COM最大软件边沿间隔0.5028秒，服务无异常重启。树莓派预览渲染正常，安装代码的SHA-256与本地一致。
- 设备切换至 wlan0 地址 `192.168.50.83` 后，丰富背景版已部署。新增墙面、窗帘、地板、地毯、台灯、挂历、抽屉柜、小风扇及咖啡杯。十二状态通过本地渲染检查，房间像素范围检查通过，树莓派预览正常。上机首轮30秒为59.93fps，COM最大软件边沿间隔0.5028秒，随后正常进入休息状态，服务保持开机启用且无异常重启。
- Makit Compute / Hermes 任务界面已上机。以普通用户身份加载配套插件并回放模拟事件，服务日志确认 thinking → tool → waiting → thinking → responding → done → idle → disconnected。连续60秒统计59.97fps，COM最大软件边沿间隔0.5048秒，无异常重启。并行同名工具、多个会话、旧载荷缺少ID、心跳失效、显示服务重连、重复监听保护和CLI退出清理已通过本地检查。
- 4秒 Makit Compute 开机动画已部署，并验证软件重启后自动播放及进入主界面。将服务提前至 sysinit 阶段后，发现早期 udev 自动加载 spidev 导致缓冲恢复4096字节的竞态，已通过 modprobe.d 固定16384字节并增加准备阶段复查。修复后两次软件重启均无服务异常重启。最新一次内核单调计时约12.216秒开始动画、16.154秒结束动画。此时间基准从内核启动计时，电源接通至首帧还包含固件启动时间。

Hermes Agent 本体在该样机上尚未安装，因此以上任务事件来自模拟回放，真实模型任务及当前 Hermes 安装版本的插件加载待安装后验证。插件文件随显示程序部署在 `/opt/rp-compute/software/status-display/hermes_display/`。

用户已确认装机屏幕界面正常且能看到角色。随后按用户提供的场景参考，进一步加粗字体并加入房间背景。软件重启后的自启与开机动画已验证，断电冷启动的实际首帧观感和长期运行稳定性待确认。
