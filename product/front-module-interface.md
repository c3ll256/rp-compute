# 前面板触控与内置音频

成品模块采用 Azoteq TPS43-201A-S，一块。硬件 2 带六针 ZIF，软件 01 提供标准手势，A 型自带贴胶，S 为单件包装。按原厂 v1.06 图 1.1、图 2.1/2.2 和表 2.1 核对。标称外形 43.3 × 40.3 mm，每边尺寸公差 ±0.2 mm，含胶及器件的厚度 2.03 mm ±10%。CAD 预留 43.5 × 40.5 mm 最大外形。按原厂板背面图，器件一侧朝机身右边，除最左 9 mm 空白板边按 1.25 mm 板厚与原厂胶预留外，其余位置均预留 2.233 mm 最大叠厚。此为保守分区估计，实物需核对器件和插座方向。

前平台的触控区与上壳一体成形，使用相同的暖白绝缘材料。外表面 Z27 mm，感应区壳厚 0.48 mm。模块中心 (0, −30.9) mm，原厂胶贴合于 Z26.52 mm 的内壁。装配时器件面朝内，左侧空白板边跨过左安装梁。模块距已订基板的最小名义间距为 0.855 mm。

先干装排线与模块，再装屏舱和基板。模组从空屏舱开口下降，在前平台内侧向前滑动 50.5 mm，再由底侧托起贴合。已检查释放胶层后的反向刚体路径，先降低 0.14 mm、平移至开口、再抬高 12 mm，未发现穿插（网格公差 0.02 mm，步长 0.12 mm）。排线采用 0.5 mm 节距、6 芯、30 mm 同面型。完整排线、胶膜抽出、触控灵敏度、按压变形和反复使用后的贴合情况须打样确认。

## 声学安装

喇叭中心 X−16、Z15 mm，麦克风进声中心 X+12、Z15 mm。左右分隔，均朝机身前方。喇叭采用 15 × 11 × 2.5 mm 标称包络及独立 1 cm³ 后腔，穿线后密封过线孔。麦克风贴在主基板顶面，Ø0.60 mm 板孔位于板坐标 (10.5, −18) mm。前壁入口与板底孔之间由弯折的密封导音件连通，入口中心高 15 mm，板底出口高 21 mm。喇叭采用 0.5 mm 装配态密封垫，麦克风导音件两端分别密封到前壁和基板底面。打样需分别验证出线、密封、音量、录音及扬声器串音。

## 触控板与基板

基板采用广濑 FH12-6S-0.5SH(55) 下接触座，排线为 XFCN 0.5-06-30-A-3344。插入基板端的裸铜面朝基板。两个座子的编号方向相反。接线以各自的焊盘号为准。

| 基板 J_TP | 模块 J1 | 信号 | Pi 物理针 |
| --- | --- | --- | --- |
| 1 | 6 | SDA / GPIO2 | 3 |
| 2 | 5 | SCL / GPIO3 | 5 |
| 3 | 4 | 3.3 V | 1 |
| 4 | 3 | GND | 6 |
| 5 | 2 | NRST / GPIO27，开漏复位 | 13 |
| 6 | 1 | RDY / GPIO17，握手 | 11 |

首件装配先断电，量通 J_TP.3 到模块标注的 3.3 V 焊点、J_TP.4 到 GND 焊点，再检查两轨之间无短接。前舱合拢前插入排线并闭锁。合拢后，插座闭合包络与触控模组之间名义余量约 0.39 mm，打开锁扣及收纳排线需要用实物试装。

[Azoteq v1.06 引脚表 2.1](https://www.azoteq.com/images/stories/pdf/proxsense_i2c_trackpad_datasheet.pdf) · [对应模块的转接板焊盘](https://github.com/mjdigit/tps43-ek/blob/main/assemble/tps43-ek_Assemble.kicad_pcb) · [广濑插座图](https://datasheet.lcsc.com/datasheet/pdf/6e8da5fecf0f520788a618d6da1919a1.pdf?productCode=C202118)

## 音频与基板

Pi 为标准 I²S 主机。默认采样率 48 kHz，每帧两个 32 位时隙，位时钟 3.072 MHz。播放和录音分别使用独立数据线，共用时钟，均取左时隙。显示继续使用原有 SPI 及 GPIO12、24、25。

| 基板端 | Pi 物理针 | 远端 |
| --- | --- | --- |
| 3.3 V | 1 | 麦克风 5 脚 VDD，主基板就近 100 nF 去耦 |
| GND | 6 | 麦克风 3 脚 GND，2 脚 LR 也接地 |
| BCLK | 12，GPIO18 | 麦克风 4 脚、功放 16 脚 |
| WS | 35，GPIO19 | 麦克风 1 脚、功放 14 脚 |
| SD | 38，GPIO20 | 麦克风 6 脚输出，基板有 100 kΩ 下拉 |
| U_AMP.1 / DIN | 40，GPIO21 | Pi 数据输出至功放 |
| J_SPK.1 / SPK+ | — | 功放 9 脚经 4.7 Ω 到喇叭正端 |
| J_SPK.2 / SPK− | — | 功放 10 脚经 4.7 Ω 到喇叭负端 |

功放用 Pi 输入侧 5 V，电源脚旁放 100 nF 和 10 µF。SD_MODE 接高电平，GAIN_SLOT 通过 100 kΩ 拉至 5 V，默认增益 3 dB。喇叭两端都由功放驱动。两只 1 W 串阻限制负载功率。在 5.25 V、串阻负公差 5% 的纯电阻模型下，任意负载的功率上界约 0.77 W。实物仍需测量提示音声压、最大音量时的供电及温升。

喇叭采用 2 针 JST SH 预制线束，默认 75 mm。麦克风、去耦电容和数据下拉电阻位于同一块定制主板，供电与 I²S 通过铜线连通。导音件装机后需检查密封和录音频响。Linux 需用同一全双工 PCM 控制器配置收发，实机检查指针、单击、播放、录音和同时收发。

[树莓派 GPIO 引脚图](https://raw.githubusercontent.com/raspberrypi/documentation/master/documentation/asciidoc/computers/raspberry-pi/images/GPIO-Pinout-Diagram-2.png) · [BCM2711 GPIO 复用表](https://datasheets.raspberrypi.com/bcm2711/bcm2711-peripherals.pdf) · [功放引脚与增益表](https://datasheet.lcsc.com/datasheet/pdf/9dd365a93d191d8d6f09766b0e3ea172.pdf?productCode=C910544) · [喇叭规格及焊接条件](https://datasheet.lcsc.com/datasheet/pdf/536554ff2f1c14207416a46063d46777.pdf?productCode=C50198761) · [麦克风引脚及封装](https://datasheet.lcsc.com/datasheet/pdf/71ad5077f354aad3d252d8bdaf2401d5.pdf?productCode=C5656610)

打样时只选整合显示、触控和音频的主基板。
