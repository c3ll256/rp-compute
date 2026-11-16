# rp-compute 显示屏样机测试

适用当前 Pi 4B 精简基板和 Sharp LS027B7DH01 / LS027B7DH01A，400×240 单色屏。接线来自 `design/pi_baseboard_lite/source/main.tsx`，串行协议和上下电顺序依据项目内两份 Sharp 原厂规格书的 6-2、6-3、6-5 节。

| 信号 | BCM GPIO | Pi 物理针脚 |
| --- | --- | --- |
| SPI MOSI / SI | 10 | 19 |
| SPI SCLK | 11 | 23 |
| 高电平有效 SCS / CE0 | 8 | 24 |
| EXTCOMIN | 12 | 32 |
| DISP | 25 | 22 |
| 显示电源使能 | 24 | 18 |
| 共用 FAULT_N 输入 | 16 | 36 |

## 样机环境

2026-11-16 通过 SSH 在 `192.168.50.82` 上调试，用户名 `xonar`。程序部署目录为 `/home/xonar/rp-compute-test`。系统为 Ubuntu 26.10、aarch64，Pi 4B Rev 1.5，GPIO 控制器为 `pinctrl-bcm2711`，SPI0 已启用。

安装依赖并将本目录文件复制到机器上。

```sh
sudo apt-get update
sudo apt-get install -y python3-libgpiod python3-pil gpiod device-tree-compiler
```

程序使用 libgpiod 2.x、Pillow 10+ 及 Linux SPI ioctl。需要 GPIO/SPI 设备访问权限，样机使用 `sudo` 运行。

## 本次运行结果

120 秒图案循环于 2026-11-16 17点58分完成，进程退出码为 0。共完成 240 帧、961 次 SPI 事务和 241 个 EXTCOMIN 边沿，最大软件边沿间隔 0.5002 秒。结束后 GPIO8、GPIO12、GPIO24、GPIO25 均实读为低，GPIO16 FAULT_N 为高。另已验证 SIGTERM 中途停止会完成清屏和关闭显示电源。

随后针对用户初次反馈的白屏/黑屏，重新开启固定棋盘格和每 4 秒切换的图案循环。用户已在实屏依次确认棋盘格、黑屏/白屏切换和文字。至此基础图像写入与显示已通过实物观察，单像素条纹、文字方向和四边完整性尚未逐项确认。Linux SPI 统计中错误和超时计数均为 0。

用户随后确认实物型号为 LS027B7DH01A。2 MHz SPI、20fps 目标的动态测试实际约为 17.7fps，用户观察到明显拖影或闪烁。改用 10 MHz SPI、完整单事务帧包及绝对时间调度后，于 2026-11-16 18点16分完成 60 秒测试，共写入 3600 帧、3601 次 SPI 事务，平均 60.00fps。软件 EXTCOMIN 边沿最大间隔 0.5001 秒，FAULT_N 保持高，SPI 错误及超时计数均为 0。用户确认运动明显顺滑，拖影或闪烁有所改善。测试完成后显示电源、DISP、COM 和 SCS 均实读为低。

该结果是本样机的一分钟实验性高频验证，采用超出公开原厂时序范围的参数，长期运行可靠性尚未验证。

## 临时启用高有效片选

Sharp SCS 为高电平有效。此内核由设备树决定 GPIO 片选极性，直接设置 Python spidev 的 `cshigh` 会报返回模式不匹配。

在当前目录编译、加载提供的 overlay，再重新绑定 SPI0 控制器。操作时先停止所有使用 SPI0 的程序。overlay 同时保留扩展接口 CE1 的低有效配置。

```sh
dtc -@ -I dts -O dtb -o rp-lcd-test.dtbo rp-lcd-test-overlay.dts
sudo dtoverlay -d "$PWD" rp-lcd-test
printf '%s' fe204000.spi | sudo tee /sys/bus/platform/drivers/spi-bcm2835/unbind
printf '%s' fe204000.spi | sudo tee /sys/bus/platform/drivers/spi-bcm2835/bind
sudo gpioinfo -c gpiochip0 8 7
sudo pinctrl get 8
```

GPIO8 应显示为普通 `output`，空闲电平为 `lo`。GPIO7 应显示为 `output active-low`。程序启动前检查 GPIO8 极性。

这组命令中的 `fe204000.spi` 是本次 Pi 4B 的实际设备名。临时 overlay 在重启后需要重新加载。样机已完成本节设置，当前会话直接运行下面的测试即可。

## 运行

```sh
sudo python3 display_test.py --duration 120 --pattern-seconds 8
```

依次循环白屏、黑屏、16 像素棋盘格、单像素竖线、单像素横线和文字。文字页包含运行时间、时钟及移动方块。观察四边是否完整、是否缺行、是否存在固定黑白点、条纹是否均匀，以及文字方向。

固定显示文字页 60 秒。

```sh
sudo python3 display_test.py --duration 60 --pattern text
```

默认运行 120 秒。正常完成、Ctrl-C 或 SIGTERM 后，程序清屏，关闭 DISP，停止 COM，再关闭显示电源。软件 COM 在专用线程产生 1 Hz EXTCOMIN，正常测试时全屏每秒刷新两次。每帧分成四个 60 行事务，每个 3122 字节，事务起始间隔至少 60 ms，适配 4096 字节 SPI 缓冲。SPI 时钟为 1 MHz，SCS 建立与保持各 10 µs。

FAULT_N 拉低或 COM 线程异常时程序退出并关闭显示电源。该故障线由显示支路和扩展模块支路共用。日志报告成功写入帧数、事务数、COM 边沿数及最大软件 COM 间隔。远程软件日志只能确认这些主机侧状态，屏幕实际显示、引脚波形和电压需要通过实物观察或仪器确认。

## 高频整屏动画

Sharp 两个型号公开规格书的 6-3 节均给出 SCS 帧频 1–20 Hz、SPI 时钟最高 2 MHz、垂直周期最小约 50 ms。400×240 全屏协议包为 12482 字节，在 2 MHz 下仅传输就需要 49.928 ms。60 Hz 整屏传输需要约 5.99 MHz SPI 时钟。程序支持 1–60 Hz 目标帧率，超过 20 Hz 的测试采用超出公开原厂时序范围的实验配置。

开源驱动 `pico_sharpmem_display` 明确支持 LS027B7DH01，默认 10 MHz SPI，并提供 60fps 动画实现与双缓冲说明。本次依据这些实现增加实验性 60fps 测试，实际发送帧率由样机测量。[驱动源码及实现说明](https://github.com/mattwach/pico_sharpmem_display)

高于 2 Hz 时，整帧放在一次 SCS 事务内发送，避免部分行分包增加片选频率。先停止所有 SPI 程序，将 spidev 缓冲临时设为 16384 字节。本次样机已完成设置，重启后需重新设置。

```sh
sudo modprobe -r spidev
sudo modprobe spidev bufsiz=16384
sudo python3 display_test.py --duration 120 --pattern motion --fps 20
```

60fps 短时测试采用 10 MHz SPI，并在结束时清屏、关闭显示电源。

```sh
sudo python3 display_test.py --duration 60 --pattern motion --fps 60
```

动画包括横向移动黑块和滚动条纹。屏幕上显示目标帧率和实际发送帧率，日志每 5 秒报告一次平均实测值。实际帧率受 Linux 调度、图像绘制和 SPI 事务开销影响，液晶像素的光学响应需通过实屏判断。目标高于 2 Hz 且至多 20 Hz 时使用 2 MHz SPI、SCS 起始间隔至少 50 ms。超过 20 Hz 默认使用 10 MHz SPI，以绝对时间表调度整帧，SCS 低电平间隔至少 1 µs。COM 均保持 1 Hz。`--spi-hz` 可显式覆盖时钟。

## 停止后台测试

首次调试使用临时 systemd 单元 `rp-lcd-test`，20Hz 目标测试使用 `rp-lcd-refresh` / `rp-lcd-refresh-fast`，60Hz 目标测试使用 `rp-lcd-60hz`，可在它们运行时提前结束。

```sh
sudo systemctl stop rp-lcd-test
sudo journalctl -u rp-lcd-test --no-pager
sudo systemctl stop rp-lcd-refresh
sudo journalctl -u rp-lcd-refresh --no-pager
sudo systemctl stop rp-lcd-60hz
sudo journalctl -u rp-lcd-60hz --no-pager
```

## 恢复原 SPI 配置

测试停止后移除临时 overlay，并重新绑定 SPI0。

```sh
sudo dtoverlay -r rp-lcd-test
printf '%s' fe204000.spi | sudo tee /sys/bus/platform/drivers/spi-bcm2835/unbind
printf '%s' fe204000.spi | sudo tee /sys/bus/platform/drivers/spi-bcm2835/bind
```

## 离线图案预览

```sh
python3 display_test.py --preview-dir /tmp/rp-lcd-previews
```
