# 手持终端外壳 — 两件式屏幕框

屏幕固定件为一体屏舱前框和等厚后压框，共两个硬质打印件。前框集成玻璃定位槽与遮边，删除独立内框、薄翻边、多级螺丝耳和独立排线护栏。外形保持76×59mm、13°，玻璃和FPC基准保持；0.5mm宽、0.3mm深浅分界线保留外圈4.75mm等宽区。玻璃口63.4×43.42mm，显示净口59.4×35.88mm，前侧挡边1.2mm。后压框2mm等厚、四耳共面，配2mm无胶后软垫；正面软垫0.2mm。软垫不是打印件。固定螺丝由硬止口承力，仍需实物验证软垫压力和玻璃安全。

机身宽76mm、深115mm，前沿名义约1.675mm；树莓派、基板、散热片、风扇与接口基准沿用。PCB绑定发布cd04f943ef57c8363e042d7d455cd9599f11065206ac235a43715b5c526e2ad6，STEP哈希fc6d293414ed15fcebd1226aa4a9bee691ebe59ee7340ee3075cb63742b08fa8。

## 当前结构

基板两枚独立打印螺丝垫片取消。两颗ISO4762 M2×3（头下3mm）直接贴合PCB底面安装孔区域；板底Z21.8、板厚0.8mm、原2.2mm孔及横梁位置不变。名义螺丝尖Z24.8，距平台/盖板底面2.2mm。套件短螺丝长度表拒绝3mm后，采用明确free标准3mm头/轴实现，接收孔仍由原套件方案生成，不增加盲孔深度。M2×4不得直接替代。

打印件的18处螺丝连接中，10处改M3；受低边沿、风扇窄耳和PCB间隙限制的8处保留M2。另6处板件/金属固定保留原M2/M2.5孔及螺纹。后压框加厚候选发生PCB干涉，故保留2mm等厚片及原孔位；没有增加打印件。

主紧固件采用10枚M3×6、90°沉头（默认参考ISO10642、头径6mm）：前拓展盖板4枚、底盖4枚、屏舱后侧2枚。现有M3×10与×12不用在这些短孔中。其余保留M2×4沉头6枚、M2×12沉头2枚、M2×3圆柱头内六角2枚、M2.5×10沉头4枚；用途及最低采购数量见产品螺丝清单。沉头长度含头，圆柱头长度从头下量。

打印沉头座保持90°，口径比对应标准头部增加0.4mm、深度增加0.2mm，硬件名义沉入0.2mm。沉头负形由库内标准轮廓生成；套件不支持M3沉头6mm长度时使用明确拒绝后的标准头/座自由实现，接收孔与长度选择保留套件结果。接收孔不跟随沉头放大。PLA自成形螺孔、扭矩和重复拆装寿命仍需实物验证。

前拓展盖板70×37×2.4mm，R4、上沿0.4mm倒角，底面Z27、顶面Z29.4，59×22mm孔距，世界X±29.5、Y-45/-23。底部仍是完整平面，不含定位凸台；拆盖沿+Z。盖板只能配本版上壳。

屏幕后压框2mm等厚，螺丝耳5.4×6mm，四枚M2×4、2mm名义接收啮合。压框上接触面、玻璃、0.2mm前软垫与2mm后软垫基准均保持，不靠螺丝压紧玻璃。底盖四枚M3×6仍用3.6mm名义接收啮合。屏舱前侧低边沿保留M2×4，后侧改M3×6；前侧工具杆通道Ø2.4、后侧Ø3.4mm。


屏舱与上壳采用四个从内侧向上拧入的隐藏固定点。前侧世界坐标(±34.4,4.2)mm，后侧(±27,51)mm；孔位及套件切孔由上壳统一定义，前框读取同一组接口。前框四处接收筋直接连到顶面，四个接触脚向下跨过0.3mm分缝并坐实上壳顶面Z27mm，外圈分缝保持。前接收孔选择1.2mm名义啮合以保留低前沿封底，后接收孔3mm；实际斜面上方1.2mm闭合封底由实体负探针断言。上壳有对应承力舌和从内侧进入的前侧Ø2.4mm、后侧Ø3.4mm工具通道；前侧工具通道位于原内腔内，不额外削薄2.4mm名义直壁；原底沿倒圆另计。前侧使用两颗ISO7046 M2×4、后侧两颗M3×6，不能混用长短。四颗螺丝只连接前框与上壳，不把玻璃纳入紧固叠层。后压框前侧两边各有一处简单避让缺口，与承力台及螺丝头保留0.3mm名义余量。前框、上壳、后压框须使用本版配套模型；均为独立单件打印，没有增加支架。

- **树莓派改由底盖承载。** 上壳内四个悬挑的树莓派托耳已删除。底盖在官方 49×58 孔位上有四根 Ø5.6 立柱（现版世界坐标X=-18.5/30.5、Y=-27/31）（顶面 Z5.3 = 板底），ISO7046 M2.5×10 沉头螺丝从底盖外侧穿过立柱和树莓派板孔，直接拧进 Geekworm P165-B 散热片自带的 M2.5 金属螺纹（计入沉头余量后名义啮合约3.1mm）。没有打印螺纹参与树莓派固定。
- **上壳竖直落下套住树莓派。** 背面 USB/网口窗口改为通到下沿的开口槽，底盖上对应的填块把窗口下方补回原来的窗台高度，合上后外观与之前一致。右侧 3.5mm 音频座和 USB-C 伸入侧壁的部分各有一条内侧盲槽通到下沿（直壁段外侧名义留1.2mm / 2.5mm实壁，底沿倒圆另计），树莓派右后板角的让位也通到下沿。保留直落装配结构与通到底沿的接口槽。此前85mm版做过0.5–8mm竖直行程检查；本次76mm版补充检查名义就位无干涉，实际GPIO对位、竖直插拔及打印公差仍需试装。
- **上壳按“顶面朝下”打印。** 顶面完全平整（拓展盖板不再下沉，改为放在顶面上，凸出 2.4mm，0.4mm 倒角），顶面外沿为平直边，屏舱侧壁与机身齐宽，后壁自接缝向上向前倾约26.29°，下沿接齐机身后沿，仅保留0.3mm装配分缝。底盖螺丝座改为从顶面一直到底盖的整高立柱（左前螺丝位从 (-32,-48) 移到 (-32,-15)，左后从 y47 移到 y51.5，避开风扇和屏舱开口）。PCB 横梁在拓展开口内保留顶板条，后部 PCB 导轨改为 51° 斜面一直连到顶面。风扇的两根固定柱从顶面垂下。打印方向保持顶面朝下；圆角排气孔宽2.4mm。前次悬垂面积统计不作为齐边屏舱版本的定量验证，切片时仍需核对实际桥接与层数。
- **风扇改为独立风扇托架。** 原来壳内的风扇底座（需要大量支撑）和单独的压框合并为一个打印 U 形托架：底板、两侧导轨、带 13.6mm 进风口的顶板和两只整高螺丝耳。底板朝下打印，只有一段 17mm 顶板桥接。两颗 ISO7046 M2×12 沉头螺丝从下方穿过螺丝耳拧进壳顶垂下的两根柱（X=-28.5，Y=-51.2/-30.8）（打印自攻接收孔，4.4mm 啮合）。三片 0.5mm 硅胶角垫保留在风扇顶面与托架顶板之间。
- **屏幕框连接**：一体前框加2mm平板后压框，前螺丝轴局部(±27,-26.25)mm、后轴(±20,25.5)mm；四个后耳同一平面。M2接收孔由printed-screw-joint-v1生成；ISO7046标准沉头头/座在套件拒绝后作明确free回退。后软垫名义2mm，压框顶面局部Z=-5.04mm；前软垫和玻璃位置保持。无独立定位框、后翻边或FPC护栏。
- **侧接口给插头胶壳让位。** 原直通孔主要围绕金属头：USB-C10.2×5.2mm、micro-HDMI7.4×4.2mm、音频孔Ø7.6mm；Pi4B模型中USB-C座最外缘X35.2、音频座X36.5，而外壁X38，分别缩进2.8/1.5mm。现在USB-C贯通净口13×7mm（外口14×7.6mm），每个micro-HDMI12×7mm（外口12×7.6mm），音频口全壁贯通Ø11mm。矩形孔R1，入口向上下各外放0.3mm；USB-C左右另放0.5mm，HDMI左右不额外放大，以保留两孔间1.5mm隔筋。USB-C到首个HDMI的外侧隔筋1.8mm，矩形孔下缘至壳体下沿最小约1.68mm；音频孔不扩大下沿入口，保留名义1.4mm下边条。主体其余侧壁仍2.4mm，Pi、基板及全部安装位置不动。
- **胶壳包络为默认值，不是标准线材认证。** 源内独立负探针检查USB-C12×6mm、每个micro-HDMI11×6mm的方角胶壳从X34.2到X50mm、音频Ø10mm从X36.5到X50mm的直线进入通道；最终上壳（包含后加固定柱）与这四个包络的共享体积均为0，成功构建即通过断言。这只验证壳体让位，未验证具体线材的插入止挡、接触长度、锁止、弯头转接器或两条实物HDMI线同时连接。没有选定线材MPN，也没有把包络发布为采购件实体。
- **PCB 固定螺丝** 改为ISO4762 M2×3圆柱头内六角，直接贴合PCB底面的安装孔区域，不装垫片，因横梁现在背靠顶面，接收孔改为盲孔、2mm 啮合，螺丝尖名义Z24.8，停在顶面以下2.2mm。
- 拓展盖板为70×37×2.4mm平板，R4，底部无定位舌或凸台，四角M3沉头孔按59×22mm布置。底面Z27、顶面Z29.4；母座名义空气间隙约0.745mm。

检查范围：本版上壳、前框、后压框及四颗屏舱固定螺丝的局部精确碰撞检查无共享实体体积；玻璃与软垫组亦无干涉，前框与上壳接触距离为0。接收孔上方1.2mm闭合封底及真实PCB/螺丝刀路径由构建断言检查。前框及平板后压框均有单实体、有效几何和硬件逐实体名义干涉断言。检查基于当前真实绑定Pi和PCB；玻璃仍为用户要求的名义参考占位，不是厂商STEP。整机复杂导入件的自动碰撞检查有耗时上限，不能作为完整公差或实物验证。没有实物打印、软垫压力、原生排线插接、插拔寿命或温升试验。

## 屏幕装配定位

屏舱前框的几何已包含13°倾角和8.010909266mm屏面抬高，因此对象仅平移到(0,21.521201483,27.3)mm，不再叠加旋转。玻璃、前后软垫、后压框及四颗后压框螺丝共用屏面坐标：原点(0,21.521201483,35.310909266)mm、绕X旋转13°；玻璃偏心与厚度、螺丝孔位及头部方向已在各自局部几何中表达，不再重复计入对象位置。

当前装配图及底面、侧面视图已检查。屏幕相关10个对象的45组配对无实体干涉；前框/上壳、前框/前垫、前垫/玻璃、玻璃/后垫、后垫/后压框的距离均为0mm。此次移动的前框、玻璃和四颗螺丝与绑定的Pi及当前基板逐实体精确检查共享体积均为0。原有打印、公差、软垫压力和原生排线实物试装限制继续适用。

## Making and assembly — 当前版本

**建议打印方向（切片中复核桥接）**
- 上壳：顶面朝下平放，四个排气孔为胶囊形。使用免支撑切片预览复核接口上沿桥接；放大后的侧孔宽约12–14mm，保留HDMI隔筋分段桥接，旧开孔的短桥接统计不能直接沿用。默认PLA、0.2mm层高仍需按打印机试配。
- 底盖：外侧朝下平放，立柱和填块向上。
- 风扇托架：底板朝下。顶板是 17mm 桥接。
- 拓展盖板：平整底面朝下，四角沉头孔朝上；无底部定位凸起。
- 一体屏舱前框：将13°屏幕正面贴平热床，定位槽和侧壁向上。浅分界线跨距仅0.5mm；后壁仍约26.29°内倾。前框不再有独立薄翻边或小护栏。后压框：大平面贴床，螺丝孔轴朝上，2mm等厚板，没有悬空多级耳。切片预览复核局部桥接、首层与孔补偿，不宣称已实打免支撑。
- 默认 PLA、0.2mm 层高；M2/M3自成形孔建议先打一个校准件试配。

**装配顺序**
1. 把 P165-B 散热片（带导热垫）对准树莓派；整体放到底盖四根立柱上，从底盖外侧拧入 4 颗 M2.5×10 沉头螺丝，交替轻紧到贴合，不要用螺丝力去压芯片。
2. 上壳顶面朝下放好。先把风扇放进风扇托架（出风口朝左侧壁散热槽、进风面朝顶板），三片角垫在风扇顶面；托架用 2 颗 M2×12 拧到顶面垂下的柱上。
3. 屏舱前面朝下，铺0.2mm无胶前垫，玻璃从背面进入定位槽（FPC向前），铺2mm无胶后垫。平板后压框四耳落到硬止口，四枚M2×4沉头交替轻紧，禁止靠拧紧螺丝强压玻璃。原生排线通过开放缺口后接J_LCD；不能夹在压框或柱之间。把前框四脚落到上壳顶面的对应承力舌，从上壳内侧向上拧入四颗屏舱固定螺丝（前侧M2×4、后侧M3×6，按零件清单，勿混用）。此时Pi和散热片留在拆下的底盖上，细杆十字螺丝刀从内侧盲槽直达螺丝头；屏舱锁紧后再装基板。旧独立定位框、旧压框及1mm后软垫不得混用。风扇线接J_FAN，基板沿后部导轨就位，以两枚M2×3直接固定横梁，不装螺丝垫片。
4. 把上壳翻正，对准底盖上的树莓派**竖直放下**：背面接口滑入开口槽，音频座和 USB-C 沿内侧槽滑入，GPIO 插针最后约 5mm 插入底板母座。不需要撬动或掰任何部位；如果下落受阻，抬起重对，不要硬压。
5. 底盖4颗M3×6 沉头从下方拧入整高立柱，对角交替轻紧。
6. 拓展盖板的平整底面贴合上壳平台，对准四角孔，以4颗M3×6沉头螺丝交替轻紧；不得用螺丝强拉翘曲盖板落座。

拆机时先软件关机并断电，卸底盖4颗螺丝，向上直接拿起上壳（GPIO随之拔出），树莓派和散热片留在底盖上。需要拆屏舱时，先释放J_LCD锁扣并脱开屏幕排线，再从上壳内侧卸四颗屏舱固定螺丝，随后取下一体屏框；不要带着Pi从接口之间斜伸工具，也不要卸错压玻璃的后压框螺丝。

**仍未验证**：没有实物打印、试装、插拔或温升测试；侧孔须用用户实际USB-C、micro-HDMI和音频线确认完全插入、拔出及胶壳间隙，不能将默认包络视为通用线头兼容认证；GPIO 插入对位依赖接口槽与底盖内沿的定位，第一次装配请慢放并观察插针对位；打印自攻孔的拧紧寿命未测；拓展盖板凸出2.4mm 是外观上的变化。

---

# 历史记录（以下为此前版本的说明，凡与上面"当前版本"冲突的内容均已被取代）

## 显示屏占位件

按用户要求新增独立可选择、隐藏和移动的 display_placeholder（LCD placeholder）。它是视觉与名义空间检查用占位实体，不是厂家 STEP 或可打印零件。包络依据 Sharp LCY-1210401A LS027B7DH01 原厂 PDF 第26页：62.8×42.82×1.64mm，不含 FPC 和突出部。沿用现有有效显示区中心基准，局部中心 Y=-1.77mm，正面 Z=-1.4mm、背面 Z=-3.04mm；装配位置(0,21.521201483,35.310909266)mm，绕X倾角13°，位于既有前后软垫之间。占位表面默认灰绿色玻璃材质，仅用于视觉表达。

最终模型 b3bf3c42360470127cf8ff87b8533f88304cd0ea45645bfade53c14fa769713c 已目视检查斜视和顶视。占位件与 bezel、fascia、front_cushion、rear_cushion、retainer、shell、pi_baseboard_lite、pi4b、passive_heatsink 共9组局部检查均无共享实体体积；前后软垫可接触，占位尺寸和安装参数可调整。整机自动检查另有39对复杂实体未判定，不能据此宣称整机所有干涉已验证。未模拟排线、有效区图像、玻璃层叠或公差极限，完整原生排线插接与实物试装仍待确认。以下关于屏幕尚未建模的历史描述由此占位件更新替代，历史制造与装配限制继续适用。

### Making and assembly — placeholder

占位件不加入采购清单、不作为打印件。真实 LCD 仍使用既有屏舱、定位框、软垫和后压框的装配方案；占位模型不证明偏光片压力、真实厚度公差、排线插接或屏幕电气功能已通过。装配时不要让 LCD 承受螺丝夹紧载荷。


## 历史设计参考（以下不是本版装配依据）

以下保留原有制造及调试记录，旧尺寸、旧PCB发布与旧紧固件均不能覆盖本节之前的当前结构。

# 独立平面拓展盖板与背面凹腔（历史：已改为放在平整顶面上）

前平台盖板已从上壳源部件拆出，成为独立CAD零件front_module_cover，发布独立对象front_module_blank。可单独选择、隐藏和移动；卸下四角M2×4螺丝后沿+Z取下整块盖板，供自制拓展件替换。盖板模型用自身上表面Z0为局部基准，装配位置(0,-34,28.4)mm。外形70×37mm、主板厚1.4mm，采用平面承托和四角安装点，底面无定位凸起，PCB仍由上壳独立支撑。

盖板外表面恢复完全平整Z27，中央不凸起也不贯通。背面按现有HLE母座包络掏盲凹腔，名义空气间隙默认0.1mm，中央非承力顶壁约0.645001mm、默认下限0.6mm。薄壁例外仅供视觉与样机空间复核，低于常规FDM外壁建议；实际打印、收缩、变形和母座高度公差必须试配，未宣称生产强度或防护能力。既有两枚1.2mm厚PCB螺丝垫片保留，螺丝尖端名义距盖板0.5mm；主壳壁与屏幕结构未改。

PCB继续使用发布8816a764c91d71af56bd3042eeca5a34a6f0ec2096f8967712fe44e23a199537，STEP哈希7be47336983ab285b75e6c7d2a93d2c29418654a82397f66cf8ef8e56ad6b53d；装配(-100,81,21.8)mm、零旋转。本次提交模型62c250f7d454362081b060b4c0ce1341a9644d2f06e0e150ab746212e5f5b7e7通过独立零件归属、平整顶面、单实体、三处原开孔封闭、中央薄顶及相关硬件零交叠检查；卸四角盖板螺丝后向上0.1/0.6/1.4/2/5/10mm的检查位置均无干涉。自动整机5对复杂实体未判定，补充检查仅覆盖盖板变更与拆卸路径；FPC完整尾部就位、风扇线束、温升及实际打印配合仍未验证。配套零件清单为盖板1件、PCB垫片2件，四角M2×4螺丝4枚和PCB固定M2×4螺丝2枚保留。

屏舱下方左后侧的四条进气槽已按用户要求去掉，左侧该区域恢复2.4mm连续实壁；左前侧四条风扇排气槽保留。当前模型f7a2881b16c8992e6aef26389e47548bad0c4b7db00c64a95b19a198af783eeb已目视核对左侧及背侧：原进气范围224.64mm³全部为壳体材料，四个排气窗口内壳体体积为0。补回的侧壁与所有已发布硬件及PCB物理实体的精确共享体积为0，壳体仍是单一有效实体。整机自动检查有32对因复杂度或耗时未判定，补充检查仅验证封孔区域，不声明整机所有干涉已通过。封闭后的外部补气路径、整机气流和温升仍未测量；不增设替代进气孔。

## Making and assembly（历史）
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.

The rear-loading locator pocket is supplemented by the retained rear frame as described above. Proposed later assembly is screen into removed pod from rear, fit low-stress support/retainer, connect tail with full latch access, then attach pod. Do not suspend LCD by FPC, stick adhesive on polarizer or bend at glass edge. Enlarged interior deck opening and thin front regions require strength checks. Failed printed-screw-kit candidates committed no geometry; retain their failure record rather than substituting hand-modeled screw joints.

### Current prototype update（历史）
The preceding making notes are retained historical records: the statements about no rear retainer/fasteners and entry-only FPC describe the previous revision and are superseded by this query's geometry above. There has still been no physical print or assembly test.
Default PLA is a CAD prototype assumption; calibrate M2 holes and verify local thin-wall strength. Print screw axes upright where possible; sloping housing and mounting receivers may need supports. Soft pads are die-cut, not FDM parts. Assemble glass/pads/frame on the removed inverted pod, alternate the four screws only to their hard stops, shape the tail once with a radius guide, insert its stiffener and close the latch before pod installation. Remove Pi for tool access if necessary. Verify pad chemistry/compression and display image uniformity before powered integration. The future supported connector board is not part of this delivery.

Front module making update: print the flat blank underside down, countersinks up. The locating tongue is removed; retain the four kit-owned ISO7046 M2x4 joints. Check printed flatness and seating before tightening. Disconnect all power before opening or changing a GPIO module.

Current PCB review addendum: historical making instructions above do not validate the new horizontal tail route. Do not treat the current assembly as fitted until the height and contact-direction conflict is resolved.

### Raised board assembly update（历史）

The prior no-fastener/17.5mm/socket-height-conflict notes above are historical. Current PCB is mounted to the upper-shell beams and rear guide atZ21.8 with higher ESQ and lower HLE. Fit the board and start both M2x4 screws loosely before tightening to contact; the removable module blank is not its support. Keep screw-tip holes clear. Assemble the screen pod off the case for latch access. Do not force or repeatedly bend the tail; current bottom-contact installation remains unresolved, so do not treat this draft as a powered or fully fitted screen assembly. The1.555mm air gap is not a cooling-performance claim.

### Current top-contact assembly update（历史）

Earlier bottom-contact conflict and1.555mm overall-minimum statements are historical. Current FH12A top-contact orientation and10terminal mapping are resolved. Current minimum ordinary-component air is1.505918mm after buffer/capacitor pockets. The board mounts to upper-shell beams; prototype the estimated native-tail seating with the screen pod removed and latch accessible. Preserve its straight stiffener, do not twist the exposed-copper face, and avoid repeated folds. Exact physical fit, thread life and temperatures remain untested.

### Cooling assembly update（历史）

Current cooling adds two real heatsinks, a real manufacturerfan model, an integralupper-shell cradle/duct and twoM2x4 kit joints. Print shell and collar separately; the inward cradle and duct roof require supports and careful cleanup. Pads and TIM are die-cut stock. Assemble fan with inlet up and outlet rearward, start bothcollar screws loosely, tighten alternately to the matched standoffs, check blade freedom, thenfactory-prewire/strain-relieve leads and installPCB. Usercold-plugsPi with prebondedCPU/RAM sinks and performs no soldering. Do not allow case loads on the chips or let wires cross the inlet. Inspect actualfan thickness and rebuildhard-stop height before printing if it differs from4.5mm. Detailed assembly/thermaltest procedure is in the cooling assembly document. No physicalprint, temperature test or plug qualification has been performed.

### 当前Pi4被动散热片与HAT风扇更新（历史）

上面的Fischer双片、后向风扇出口和高风罩是历史装配记录，以本次顶部说明和当前装配指南为准。打印上壳和1.4mm压框分开；下托耳/内伸支架需要试排方向和局部支撑，勿在电气焊盘接触处残留支撑。四角沉头只在打印件，不能锥削Pi孔。确认P165-B实际底面与贴片落差、金属螺纹深度后再四角交替轻紧，不允许强压芯片或弯PCB。先装前部风扇、按实测厚度调整软垫/限位，检查转动，再装Pi/HAT。HAT底面J_FAN插预装工厂两针线并松弛固定；用户无需焊接。风扇入口向上、出口前向，线束按2mm弯曲半径放在前沿上方，不遮入口。屏舱拆下接FPC，折回露铜向上，不强拉估计长度的原生排线。所有历史"尚无风扇插头"或"按钮干涉未处理"的陈述被本次模型取代；仍无实际打印、插接、温升测试。

### 新版PCB同步装配更新（历史）

当前接口是C5373447上接触抽拉座，均匀拉推锁扣两端，不能掀开。元件最小空气间隙1.555001mm、保守锁扣空间2.7mm。先试配局部薄顶和M2接收端；卸下屏舱，在软垫上支撑玻璃，实测尾部长度、补强位置和接口止挡，再按Sharp允许区弯折、铜面朝上插入。不要以拉伸、扭转或反复折弯补偿。完整尾部插接尚未验证。J_FAN在正面后部，旧底面短线束记录属于历史，不能直接沿用。没有实际打印、插接或热测试。

### 底盖固定与侧孔试装更新（历史）
此前"底盖无固定件"的段落是历史记录。当前底盖单独平放打印，定位边向上；上壳托耳与内伸结构需要在切片器中检查方向和局部支撑。采用PLA样机默认，先校准M2打印接收孔；沉头座勿残留支撑。四枚M2×6从底部插入，对角逐步轻紧到贴合，不以拧紧消除翘曲。断电后卸下四枚底盖螺丝，再沿-Z平移底盖，浅定位边没有卡扣，Pi和HAT仍由上壳承载。试插实际USB-C、micro-HDMI、3.5mm插头，确认插头肩部能靠近接口、能完全就位和拔出，再决定是否微调开孔参数。没有实际打印、拉拔或插拔试验；无需热熔铜螺母。

### 无侧面按钮装配更新（历史）
当前上壳取消侧面按钮和按钮帽；此处是上壳连续全厚侧壁，不安装开关或封孔塞，不再打印power_cap。上文橙色按钮、按钮开孔和按钮干涉的内容是历史装配记录，当前橙色外观只保留屏舱。使用系统软件正常关机后再断开Pi原生USB-C电源；没有新增按钮功能。其他底盖、屏幕、风扇装配说明保留，仍需实物试装。

### 独立平面盖板装配更新（历史）
打印或制作盖板时保持底面平整，无定位舌、凸台或母座局部凹腔；名义板厚1.4mm，底面Z27、顶面Z28.4。盖板对母座名义间隙约0.745mm，仍需检查首层、翘曲、孔位和实际落座，不能靠螺丝强拉到位。更换模块前先正常关机并断开全部供电，卸四角螺丝后沿+Z提起；PCB、底盖与屏舱保持固定。自制件沿用70×37外形和平面承托、四角孔位。未作实物打印或承载测试。

### 左后侧进气槽取消（历史）

打印上壳时该区域为完整2.4mm壁，不再清理或后加工原四条进气槽。保留左前侧排气槽，装配后确认内部吸气净空与排气窗通畅。封闭后的进气路径及温升必须在样机上测量，未作冷却性能结论。

### 组件角色分类（历史）

当前整机39个对象中，36个可编辑对象已显式声明role：12个part（上壳、底盖、屏舱、后压框、屏幕定位框、风扇压框、定制风扇软垫、两枚PCB垫片、前后屏幕软垫、独立拓展盖板）；20个fastener（现有所有螺丝）；4个reference（屏幕占位件、P165-B散热片参照、两片套件TIM名义间隙参照）。仅增加publish的role关键字，未改几何建模表达式、尺寸参数或装配位置。part包括定制裁切软垫，不能把全部part直接当作FDM打印件。

三个受管STEP导入对象pi4b、cooling_fan、pi_baseboard_lite仍未显式标注role，均应归类reference。现有cad.edit import接口没有role参数，重新绑定相同Pi资产返回design_unchanged；imports目标不能作为普通Python单元编辑。此次保留真实导入资产及其位置，不绕过受管源编辑规则。未标注导入参照可能仍进入默认零件导出，补齐这些角色前不要把导出对象清单当作纯定制零件清单。

### Making and assembly — role分类补充（历史）

role只描述交付分类，不增加打印、装配或电气验证。现有所有制造与装配限制继续适用，屏幕占位件、购入散热片及其TIM名义参照不作为定制制造件。螺丝属于购入fastener，软垫按既有材料与裁切方法制作。完整实物试装与温升仍未完成。
