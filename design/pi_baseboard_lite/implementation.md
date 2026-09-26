# 电路、接口和证据

## 资料

Pi索引身份：raspberrypi/raspberry-pi-4-model-b。[官方GPIO图](https://raw.githubusercontent.com/raspberrypi/documentation/master/documentation/asciidoc/computers/raspberry-pi/images/GPIO-Pinout-Diagram-2.png)已目视核对，SHA256 646c2db09e9eb5894440b22c9fe1b9623dfd4ecefcf3aaae7f554e5fd8c1c934。5V使用物理2/4脚；1/17脚仅提供控制参考/故障上拉。GND为6/9/14/20/25/30/34/39，17个未用Pi端子明确留空。

Sharp资料：product/references/LS027B7DH01-sharp-2010.pdf，SHA256 997ecbcb7f020fbe077632dc90f6bf82d9e0e49ccf2211484093dec348965d98。第11页端子，第13页电平，第14页上下电，第15页串行与COM时序。FPC座Hirose FH12-10S-0.5SH(55)/C506791，供应商原封装保留，本版装在正面，保持厂家原生端子顺序及向-Y开口。

TI原厂资料：[TPS2553](https://www.ti.com/lit/ds/symlink/tps2553.pdf)、[TLV755P](https://www.ti.com/lit/ds/symlink/tlv755p.pdf)、[SN74AHC125](https://www.ti.com/lit/ds/symlink/sn74ahc125.pdf)。复用已核对DBV/PW封装及引脚。TPS2553采用KiCad SOT-23-6，1=IN、2=GND、3=EN、4=FAULT_N、5=ILIM、6=OUT。TLV75533为1=IN、2=GND、3=EN、4=NC、5=OUT。

母座：[Samtec SSQ-104-02-G-D](https://www.samtec.com/products/ssq-104-02-g-d)。已目视核对本地ssq-series-print.pdf第1页Rev BH，SHA256 3609be190ef021cc260abf423296449d797dd474fe1618dcf0fec719e2a05141；来源https://suddendocs.samtec.com/prints/ssq-1xx-xx-xxx-x-xx-xxx-xx-x-mkt.pdf。2×4、2.54mm间距/排距、0.64mm方尾、壳高8.51mm、焊尾4.93mm，壳长10.67mm、宽4.93mm。采用官方KiCad Connector_PinSocket_2.54mm/PinSocket_2x04_P2.54mm_Vertical，1.7mm焊盘/1.0mm孔。标准库3D不是该精确料号的制造模型，焊尾长度等不能用于装机定版；未验证公母插合高度及壳体避让。旧公针实物行顺序不作为兼容依据；模块必须遵循新母座1–8编号。

## 显示端子映射

| FPC针 | Sharp信号 | 本板网络 / Pi来源 |
|---|---|---|
| 1 | SCLK | LCD_SCLK，GPIO11物理23，经缓冲 |
| 2 | SI | LCD_SI，GPIO10物理19，经缓冲 |
| 3 | SCS | LCD_SCS，GPIO8物理24，经缓冲，高有效 |
| 4 | EXTCOMIN | LCD_COM，GPIO12物理32，经缓冲 |
| 5 | DISP | LCD_DISP，GPIO25物理22，经缓冲 |
| 6/7/8 | VDDA / VDD / EXTMODE | 共同V5_LCD，外部COM模式 |
| 9/10 | VSS / VSSA | GND |

AHC125由显示支路生成的3.3V供电。Sharp VIL上限0.15V；AHC小负载DC VOL上限0.1V，动态电平和边沿仍须在实际FPC末端测量。Pi侧五路各100k下拉。未用缓冲输入接地、使能拉高、输出留空；DISP无拖慢边沿的对地电容。

## 电源

Pi原生USB-C唯一输入。显示EN为GPIO24/物理18并以100k默认关闭；模块EN为Pi3.3V并带100k下拉。显示5V供LCD及缓冲LDO，模块5V供模块LDO，两路5V各10k泄放。FAULT开漏并联，由10k上拉到Pi3.3V，送GPIO16/物理36，只能报告任一路故障。

169kΩ±1%设置TPS2553，原厂上下界约136–187mA。模块正常预算100mA；LDO在5.25V、100mA时约耗散0.195W，样板需测温。2.2µF/50V/X5R/0805为CL21A225KBQNNNE，偏压后有效容量和LDO稳定性仍须实物核对，不能以额定电压代替容量证据。

外层1oz、10°C温升IPC-2221估算：0.5A约0.115mm、0.2A约0.033mm，设计电流下限统一至少0.20mm。实际输入/模块干线0.5mm，显示5V全网0.25mm，缓冲电源0.30mm。FPC采用0.15mm铜间隙；未通过降低电流预算解决DRC。双面地铺铜，18个明确定位的缝合过孔，无via-in-pad例外。

## 驱动约束（尚未实现）

1. 启动先令GPIO24和五路显示信号低；开启电源并稳定后按Sharp第14页清显存、使能DISP及COM，上电T3/T4各至少30µs。完整顺序以图纸为准。
2. SPI不超过2MHz，按Sharp位序和行协议；SCS高有效，不能直接使用Linux默认低有效CE0。模块CE1独立，共享总线只选中一方并切换对应速率/模式，空闲MISO高阻。
3. GPIO12硬件PWM持续产生COM输入。外部输入1–20Hz，COM反转对应0.5–10Hz，默认初试2Hz外部输入，实测后冻结。没有独立硬件COM看门狗，驱动退出/停机必须关闭显示电源。
4. 正常关机按Sharp时序清屏、DISP拉低并等待，再关GPIO24。异常拔USB-C的掉电顺序没有验证。
5. I²C使用Pi既有上拉，模块不得拉到5V，额外上拉须核算总阻值。扩展口只允许本板供电、3.3V逻辑、断电插拔。

## 未验证边界

检查通过不证明波形、COM持续性、5V压降、温升和模拟稳定性。原理图电气类型元数据仍不完整，不声明仿真或满覆盖ERC。装机需打开Pi USB-C，核实GPIO堆叠、连接器/散热器避让、支柱孔位、完整短FPC路径及锁扣操作。不得将本电气样板直接当作整机已验证安装板。
