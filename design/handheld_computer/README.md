# 紧凑Pi4终端：被动散热片与HAT供电风扇

用户要求热风不朝前吹：后部左侧进气、风扇朝左侧排气，前侧排气孔封闭。旧基板充电开口仍取消，活动精简版使用右侧Pi原生USB-C；HAT电路及Pi四角固定保留。

保留85×115mm紧凑外壳、13度屏舱和1mm前沿。当前带风扇插座HAT发布dbacb2cc60cdef69951f80af131442ea24b1ed03394f9e446a1f890bf9a1d209，精确STEP SHA256 fc63232fc7ddf1972848edb829711607d9a1d65cc299b42f3427e71f542c520a，装入CAD位置(-100,81,21.8)mm、零旋转。PCB40×83.5mm、0.8mm四层，32个实装元件；V5_PI_IN0.5mm走线，40枚0.6/0.3mm过孔。PCB0DRC错误、0未连接，34条生成库封装提示，三个发布区可用。不会因此宣称自动贴片订单已验证。

## 接口和固定

FPC为FH12A-10S-0.5SH(55)水平上接触座，入口-Y/向下，折回露铜朝上；物理端子对应为座=11−屏。高GPIO ESQ-120-12-G-D、低8pin HLE-104-02-G-DV保留。HAT由上壳两条梁、两枚内部M2×4螺丝和后导向承载，下盖和模块盖不承载HAT。Pi四角49×58mm位置以四枚M2.5×6沉头螺丝从打印下托耳穿过原PCB孔进入散热片金属螺纹，2.4mm名义啮合；无单独金属件上壳支架。四枚前模块M2×4、四枚屏后压框M2×6和两枚风扇压框M2×4均用沉头。沉头座只做在打印件，PCB不改孔。

## 散热与电源

按用户图片65×55×11mm Pi4被动片安排，匹配Geekworm P165-B单件SKU100237。散热片底部接触台阶、鳍片和端口缺口为明确的厂家照片参考，未获得厂家STEP或底部公差；不能作为加工金属件图纸或保证实物贴合。CPU/RAM暂用0.25mm TIM间隙参考，套装实际贴片厚度未知。高ESQ端部最小参考间隙0.345mm，需实测该缺口是否容纳母座。

Nidec F16FB-05LLC厂家STEP置于左侧壁附近(-29,-38,11.55)mm，安装旋转(180,0,270)度，入口向上、出口朝左(-X)；上壳一体托架和旋转后的19×29×1.4mm薄压框固定，不保留旧Fischer双散热片或跨板高风罩。J_FAN在HAT底面，JST原厂侧入SH2pin座；Pi GPIO-header5V/GND经HAT铜箔给风扇供电，40mA额定/100mA预算，默认随电源常转。工厂32AWG SH引线转接36AWG风扇线并测试，用户插线，无焊接。LCD COM GPIO12保留。

## 已完成的名义几何检查

CAD版本82ffbfe4e57949e3264e188079107e331e2ea36690ffda9ae6a7cb11e72667be与上述冻结PCB逐物理实体检查：新增散热片、风扇、压框和软垫对Pi、HAT及所查壳体无体积交叠；HAT与屏/壳的检查无交叠，Pi与上壳无交叠。Workbench全组件自动检查对大量导入实体有时间/数量限制，不能把它的未判定当作无干涉；补充精确检查剔除了PCB可视化铜箔/焊盘/过孔实体。

风扇按最大5mm厚预留Ø12×3mm清空进气柱；后部左侧进气/左侧排气孔总57.6/43.2mm²无遮挡；侧面出口到内壁名义3.1mm，排气保留区无阻挡，前侧原四个排气孔恢复完整壁厚。含端头52.521mm线束路径、1.4mm束径和2mm弯曲半径探针通过，J_FAN插头空间通过。散热片到上壳1.6mm；普通HAT正面最小1.505918mm；屏螺丝到板基材1.292813mm；FPC打开锁扣保守包络最小1.490322mm；8针座顶低于面板0.745001mm；Pi四角螺丝头到底盖1.1mm。按钮增加9mm活动颈部，保留10mm帽面，与壳体零交叠。

上述检查仅针对名义模型。P165底部/TIM/高母座兼容、4角真实螺纹深度、风扇装配公差和合壳温升未实测。FPC原生排线13.7±0.5mm仍为授权估计，不是测量结果。旧底盖固定方式未在这轮重新设计。CAD供视觉及样机空间复核，实物装配和热性能仍需验证。

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
