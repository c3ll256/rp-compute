# 独立平面拓展盖板与背面凹腔

前平台盖板已从上壳源部件拆出，成为独立CAD零件front_module_cover，发布独立对象front_module_blank。可单独选择、隐藏和移动；卸下四角M2×4螺丝后沿+Z取下整块盖板，供自制拓展件替换。盖板模型用自身上表面Z0为局部基准，装配位置(0,-34,27)mm。外形70×37mm、主板厚1.4mm，原定位座、定位舌与四角安装点保持，PCB仍由上壳独立支撑。

盖板外表面恢复完全平整Z27，中央不凸起也不贯通。背面按现有HLE母座包络掏盲凹腔，名义空气间隙默认0.1mm，中央非承力顶壁约0.645001mm、默认下限0.6mm。薄壁例外仅供视觉与样机空间复核，低于常规FDM外壁建议；实际打印、收缩、变形和母座高度公差必须试配，未宣称生产强度或防护能力。既有两枚1.2mm厚PCB螺丝垫片保留，螺丝尖端名义距盖板0.5mm；主壳壁与屏幕结构未改。

PCB继续使用发布8816a764c91d71af56bd3042eeca5a34a6f0ec2096f8967712fe44e23a199537，STEP哈希7be47336983ab285b75e6c7d2a93d2c29418654a82397f66cf8ef8e56ad6b53d；装配(-100,81,21.8)mm、零旋转。本次提交模型62c250f7d454362081b060b4c0ce1341a9644d2f06e0e150ab746212e5f5b7e7通过独立零件归属、平整顶面、单实体、三处原开孔封闭、中央薄顶及相关硬件零交叠检查；卸四角盖板螺丝后向上0.1/0.6/1.4/2/5/10mm的检查位置均无干涉。自动整机5对复杂实体未判定，补充检查仅覆盖盖板变更与拆卸路径；FPC完整尾部就位、风扇线束、温升及实际打印配合仍未验证。配套零件清单为盖板1件、PCB垫片2件，四角M2×4螺丝4枚和PCB固定M2×4螺丝2枚保留。


屏舱下方左后侧的四条进气槽已按用户要求去掉，左侧该区域恢复2.4mm连续实壁；左前侧四条风扇排气槽保留。当前模型f7a2881b16c8992e6aef26389e47548bad0c4b7db00c64a95b19a198af783eeb已目视核对左侧及背侧：原进气范围224.64mm³全部为壳体材料，四个排气窗口内壳体体积为0。补回的侧壁与所有已发布硬件及PCB物理实体的精确共享体积为0，壳体仍是单一有效实体。整机自动检查有32对因复杂度或耗时未判定，补充检查仅验证封孔区域，不声明整机所有干涉已通过。封闭后的外部补气路径、整机气流和温升仍未测量；不增设替代进气孔。

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.

The rear-loading locator pocket is supplemented by the retained rear frame as described above. Proposed later assembly is screen into removed pod from rear, fit low-stress support/retainer, connect tail with full latch access, then attach pod. Do not suspend LCD by FPC, stick adhesive on polarizer or bend at glass edge. Enlarged interior deck opening and thin front regions require strength checks. Failed printed-screw-kit candidates committed no geometry; retain their failure record rather than substituting hand-modeled screw joints.


### Current prototype update
The preceding making notes are retained historical records: the statements about no rear retainer/fasteners and entry-only FPC describe the previous revision and are superseded by this query's geometry above. There has still been no physical print or assembly test.
Default PLA is a CAD prototype assumption; calibrate M2 holes and verify local thin-wall strength. Print screw axes upright where possible; sloping housing and mounting receivers may need supports. Soft pads are die-cut, not FDM parts. Assemble glass/pads/frame on the removed inverted pod, alternate the four screws only to their hard stops, shape the tail once with a radius guide, insert its stiffener and close the latch before pod installation. Remove Pi for tool access if necessary. Verify pad chemistry/compression and display image uniformity before powered integration. The future supported connector board is not part of this delivery.

Front module making update: print the blank separately with the tongue facing upward if possible, calibrate its 0.3mm lateral seat clearance and the four kit M2 holes, then verify screw head access and repeated removal before user-facing use. Turn all power off and isolate the battery before releasing the four screws and unplugging a future module harness. There is no printed or tested electrical harness in this CAD handoff.

Current PCB review addendum: historical making instructions above do not validate the new horizontal tail route. Do not treat the current assembly as fitted until the height and contact-direction conflict is resolved.


### Raised board assembly update

The prior no-fastener/17.5mm/socket-height-conflict notes above are historical. Current PCB is mounted to the upper-shell beams and rear guide atZ21.8 with higher ESQ and lower HLE. Fit the board and start both M2x4 screws loosely before tightening to contact; the removable module blank is not its support. Keep screw-tip holes clear. Assemble the screen pod off the case for latch access. Do not force or repeatedly bend the tail; current bottom-contact installation remains unresolved, so do not treat this draft as a powered or fully fitted screen assembly. The1.555mm air gap is not a cooling-performance claim.

### Current top-contact assembly update

Earlier bottom-contact conflict and1.555mm overall-minimum statements are historical. Current FH12A top-contact orientation and10terminal mapping are resolved. Current minimum ordinary-component air is1.505918mm after buffer/capacitor pockets. The board mounts to upper-shell beams; prototype the estimated native-tail seating with the screen pod removed and latch accessible. Preserve its straight stiffener, do not twist the exposed-copper face, and avoid repeated folds. Exact physical fit, thread life and temperatures remain untested.

### Cooling assembly update

Current cooling adds two real heatsinks, a real manufacturerfan model, an integralupper-shell cradle/duct and twoM2x4 kit joints. Print shell and collar separately; the inward cradle and duct roof require supports and careful cleanup. Pads and TIM are die-cut stock. Assemble fan with inlet up and outlet rearward, start bothcollar screws loosely, tighten alternately to the matched standoffs, check blade freedom, thenfactory-prewire/strain-relieve leads and installPCB. Usercold-plugsPi with prebondedCPU/RAM sinks and performs no soldering. Do not allow case loads on the chips or let wires cross the inlet. Inspect actualfan thickness and rebuildhard-stop height before printing if it differs from4.5mm. Detailed assembly/thermaltest procedure is in the cooling assembly document. No physicalprint, temperature test or plug qualification has been performed.


### 当前Pi4被动散热片与HAT风扇更新

上面的Fischer双片、后向风扇出口和高风罩是历史装配记录，以本次顶部说明和当前装配指南为准。打印上壳和1.4mm压框分开；下托耳/内伸支架需要试排方向和局部支撑，勿在电气焊盘接触处残留支撑。四角沉头只在打印件，不能锥削Pi孔。确认P165-B实际底面与贴片落差、金属螺纹深度后再四角交替轻紧，不允许强压芯片或弯PCB。先装前部风扇、按实测厚度调整软垫/限位，检查转动，再装Pi/HAT。HAT底面J_FAN插预装工厂两针线并松弛固定；用户无需焊接。风扇入口向上、出口前向，线束按2mm弯曲半径放在前沿上方，不遮入口。屏舱拆下接FPC，折回露铜向上，不强拉估计长度的原生排线。所有历史“尚无风扇插头”或“按钮干涉未处理”的陈述被本次模型取代；仍无实际打印、插接、温升测试。


### 新版PCB同步装配更新

当前接口是C5373447上接触抽拉座，均匀拉推锁扣两端，不能掀开。元件最小空气间隙1.555001mm、保守锁扣空间2.7mm。先试配局部薄顶和M2接收端；卸下屏舱，在软垫上支撑玻璃，实测尾部长度、补强位置和接口止挡，再按Sharp允许区弯折、铜面朝上插入。不要以拉伸、扭转或反复折弯补偿。完整尾部插接尚未验证。J_FAN在正面后部，旧底面短线束记录属于历史，不能直接沿用。没有实际打印、插接或热测试。


### 底盖固定与侧孔试装更新
此前“底盖无固定件”的段落是历史记录。当前底盖单独平放打印，定位边向上；上壳托耳与内伸结构需要在切片器中检查方向和局部支撑。采用PLA样机默认，先校准M2打印接收孔；沉头座勿残留支撑。四枚M2×6从底部插入，对角逐步轻紧到贴合，不以拧紧消除翘曲。断电后卸下四枚底盖螺丝，再沿-Z平移底盖，浅定位边没有卡扣，Pi和HAT仍由上壳承载。试插实际USB-C、micro-HDMI、3.5mm插头，确认插头肩部能靠近接口、能完全就位和拔出，再决定是否微调开孔参数。没有实际打印、拉拔或插拔试验；无需热熔铜螺母。

### 无侧面按钮装配更新
当前上壳取消侧面按钮和按钮帽；此处是上壳连续全厚侧壁，不安装开关或封孔塞，不再打印power_cap。上文橙色按钮、按钮开孔和按钮干涉的内容是历史装配记录，当前橙色外观只保留屏舱。使用系统软件正常关机后再断开Pi原生USB-C电源；没有新增按钮功能。其他底盖、屏幕、风扇装配说明保留，仍需实物试装。




### 独立平面盖板装配更新
打印或制作盖板时将背面定位舌、母座盲凹腔与其他让位凹腔一起检查；外表面保持平整，中央不是按钮或封孔塞。中央薄顶约0.645mm，仅可按样机默认评估，先核对切片层数、残留支撑、翘曲及实际母座间隙；不得用拧紧螺丝消除对母座的挤压。PCB底面的两枚1.2mm垫片按既有方法安装。更换拓展件时先软件关机、断开全部供电，只卸四角盖板螺丝，沿+Z提起整块盖板；PCB、底盖和屏舱保持固定。自制件沿用70×37外形、定位舌和四角接口，器件载荷须由模块自身承受。无实物打印、反复拆装或承载测试。

### 左后侧进气槽取消

打印上壳时该区域为完整2.4mm壁，不再清理或后加工原四条进气槽。保留左前侧排气槽，装配后确认内部吸气净空与排气窗通畅。封闭后的进气路径及温升必须在样机上测量，未作冷却性能结论。
