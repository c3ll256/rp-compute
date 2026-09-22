# 后方与侧面接口交接 · 2026-09-22

## 本轮结果
保留13°浅斜屏舱和水平前平台。取消前面充电开口；Pi四个USB-A（两组双层）及RJ45朝后，两个micro-HDMI和原生3.5mm接口朝右，基板充电12×5mm暂定孔移到左侧。单电源按钮仍在右侧。无PCB设计。

底座85×115×27mm（原20mm，默认增加7mm以容纳真实Pi接口）；含按钮宽85.65mm，壳体总高42.467515mm。Pi接口最突出后面0.36mm，含模型总深115.36mm。外壳名义壁厚2.4mm，底盖2.4mm，0.3mm视觉缝。后排接口之间窄筋及桥接需制造阶段加强/打印验证，不声称可直接打印。

## 真实Pi几何
内置FreeCAD资产安装失败：源文件不存在；从step.parts取得精确型号Pi4B参考STEP，校验SHA256=1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe，89实体。未用Pi5/Pico或自制占位体替代。来源及绑定资产见source/design.json和product/bom.json。第三方模型不是实际板版本/制造公差证明；RAM不机械区分。

Pi placement=[39,-30.5,7]、rotation=[90,90,0]。原文件板长轴X、厚度Y、宽度-Z；转换后X=原Z+39、Y=原X-30.5、Z=原Y+7。主板包络X[-17,41.5]、Y[-35,57.86]、Z[3.45,23.34]mm。GPIO针顶约Z17，母座及PCB堆叠尚未放入，不宣称电气堆叠适配。

## 开孔
后面Y=57.5：RJ45中心X=-6.75/Z14，17.5×17mm；中间USB中心X12/Z15，16×19mm；右USB中心X30/Z14.5，18.5×20mm。右侧X=42.5：micro-HDMI中心Y=-4.5及9/Z8.6，10×6mm；AV中心Y23.5/Z10，直径10mm。左侧X=-42.5：充电中心Y=-37/Z12，12×5mm。

Pi自身USB-C只有内侧盲让位、外壁保留1.5mm，不开放外部插拔；这不是已完成的电气联锁盖。microSD暂定断电拆底维护，无正面接口；取卡手指及拆装路径待验证。

## 屏舱及维护
屏舱placement=[0,21.521201483,27.3]，内框=[0,21.521201483,35.310909266]、rotation=[13,0,0]；面长65mm、宽77mm不变。前边Y=-10.145825723不变，前沿名义顶面Z28，含0.3mm分缝高出平台Z27共1mm。改变板姿态、底座尺寸或屏角需要同步更新开孔与绝对装配位置，不是自动联动。

## 检查
最终revision：59a92a25ffb35e410960806eab6c57a2dcca3fff65737c2e6d4c8975142d086f。
内核94有效实体（5外壳+89板模型）。自动Pi/壳精确检查因89候选实体上限返回未确定；补充逐实体OCC相交检查使用已提交STEP，只读、无改模，结果无大于1e-5mm³相交，见port-clearance-check.json。它不取代自动检查，也不是插头/插入路径验证。
ISO证据：.work/cache/cad-workbench/designs/handheld_computer/observations/c9cdf8a35da2d8c8941913ff39b7584af691ee66a647033b73867e8aaf36ac4e/look-107f9555a904ff7801d7d90e/workbench_iso.png
右视证据：.work/cache/cad-workbench/designs/handheld_computer/observations/c9cdf8a35da2d8c8941913ff39b7584af691ee66a647033b73867e8aaf36ac4e/look-107f9555a904ff7801d7d90e/workbench_right.png

## 未完成事项
仍为外观及端口排布稿。紧固/导向、GPIO母座与基板、实际插头壳和网线卡扣/手指空间、LCD/FPC、电池整包、散热及联锁均未验证。充电口仅提出PCB接口位置；没有内部转接线假设。屏幕窗口是空孔，不是LCD模型。当前不可作为完整可打印/可通电装机产品。

## 本轮1mm前沿修订
参考screen_front_1mm_markup。fascia_front_height=0.7mm（加0.3mm装配缝为用户要求1mm），圆角之前的名义尺寸，不把曲面最低处当顶面。内框同步下降5.3mm。底座、Pi及接口几何未改，旧Pi/壳逐实体检查仍仅对应那对未改几何。当前构建94有效实体，无新增相交；自动Pi/壳检查仍超复杂度限制，不声称全自动碰撞检查通过。前唇局部薄边强度/打印待验证。
最新ISO：.work/cache/cad-workbench/designs/handheld_computer/builds/59a92a25ffb35e410960806eab6c57a2dcca3fff65737c2e6d4c8975142d086f/validated/previews/workbench_iso.png
最新右视：.work/cache/cad-workbench/designs/handheld_computer/observations/59a92a25ffb35e410960806eab6c57a2dcca3fff65737c2e6d4c8975142d086f/look-18967734b25ff39dc61ba003/workbench_right.png

## 后续屏幕空间修订
当前机械状态以screen-installation.md为准。内框49mm深并增加玻璃定位槽；屏舱及底座增加内部让位。原1mm前沿和外部端口不变。固定压框及完整FPC路线仍受阻，不能宣称已完成安装。
