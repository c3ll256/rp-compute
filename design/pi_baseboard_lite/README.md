# 屏幕与 GPIO 精简基板（需求草案）

本版由用户要求新建：只提供 Sharp LS027B7DH01 屏幕 FPC 接口和 8 针、与 Pi GPIO 同类的扩展针座。原 pi_baseboard 的充电、Pi 供电、MCU、联锁及辅助电源版本保留，不能将其尚未通过的 DRC 视为本版验证。

## 功能草案

- 沿用 Pi 4B 与现有 40 针 GPIO 对接方式；屏幕型号不变。
- 屏幕使用既有 10 芯、0.5 mm FH12-10S-0.5SH(55) FPC 座；保留显示供电、逻辑缓冲、去耦及必要的默认关闭电路。具体 COM 反转和 DISP 控制移交 Pi，需重新核对时序、上电及掉电状态。
- 前部扩展改为总计 8 个触点的 2.54 mm GPIO 类接口。暂拟 2×4 直立公排针，包含电源与地；单双排及公母等待用户明确。引脚分配仍为工程设计事项，尚未冻结。
- 本版不布置电池、充电器、升压器、Pi 电源开关、监督 MCU 或喇叭。
- 暂拟由 Pi 原生 USB-C 供电，再从 Pi 的 GPIO 电源触点向显示支路取电；这与完整版装机遮挡 Pi USB-C 的需求不同，须由用户确认本版供电方式后才能固定电路和外壳接口。
- 沿用可拆换前模块的产品目标，只支持断电插拔。模块供电预算、保护和信号分配在器件及电路阶段确定。

## 机械和验证边界

保留现有外壳定位槽、1 mm 屏舱前沿以及用户设置的 12 mm 电源帽直径；本次草案不修改 CAD。既有 70×104 mm 板框及接口坐标仅供布局起点，不是本版已验证的安装尺寸。FPC 完整路径、触点方向和装配堆叠仍需与最终 PCB 一起验证。

当前仅有需求草案，没有本版电路、布线、DRC 或制造文件。主需求已登记精简版范围和两个未决项；BOM 保留完整版参考行并标为未就绪，尚未选定精简版采购清单。

## 已核对的设计输入

Pi 4B 索引身份为 `raspberrypi/raspberry-pi-4-model-b`。官方 GPIO 图已目视核对：[官方针脚图](https://raw.githubusercontent.com/raspberrypi/documentation/master/documentation/asciidoc/computers/raspberry-pi/images/GPIO-Pinout-Diagram-2.png)，图像 SHA256 为 `646c2db09e9eb5894440b22c9fe1b9623dfd4ecefcf3aaae7f554e5fd8c1c934`。

| 可复用功能 | Pi 物理针号 | 官方信号名 |
|---|---|---|
| 显示串行时钟 | 23 | GPIO11 / SCLK |
| 显示数据 | 19 | GPIO10 / MOSI |
| 显示片选候选 | 24 | GPIO8 / CE0 |
| 扩展 I²C 候选 | 3、5 | GPIO2 / SDA、GPIO3 / SCL |
| 扩展 SPI 候选 | 19、21、23、26 | GPIO10 / MOSI、GPIO9 / MISO、GPIO11 / SCLK、GPIO7 / CE1 |
| 3.3 V、电源地 | 1 或 17；6 等 | 3V3 power；Ground |
| 5 V 显示输入候选 | 2 或 4 | 5V power |

以上为可用针脚证据，不是已冻结的 8 针分配。显示和扩展可共享 SPI 数据/时钟，但须使用不同片选并在驱动层协调；接口同为 2.54 mm 不代表与 Pi 前 8 针逐针兼容。

Sharp 资料为 `product/references/LS027B7DH01-sharp-2010.pdf`（SHA256 `997ecbcb7f020fbe077632dc90f6bf82d9e0e49ccf2211484093dec348965d98`）。第 11 页明确 EXTMODE 高接 VDD、低接 VSS，分别选择外部 COM 或串行标志；DISP 低为白屏且保留显存。第 14 页上下电时序图已目视复核：供电稳定后先初始化显存，再启动显示和 COM；关机先清屏、拉低 DISP，再降低供电。VDD/VDDA 须同时变化或 VDD 先变化。第 15 页文本给出 SCLK 最大 2 MHz。Pi 驱动、上电默认电平和受控断电实现仍待电路阶段验证。
