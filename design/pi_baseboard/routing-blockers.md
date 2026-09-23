# 单基板剩余布线问题与复现依据

本记录用于继续修复，不是 DRC 豁免或制造许可。所有复测均从 editable source 运行 pcb.run(check)，未编辑生成的 KiCad、DSN、SES 或报告。

## TPS22990 多形状 VOUT 端子丢失网络

- 器件 U_MAIN_SW，TPS22990DMLR / C962990，原厂引脚 8/9/10 都是 VOUT。电路源把 VOUT1/VOUT2/VOUT3 直接接 V5_MAIN。
- 供应商 pad 10 同时有矩形和重叠多边形。生成 Circuit JSON 中有逻辑 pin 10 和 pin10_internal_1，并有 source_component_internal_connection 连接两者。前者具有 V5_MAIN 的 connectivity key，后者没有。
- 输出 KiCad 的矩形 pad 10 有 V5_MAIN，多边形 pad 10 没有 net；多边形与 VOUT 的 8/9/10 重叠，造成 2 个 clearance、1 个 shorting_items、2 个 solder_mask_bridge 错误，并阻挡 VOUT 出线。
- 已尝试与供应商一致的 VOUT1/VOUT2/VOUT3 名称，以及具证据的 same-pcb-port logicalPadGrouping 声明；多轮完整 check 仍出现相同结果。
- 正确修复应让同一个物理端子的所有形状继承同一逻辑网络。不能删掉必要焊盘、捏造第二个端子或添加零欧姆元件来掩盖映射问题。验收：所有 pad 10 形状均为 V5_MAIN，以上 5 个错误消失，3 个 VOUT 端点真正布通。

## 大电流干线仍被全网细脚线宽替代

- BAT_RAW 和 SYS_RAW 声明 2 mm 干线、6 A 条件目标、1.8 mm 估算最低铜宽，并只允许 U_CHARGER 周围最多 1 mm 的 0.2 mm 逃线。CHG_SW 也只允许最多 1 mm 短逃线。
- 实际 DSN 对整个网络使用约 0.224003 mm 单一线宽；KiCad 以 0.224 mm 输出。长距离电源干线因此未形成，escape 检查持续失败。
- CHG_VBUS、V5_MAIN 的自动细脚宽度还分别出现 0.224003→0.224 mm、0.280010→0.280 mm 的取整报错。这些网络同时承担大电流，未通过降低整网最小线宽消除报告。
- BOOST_SW、V5_BOOST、V5_PI 等也必须按实际铜宽、长度、层别和过孔重新核验，不能因为某项 gate 未报错就视为满足电流。
- 当前配置接口只能声明局部逃线规则；复测显示路由结果没有生成声明的宽干线。需要工具支持实际局部加宽/电源铜区，或可持久化且可复核的手工电源布线路径。不得把电源分成虚假的独立网络，不得直接修补输出文件。

## 已修复的表示问题

TPS61088 原生 RHL 凹形热焊盘在 DSN 中被凸包填满，遮住 VCC/SS。以原生 KiCad 库为依据，把同一个 pad 21 表为面积和轮廓相同的两个矩形，保留焊盘号、周边焊盘、锡膏和方向后，BOOST_VCC 与 BOOST_SS 已布通。证据和哈希见 SOURCES.md。

GPIO AUX 正常预算为 100 mA；固件、信号故障反灌隔离、功率器件热验证、固定孔和 FPC 堆叠尚未完成。即使后续 DRC 清零，仍须分别验证这些项目。

## 最后一次复测结果（2026-09-24）

Run `6e2cc748-8430-47df-a123-091fc622fcdd`：局部重布 BOOST_COMP 后，KiCad 仍为 5 个错误、0 个警告、8 个阻断连通发现（含 2 个铜区分裂）；BOOST_COMP 和 V5_MAIN 仍部分连通。工具确认连续两轮相同阻断集合，停止重复同类修补。Freerouting 的预地铜汇总为 40 个未完成项，不能把这个预填铜数当作最终 KiCad 断线数。

pcb.measure 实测：BAT_RAW/SYS_RAW/CHG_SW 为 0.224 mm，BOOST_SW/V5_BOOST 为 0.24 mm，V5_MAIN 为 0.28 mm，V5_PI 为 0.3 mm，USB_VBUS 为 0.2 mm。正常 GPIO 辅助电源轨为 0.5 mm。板为 70 × 104 × 1.6 mm、4 层、144 元件、122 个 0.6/0.3 mm 过孔。功率干线的实测宽度不是额定电流合格证明。

R_LCD_ILM 与 C_LCD_DVDT 的间距冲突已消除。LCD_ILM、V5_LCD、LID_CLOSED、BOOST_VCC、BOOST_SS 不再出现在未完成网络清单。内层独立渲染遇到 PCB sandbox 不能确定 design 归属的环境错误，未声称通过内层视觉复核。未生成 release 或制造文件。
