# 屏幕与8针GPIO紧凑基板

按用户最新要求保留单块紧凑板、水平侧插FPC和原生排线轻弯。31个实装元件与电气拓扑保留；Pi原生USB-C供电，无电池、充电、升压、MCU或音频。

## 已实现接口与电路

正面J_LCD为Hirose FH12-10S-0.5SH(55) / C506791，10芯0.5mm、0.30mm排线、底接触、开口朝板+Y。背面J_PI为Samtec SLW-120-01-G-D，正面J_MOD为SLW-104-01-G-D；两者2.54mm双排，实物壳高4.57mm、焊尾2.92mm、允许插入2.16–2.92mm。标准KiCad母座STEP仅为封装位置代理，不是准确SLW高度模型。

J_MOD针号1=AUX_3V3，2=GND，3=GPIO2/SDA，4=GPIO3/SCL，5=GPIO10/MOSI，6=GPIO9/MISO，7=GPIO11/SCLK，8=GPIO7/CE1。数字针号与Pi映射已核对，不是Pi前8针同序。模块预算100mA、3.3V逻辑，断电插拔，不支持外部模块电源或热插拔。

两个TPS2553分别限制显示与模块电流，两个TLV75533分别提供缓冲器和模块3.3V；两个SN74AHC125缓冲显示五个信号。GPIO24控制显示电源，GPIO12产生COM，GPIO25控制DISP，GPIO16读合并FAULT。

## 实际布局与制造

外包络40×83.5mm，净面积2284.54mm²，比旧70×104mm发布板减少68.6%。GPIO窄条局部17mm，尾部15mm；下端电路岛40×25.5mm，侧面小承载区用于FPC与缓冲器。尺寸是本轮默认布局值，并非用户指定值。

板厚0.8mm，四层FR4、内外1oz。双层经多次调整仍有信号拥堵和接地铜皮断开，四层作为本轮默认实现增加回流空间；成本会高于双层。GND在top/inner1/bottom铺铜，inner2参与走线。保留0.15mm最低铜间距、1mm铜到板边、0.6/0.3mm通孔过孔；没有使用焊盘内过孔例外或降低制造下限。500mA输入0.50mm实际走线，0.31mm最低宽度按1oz内层IPC-2221、10°C升温计算；200mA支路最低0.20mm。

左边缘增加屏幕固定螺钉避让缺口，原屏幕与螺钉位置不变，目标间隙0.5mm。

两枚2.2mm非金属化工装孔位于板(-16,-13)/(16,-13)mm，所有层保持2.5mm半径禁布区。外壳尚无对应固定支柱，工装孔不代表已经装壳固定。

## 机械坐标和范围

板坐标X=-20..20、Y=-35.5..48mm；板到世界XY平移(0,-19)mm。J_PI针阵列中心(-13.5,21)变为世界(-13.5,2)，J_MOD中心(0,-15)变为(0,-34)，位于前舱开孔中央。J_LCD正面原点(0,25.7628506593)变为世界(0,6.7628506593)，水平侧插。

板前缘世界Y=-54.5mm，相对壳内前边-55.1mm仅0.6mm名义平面余量。排线总长暂取13.7±0.5mm、非接触间隙每侧0.5mm；这是用户授权的默认估计，不是实测或制造公差。当前平面FPC与原倾斜、倒置连接器目标不同，必须核对接触面、针1、插入深度和高度，不能用“排线可以弯”替代装配尺寸验证。

## 验证和发布

2026-09-30最终check通过：全部信号、电源、GND连通，KiCad DRC零错误、零未连通，无焊盘内过孔，放置与板边检查通过。已查看正反面布线预览并核对J_PI/J_LCD/J_MOD数字针序。36枚过孔均0.6mm外径/0.3mm钻孔。

发布a183ffa45c8d8cf64f65fdf30fee1c9048fcdda8b56f28e06d5ca1ee549fda45，Build467880f8bd542495d5a913c9ec667aa2390df76883c52231dcd351f133155db3。制造、装配和机械文件三个发布区均已生成。所有BOM元件当前声明手工装配；导出的JLC格式CSV不代表已验证自动贴片订单。四层内外1oz是本次DFM检查条件，不能直接改成双层或其他铜厚下单。

新版STEP已用于CAD装配核对；整机是否可安装以enclosure-interface-review.json和CAD实物体碰撞结果为准。电气上电、显示波形、温升、短排线接插和打印装配没有实测。

## Making and assembly

全板按手工样板装配，不声明JLC自动贴片套餐可直接下单。先焊背面小件，再焊正面FPC座、缓冲器及电源支路，最后焊40针母座及8针母座；核对1脚后再装Pi。实际装配顺序仍需样板验证。

首次不装屏幕和模块，检查无短路，再由Pi USB-C供电，测试3.3V模块支路、GPIO24控制的显示5V及两路限流/FAULT。屏幕端实测须保持4.8–5.5V；驱动准备好且COM波形验证后才接屏。工装孔不替代Pi的独立固定。

## Completed enclosure review
The exact current release is installed in CAD at translation[-100,81,17.5]mm, zero rotation. The revised notch gives0.737409mm exact clearance to the retained front-left screen screw, above the0.5mm default. The released substrate and component bodies clear the listed shell/retainer/panel-envelope probes except two generic socket-model overlaps; these do not qualify actual SLW mating. Horizontal FPC remains selected. Keeping curvature inside Sharp’s recommended0.8..6mm bend region yields an optimistic height deficit of at least2.043738mm at the retained screen/board stack. Tail13.7±0.5mm remains an authorized estimate and cannot resolve this height deficit by itself. Assembly is not qualified. Next architecture choice is a small raised horizontal FPC board, or a reworked single-board GPIO/front-module stack.
