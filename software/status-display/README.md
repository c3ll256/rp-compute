# rp-compute 状态与动态角色

400×240 黑白状态屏，面向当前 Pi 4B 基板及实物 Sharp LS027B7DH01A。复用 `../display-test/display_test.py` 中已完成上机测试的电源、SPI、COM 与清屏逻辑。

屏幕主体是一个全宽工作间。透视桌面、墙角、地板、窗框与桌柜带出前后层次，远处城市窗景有轻微视差。画面以原生 400×240 像素绘制，阴影使用锁定在像素网格上的黑白点阵。顶部保留 Makit Compute 和时钟。

## Codex 联动

桌面显示器和角色动作跟随 Pi 本机 Codex。显示服务用后台线程读取 `--terminal-user` 对应用户的 `~/.codex/sessions`，每 0.5 秒观察可见的新事件。支持 SSH、网页终端和小屏终端启动的同一用户 Codex。自定义会话目录可用 `--codex-sessions` 指定。

| Codex 阶段 | 工作间反馈 |
| --- | --- |
| Ready | 眨眼、轻微浮动，空闲且低负载时休息 |
| Thinking | 思考气泡与桌面屏幕动效 |
| Working | 敲键盘动作和滚动短线 |
| Replying | 屏幕进入回复状态 |
| Needs you | 检测到用户输入工具时显示问号 |
| Done | 小跳和勾号，完成反馈保留 8 秒 |
| Attention / Stopped | 显示错误提示或任务中止 |

观测器只向渲染器传递阶段和活动任务数。该联动依赖当前 Codex CLI 的本地 JSONL 会话格式。没有新事件的未结束任务在 15 分钟后归为空闲。

## 键盘与 Terminal 模式

接入 USB 键盘或已由 Linux 配对的蓝牙键盘后，按 `Ctrl+Alt+T` 在角色界面与 Terminal 模式之间切换。程序约每秒检测一次新键盘，检测到后在工作间顶部显示快捷键提示。按住快捷键重复触发的按键事件会被吞掉，一次按下切换一次。

Terminal 使用真实 PTY 会话，默认以 `xonar` 用户及其登录 shell 运行。切回角色界面时会话与正在运行的命令继续保留，再次切入后恢复。输入 `exit` 或在空提示符按 `Ctrl+D` 会结束 shell 并返回角色界面，下次切入会创建新会话。显示服务重启会结束其终端子进程。PTY 输出解析按帧设置短时间预算，大量输出时采用管道背压维持快捷键和屏幕响应。

终端为49列×15行，每个字符占8×14像素。常规和粗体正文使用随程序打包的 Terminus Font 14像素原生点阵字体，许可位于 `fonts/terminus/LICENSE.txt`。斜体使用 DejaVu Sans Mono，中文使用12像素 Noto CJK 字体回退，统一基线。按 ANSI 属性区分常规、加粗、斜体、下划线与反白。ANSI 16色、256色和RGB真彩色背景按亮度映射为固定4×4 Bayer点阵灰阶，文字使用实心黑白笔画，灰色背景上的字符增加对比轮廓。显式相同的前景色和背景色保持隐藏文字效果。显示帧始终输出1bit黑白格式，点阵位置固定于物理像素。支持方向键、Home/End、PageUp/PageDown、功能键、Tab、Ctrl+C 和应用光标模式，并保留独立的全屏应用缓冲区。`Shift+PageUp` / `Shift+PageDown` 浏览最多1000行滚动历史。键盘布局读取 `/etc/default/keyboard`，支持 Shift、Caps Lock、Num Lock、AltGr 和组合字符。

命令由树莓派本机的独立 PTY 登录 shell 执行，显示前端使用 pyte 解析常用 ANSI/VT 控制序列。高级 xterm 扩展、图形协议及复杂 TUI 的兼容性需按应用验证。Sharp LS027B7DH01A 使用每像素1bit存储，灰阶以黑白像素密度模拟。[屏幕规格](https://d7rh5s3nxmpy4.cloudfront.net/CMP7377/files/LS027B7DH01A_06Aug12_Spec_LCP-1112041.pdf)

键盘事件通过 evdev 独占接收，显示程序运行期间连接的完整键盘由 LCD 界面接管，程序退出后释放。可用 `--no-keyboard` 将键盘留给系统控制台，或通过 `--terminal-user` 指定终端用户。键盘热拔插会保留终端会话。

## 开机动画与启动时机

显示服务启动时默认播放4秒 Makit Compute 动画，包含角色睁眼、轻微呼吸、眨眼和启动指示点，然后自动进入工作间。临近动画结束时，系统关键指标已就绪则显示 Ready。可用 `--boot-seconds 0` 关闭动画，或设置其他非负秒数。`--duration` 包含动画播放时间。

服务安装到 `sysinit.target`，在所需挂载点、根文件系统重挂载、模块加载和 udev 服务启动后运行，关闭默认的 basic.target 排序依赖，并在关机时先完成屏幕清理。每次重启显示服务也会播放动画。动画开始于 Linux 的早期用户空间，上电至首帧的时间仍包含固件、内核、initrd 和屏幕初始化阶段。

```sh
python3 status_display.py --boot-preview --preview boot.gif
python3 status_display.py --boot-preview --preview boot.png
```

默认开机预览 GIF 为4秒动画加1秒主界面，合计5秒，并标注 Preview。

## 本地预览

预览使用明确标注的模拟 Codex 状态，可在安装 Pillow 的 macOS/Linux 上运行。

```sh
python3 status_display.py --preview preview.png
python3 status_display.py --preview preview.gif
python3 status_display.py --preview states.gif --showcase
```

PNG 为400×240，默认 GIF 为20fps的6秒任务动画。`--showcase` 生成八种 Codex 状态的 16 秒演示。

## 树莓派前台运行

将整个 `software` 目录复制到机器上，保留 `display-test` 与 `status-display` 两个相邻目录。依赖与屏幕连接设置沿用显示测试说明。默认 60fps 使用此前上机成功的 10MHz SPI 参数，该参数超出公开原厂 2MHz/20Hz 时序范围。

```sh
sudo apt-get update
sudo apt-get install -y python3-libgpiod python3-pil python3-evdev python3-pyte python3-xkbcommon fonts-dejavu-core fonts-noto-cjk gpiod device-tree-compiler iproute2
cd software/status-display
sudo python3 status_display.py --fps 60
```

默认持续运行，Ctrl-C/SIGTERM 会先清屏、关闭 DISP 和 COM，再关闭显示电源。按指定时间结束或指定网卡时，可使用下面的参数。

```sh
sudo python3 status_display.py --fps 60 --duration 120 --interface eth0
```

`--fps 20` 使用 2MHz SPI。原有驱动在显示电源故障或 COM 线程异常时退出。样机还保留此前同步的可选 `--ignore-fault` 参数及设备上的 systemd 覆盖配置，启用时低电平 `FAULT_N` 以告警记录。

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
- 4秒 Makit Compute 开机动画已部署，并验证软件重启后自动播放及进入主界面。将服务提前至 sysinit 阶段后，发现早期 udev 自动加载 spidev 导致缓冲恢复4096字节的竞态，已通过 modprobe.d 固定16384字节并增加准备阶段复查。修复后两次软件重启均无服务异常重启。最新一次内核单调计时约12.216秒开始动画、16.154秒结束动画。此时间基准从内核启动计时，电源接通至首帧还包含固件启动时间。
- 2026-11-17 已部署键盘 Terminal 模式。真实 PTY 验证用户UID为1000、终端尺寸15×56、控制终端有效，中文输出与 top 渲染正常。使用 uinput 虚拟键盘完成生产服务入口测试，覆盖 Ctrl+Alt+T 往返切换、会话环境变量保留、Ctrl+C、Tab 补全、方向键命令历史、Ctrl+D、重新打开终端，以及持续输出下切换与中断。独立测试通过长按快捷键抑制、Shift、Caps Lock、键盘拔插、独立应用屏幕和子进程清理。服务保持开机启用、无异常重启，测试结束恢复角色界面。实物 USB/蓝牙键盘待接入验证。
- 2026-11-17 已补充终端灰阶映射与 ANSI 字重处理。测试通过普通/明亮16色、256色、RGB颜色、反白、固定像素点阵和1bit帧格式，以及真实PTY会话、top、Ctrl+C和退出。更新后再次通过生产服务虚拟键盘完整入口测试，测试结束回到角色界面。
- 2026-11-17 粗体清晰版改为49列×15行，常规及粗体正文采用 Terminus Font 14像素点阵字形，文字笔画使用实心黑白，中文回退字体对齐基线。已通过常规、粗体、斜体、中文、隐藏文字、主/备用屏幕切换和真实PTY中的Codex登录界面检查。样机部署文件校验一致，显示服务启动正常，实物观感待确认。

日志另记录到2026-11-17 16:34、16:41、16:56先后触发LCD/扩展模块共享的 FAULT_N 故障标志并保护性重启。供电或信号原因需要实物测量确认。


用户已确认装机屏幕界面正常且能看到角色。随后按用户提供的场景参考，进一步加粗字体并加入房间背景。软件重启后的自启与开机动画已验证，断电冷启动的实际首帧观感和长期运行稳定性待确认。
