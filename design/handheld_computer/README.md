# 侧面按钮取消与连续侧壁

保持85×115mm外形、27mm前面板、13°屏舱和1mm前沿。当前PCB发布8816a764c91d71af56bd3042eeca5a34a6f0ec2096f8967712fe44e23a199537，STEP SHA256为7be47336983ab285b75e6c7d2a93d2c29418654a82397f66cf8ef8e56ad6b53d；装入(-100,81,21.8)mm、零旋转。PCB40×83.5mm、0.8mm四层，正面31元件，背面仅J_PI。板子由上壳梁与后导向承载，两枚M2×4固定，模块盖不承载PCB。

前次PCB同步版本ec22671b23ade2b894c2bd11afd797e6d93edd25c97aab1550952768fc5b8ca5。上壳/模块盖增加12处内部让空，屏舱/后框增加U_BUF1让位、C5373447抽拉包络和尾部通道。主壁2.4mm；局部最薄顶1.255001mm，按样机默认1.2mm下限保留，强度未实测。

逐物理实体检查：普通正面元件最小空气间隙1.555001mm，U_BUF1为1.6mm；屏螺丝距板基材1.292813mm。新版PCB与所查壳体、真实Pi、屏框、固定螺丝、名义玻璃均无实体交叠；Pi与上壳零交叠。固定螺丝、沉头齐平和Pi螺丝头到底盖1.1mm检查通过。Workbench自动检查38个组件对未判定；补充检查剔除PCB可视化铜箔/焊盘/过孔，对真实物理实体做精确布尔运算，并未把未判定当作无干涉。

FPC为SHOU HAN C5373447（0.5-10P CTSJ-H2.0 119），10针0.5mm、上接触、入口-Y、抽拉锁扣，不能掀开。折回铜面朝上，座端子=11−屏端子。详细模型来自嘉立创EDA/EasyEDA官方库，内部配合未经厂家认证。以图纸开闭深度差预留1.5mm抽拉量，保守打开包络与所查壳体/名义玻璃最小间隙2.7mm。应卸下屏舱接插，必要时先拆Pi；合壳后手指可达性未验证。

原生尾部13.7±0.5mm仍为授权估计，非厂家保证公差。Sharp要求出口展开0.8–6mm内弯折、内R≥0.45mm、末端4mm补强保持直线、不超过三次往复。按库模型推定槽面和1.85mm插入深度，一组两圆弧候选的13.7/14.2mm尾部最后弯折超过6mm，故没有接受该完整范围方案。这不证明所有路径不可行；实物尾长、槽面与止挡决定最终路线。目前不宣称尾部完全就位，旧负形槽仅作历史让空。

散热保留P165-B照片参考、Nidec F16FB厂家模型和左侧排气，未做温升测试。J_FAN现在位于PCB正面后部，旧底面J_FAN的52.521mm线束路线不适用，本次未重验风扇线束。Pi原生USB-C供电、旧基板充电开口取消。Pi四角M2.5×6、前模块M2×4、屏后框M2×6、风扇框M2×4保持；打印接收端来自printed-screw-joint-v1，M2沉头采用库内ISO7046明确回退。

模型供视觉和样机空间复核，没有实际打印、插接或上电验证；底盖已增加下述固定结构。以下Making and assembly记录完整保留；旧接口、面别、路线和间隙以当前说明和屏幕装配指南为准。


当前CAD版本a3ad0bddefeec6ea79ecd0e5d1ac9aeb94276e7795fead3fa2530d885ad8b33a。针对用户“底面无法固定、侧面接口孔太大”的反馈，底盖新增四枚ISO7046 M2×6沉头螺丝，从底部向上固定到上壳一体托耳。轴线为(-32,-48)、(32,-48)、(-32,47)、(32,-35)mm，采用不对称布置避开Pi后部USB和板底空间。四处打印接收端由printed-screw-joint-v1生成，默认PLA，名义咬合3.6mm；M2沉头按已有明确回退采用ISO7046头/座，接收端和补偿杆仍来自套件。托耳底面Z2.4接触底盖、顶部Z9；与侧壁融合，上壳与底盖各为一个实体。底盖保留2.4mm主板厚，新增0.8mm高、1.2mm厚的浅定位边，与上壳内壁每侧0.3mm间隙，托耳位置留缺口；定位边只定位，螺丝负责固定。

USB-C孔由12×8缩至10.2×5.2mm，中心(Y,Z)=(-19.3,8.18)mm；双micro-HDMI孔由8.5×5.2缩至7.4×4.2mm，中心Y=-4.5/9、Z8.6mm；3.5mm接口孔由直径8.5缩至7.6mm，中心(Y,Z)=(23.5,9.6)mm。USB-C和耳机孔高度按已放置Pi模型修正。后部USB/RJ45和散热开孔保持；当前侧面按钮和按钮孔已取消。尺寸为样机默认，已进入参数及约束表；没有用孔变小代替实际插头肩部、插入深度与打印缩孔验证。

当前提交模型逐实体检查：上壳/底盖/四枚新增螺丝对Pi、风扇和真实基板物理实体均零实体交叠；新增螺丝对接收上壳与底盖也零交叠，底面齐平。壳/底盖零交叠，定位边避开原Pi螺丝。自动组件检查有41对因复杂度或时间未判定；本次补充检查覆盖变更结构与相关硬件，没有把未判定当作整机无干涉。原屏幕/FPC、散热和线束待验证项保持。

用户确认取消侧面电源按钮。当前模型已删除power_cap对象及其源部件，并直接从上壳源代码删除按钮负形孔和专用参数，恢复原位置2.4mm全厚连续侧壁。现有精简基板没有按钮电路，无新增GPIO接线，软件关机策略维持。需求、约束、当前零件清单与需求摘要同步；不采购或打印按钮帽/开关。原按钮位置10×10mm区域跨全壁厚的精确实体探针体积240mm³，封闭检查通过；重新核对上壳与Pi、真实基板物理实体、风扇及底盖四枚螺丝，均无新增实体交叠。底盖与现有接口尺寸保留。自动整机检查仍有复杂实体对未判定，补充检查覆盖本次变更相关配合；不据此宣称实物整机适配。

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
