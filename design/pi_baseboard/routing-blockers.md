# 单基板：局部功率铜已建立，宽干线的路由输入仍不完整

这是修复、验证和复现记录，不是 DRC 豁免、载流认证或制造许可。所有修改均在 editable source；没有手改 KiCad、DSN、SES、Circuit JSON 或检查报告。旧版本细线/过孔误判的历史保留在 Git。

## 最终结果（2026-09-24）

- 最终 check：`37241952-a874-411b-a105-8bc95fac9e7c`，blocked，3 条聚合错误诊断。
- KiCad 板 SHA-256：`fd11b4bc419043440250154f29b934e2d769121b67f37c89857c3983f19ee064`。
- 应用：0 个实体几何错误、0 个归一化警告、40 项阻断连通发现，来自 46 个原始 KiCad 未连通项，含 6 个分裂铜区。
- 独立 `pcb.kicad_cli pcb drc --format json --exit-code-violations`：exit 5；同样 46 个未连通项；144 个 `lib_footprint_mismatch` 警告；没有其他实体 violation。返回非零是未通过，不是 KiCad 无法运行。
- 没有元件重叠、短路、铜间距、钻孔间距或 USB 焊脚热连接错误。旧版 14 个声明地过孔的间距误判本轮不再出现。
- 原先 TPS22990 多形状 pin 10 映射修复保留；两个物理形状仍是一个 V5_MAIN 逻辑端口。供应商焊盘形状/编号没改。
- 没有制造 release；当前板不完整，不能用于制作或通电。

## 本轮修改

1. 充电电感旋转并移近 SW，调整 SYS/BAT/PMID 电容及 bootstrap 电容位置，修掉全部 courtyard 冲突。
2. 升压电感移到 SW 引脚侧，三个输出电容旋转成共同正极方向；调整输入、VCC、bootstrap、FSW、ILIM 和使能外围。
3. 声明 39 个局部功率铜区，包括输入/输出并联脚、真实低电流支路接入面、充电 BAT/SYS 独立扇出，以及升压输出到主开关的连续铜区轮廓。所有轮廓通过几何有效性检查；相交的同网铜区已做几何并集，未使用优先级豁免。
4. 铜区清距对 USB_VBUS、CHG_VBUS、BAT_RAW、SYS_RAW、CHG_SW、CHG_PMID 设为 0.15 mm。这是原制造能力下限；0.25 mm 会清除 BQ25622/TUSB320 细脚颈部。该清距作用于相应网络，不限于局部。所有 currentCapacity、nominalWidthMm、minimumWidthMm、escape、netClasses、manufacturing、footprintExceptions、原 17 个 stitchingVias 与本轮起点逐对象核对一致。
5. 定向重布 V5_MAIN、USB_OUT2。USB_OUT2 原始未连通清除；功率铜区之间的干线仍未产生。

接口位置、元件身份和电路连接没有改变；CAD 没有修改。

## 宽度规则已经恢复，但干线没有生成

最终所有带 currentCapacity 的 9 个网络不再报告 `net_width_below_current_requirement`。完整布线及定向重布的 DSN 都保留以下宽度：

| 网络 | 保留电流目标 A | 最低估算线宽 mm | DSN 全网线宽 mm |
|---|---:|---:|---:|
| BAT_RAW / SYS_RAW | 6 | 1.8 | 2.0 |
| BOOST_SW | 6 | 1.8 | 2.0 |
| CHG_SW | 3.5 | 0.85 | 1.2 |
| USB_VBUS / CHG_VBUS | 2.7 | 0.75 | 1.2 |
| V5_BOOST / V5_MAIN | 3.3 | 0.8 | 1.2 |
| V5_PI | 3.2 | 0.75 | 1.2 |

这些是输入规则，不能当作最终铜几何。最终 `routed-copper-dump.json` 中 BAT_RAW、SYS_RAW、USB_VBUS、CHG_VBUS、BOOST_SW、V5_MAIN 的普通干线线段数均为 0；V5_PI 仅 1 段 1.2 mm。CHG_SW、V5_BOOST 的连接由铜区承载，仍须检查铜区分裂及颈部。没有完整路径，就没有载流验收。

自动布线最终未完成网摘要列出 BAT_RAW、BOOST_SW、CHG_VBUS、SYS_RAW、USB_VBUS、V5_MAIN 和 V5_PI。V5_BOOST 不在此摘要，但原始 KiCad 仍有 2 个 `replicator_area_BOOST_5V_DISTRIBUTION` 区内未连通，属于信号切割铜区后的分裂；不得因此把升压到主开关声称为完全布通。40 个连通阻断也不能说成“仅剩 3 个 DRC 错误”。

## 可复现的铜区 → 自动布线输入缺口

两个层面的输出不一致：

- `copper_area_placed` 确认铜区到达细功率焊盘，宽度选择因此恢复到 1.2/2 mm。
- 最终 KiCad 的铜区存在并填充；但提交给 Freerouting 的 DSN wiring 没有对应 power-area polygon，网络端点仍列原始细焊盘。全量运行的 wiring 没有 wire，只有已有定位过孔；定向重布保留普通铜线后仍没有铜区连接几何。

全量 run：`8679ffd5-3c89-45fb-b4c2-a517b9c84278`，DSN `routing/2026-09-24T14-05-05-216Z/pi_baseboard.dsn`。定向重布 run：`37241952-a874-411b-a105-8bc95fac9e7c`，DSN `routing/2026-09-24T14-08-54-269Z/pi_baseboard.dsn`，SHA-256 `038b73ebcc7ae553db82d22673b50294706398f1349c985c0c280ef832c995ec`。

后者的 wiring 有 933 条普通 wire，而 power-area polygon 数为 0。网络示例仍为：

```
(net V5_MAIN
  (pins U_PI_EFUSE-1 U_PI_EFUSE-5 U_LCD_EFUSE-1 U_LCD_EFUSE-5
    C_LCD_FUSE_IN-1 C_PI_FUSE_IN-1 U_AUX_LIMIT-1 R_PI_OVLO_TOP-1
    R_LCD_OVLO_TOP-1 C_AUX_IN-1 U_MAIN_SW-8 U_MAIN_SW-9
    U_MAIN_SW-10 U_MAIN_SW-10@1))
```

宽度恢复后，路由器仍面对 0.28/0.30 mm 等细端点，没有本应可接入的宽铜区边界。这个输出缺口与多个电源网无干线、信号穿过铜区并将其割裂的结果一致。没有修改应用实现来绕过门禁，也没有插假零欧姆、拆假网络或改生成文件。工具返回的 next.paths 有时指向 `.ses`；那是生成物，不是允许修改的源。

## 填铜后的检查仍未完成

最终填铜报告可见：BOOST_5V_DISTRIBUTION 保留 93.3% 轮廓面积，跨越网络包括 BOOST_COMP、BOOST_FB、MAIN_CT；它仍分裂。其他示例为 CC_VDD_LAND 只剩 6.3%，R_BOOST_FSW_POWER_LAND 28.7%，CHARGER_PMID_LOCAL 33.4%。所有窄脚“被覆盖”不能替代跨区连通、瓶颈或回路验证。最终顶/底铜层已通过独立 KiCad SVG 导出查看。

地铜的未连通还包括 U_CC、输入旁路、U_LCD_EFUSE、U_POR 和底层缓冲/控制附近；应继续以真实填充轮廓和异网铜几何定位。自动救援提示的 region_mm 部分仍带错误坐标变换（例如源板 X≈6.6 的区域显示 X≈106.6），不能用该数值直接放孔，更不能用 zone 元数据原点放孔。

## 解除阻断的验收条件

1. 让铜区在自动布线输入中携带真实同网连接与可接入几何，且路由器尊重不同网的已填充功率铜；不能只把窄脚从线宽约束中排除。
2. 保持以上电流、线宽、铜厚及最长 1 mm 逃线要求，生成所有缺失干线；检查跨层过孔并联数量和各层铜厚的实际载流能力。
3. 重填铜后核对每一个功率支路、开关回路、细脚颈部及地回流；不能仅用铜区填充比例作通过依据。
4. 应用 check 和同一最终 KiCad 的独立 DRC 都无未连通、短路、间距错误，再进行最终板面检查。本轮没有达到这些条件。

PCB 固件、热验证、FPC 机械到达性、板固定孔及禁布区仍按原合同独立验收；本轮没有改它们的要求。
