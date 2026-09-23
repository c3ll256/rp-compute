// ATtiny1616-SN: Microchip DS40002204A pp15,18,505-506.
// 5 MHz internal clock; keep PA0 as UPDI. Firmware is required before operation.
// Interlock pin maps and reset timing: product/power-interface-design.md.
const wirePair = "kicad:Connector_Wire/SolderWire-0.1sqmm_1x02_P3.6mm_D0.4mm_OD1mm";
const odPins = { pin1: "NC", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" };
const crossings = [
  { ref: "U_HOST_TX", a: "MCU_TX", y: "PI_RX", supply: "V3V3_AON", pull: "V3V3_PI", x: 0, yPos: 25 },
  { ref: "U_HOST_RX", a: "PI_TX", y: "MCU_RX", supply: "V3V3_PI", pull: "V3V3_AON", x: 8, yPos: 25 },
  { ref: "U_HOST_REQ", a: "MCU_REQ_N", y: "PI_REQ_N", supply: "V3V3_AON", pull: "V3V3_PI", x: 0, yPos: 34 },
  { ref: "U_HOST_ACK", a: "PI_ACK_N", y: "MCU_ACK_N", supply: "V3V3_PI", pull: "V3V3_AON", x: 8, yPos: 34 },
  { ref: "U_CHG_PERMIT", a: "MCU_CHG_DISABLE", y: "CHG_CE_N", supply: "V3V3_AON", pull: null, x: 0, yPos: 43 },
  { ref: "U_RUN_PERMIT", a: "MCU_RUN_OK", y: "ILK_RESET_N", supply: "V3V3_AON", pull: null, x: 8, yPos: 43 },
];

export const Controller = () => (
  <>
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_MCU" manufacturerPartNumber="ATTINY1616-SN"
      footprint="kicad:Package_SO/SOIC-20W_7.5x12.8mm_P1.27mm" supplierPartNumbers={{ jlcpcb: ["C614136"] }}
      pinLabels={{ pin1: "VDD", pin2: "PA4", pin3: "PA5", pin4: "PA6", pin5: "PA7",
        pin6: "PB5", pin7: "PB4", pin8: "PB3", pin9: "PB2", pin10: "PB1",
        pin11: "PB0", pin12: "PC0", pin13: "PC1", pin14: "PC2", pin15: "PC3",
        pin16: "UPDI", pin17: "PA1", pin18: "PA2", pin19: "PA3", pin20: "GND" }}
      connections={{ VDD: "net.V3V3_AON", GND: "net.GND", PA4: "net.BAT_ADC",
        PA5: "net.MCU_COM", PA6: "net.SYS_ADC", PA7: "net.NTC_ADC",
        PB5: "net.MCU_RUN_OK", PB4: "net.MCU_ARM", PB3: "net.MCU_RX", PB2: "net.MCU_TX",
        PB1: "net.CHG_SDA", PB0: "net.CHG_SCL", PC0: "net.MCU_DISP",
        PC1: "net.MCU_CHG_DISABLE", PC2: "net.POWER_KEY_N", PC3: "net.BOOST_EN",
        UPDI: "net.UPDI", PA1: "net.MCU_REQ_N", PA2: "net.MCU_ACK_N", PA3: "net.ILK_RESET_N" }}
      schSectionName="Supervisor" layer="bottom" pcbX={-25} pcbY={22} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_MCU" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.GND" }}
      schSectionName="Supervisor" layer="bottom" pcbX={-20.5} pcbY={30} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_MCU_BULK" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.GND" }}
      schSectionName="Supervisor" layer="bottom" pcbX={-31} pcbY={31} />
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="J_UPDI" footprint="kicad:Connector_PinHeader_2.54mm/PinHeader_1x03_P2.54mm_Vertical"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.UPDI", pin3: "net.GND" }}
      schSectionName="Supervisor" layer="bottom" pcbX={-13} pcbY={46} pcbRotation={90} />

    {/* Receiving-domain pullups prevent a powered sender feeding an unpowered Pi. */}
    {crossings.map((c) => <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={c.ref} name={c.ref}
      manufacturerPartNumber="SN74LVC1G07DBVR" footprint="kicad:Package_TO_SOT_SMD/SOT-23-5"
      supplierPartNumbers={{ jlcpcb: ["C7829"] }} pinLabels={odPins}
      connections={{ A: `net.${c.a}`, Y: `net.${c.y}`, VCC: `net.${c.supply}`, GND: "net.GND" }}
      schSectionName="Host and permits" layer="bottom" pcbX={c.x} pcbY={c.yPos} />)}
    {crossings.map((c, i) => <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`bypass-${c.ref}`} name={`C_CTRL${i + 1}`}
      capacitance="100nF" footprint="0603" connections={{ pin1: `net.${c.supply}`, pin2: "net.GND" }}
      schSectionName="Host and permits" layer="bottom" pcbX={c.x - 3} pcbY={c.yPos + 3} />)}
    {crossings.filter((c) => c.pull).map((c, i) => <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`pull-${c.ref}`} name={`R_HOST${i + 1}`}
      resistance="4.7k" footprint="0603" connections={{ pin1: `net.${c.pull}`, pin2: `net.${c.y}` }}
      schSectionName="Host and permits" layer="bottom" pcbX={c.x + 1} pcbY={c.yPos + 4} />)}
    {[
      ["R_RUN_OFF", "MCU_RUN_OK", "GND", -30, 35],
      ["R_ARM_OFF", "MCU_ARM", "GND", -24, 35],
      ["R_CHG_OFF", "MCU_CHG_DISABLE", "V3V3_AON", -18, 35],
      ["R_REQ_IDLE", "MCU_REQ_N", "V3V3_AON", -30, 38],
      ["R_ACK_IDLE", "PI_ACK_N", "V3V3_PI", -24, 38],
      ["R_COM_OFF", "MCU_COM", "GND", -18, 38],
    ].map(([ref, a, b, x, y]) => <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={String(ref)} name={String(ref)} resistance="100k" footprint="0603"
      connections={{ pin1: `net.${a}`, pin2: `net.${b}` }}
      schSectionName="Supervisor" layer="bottom" pcbX={Number(x)} pcbY={Number(y)} />)}

    {/* Fail-open lid circuit: factory harness COM=AON, NO=LID_CLOSED; NC unused. */}
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="J_LID" footprint={wirePair}
      connections={{ pin1: "net.V3V3_AON", pin2: "net.LID_CLOSED" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-29} pcbY={46} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_LID_OFF" resistance="1k" footprint="0603"
      connections={{ pin1: "net.LID_CLOSED", pin2: "net.GND" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-22} pcbY={46} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_POR" manufacturerPartNumber="TPS3808G33DBVR" footprint="kicad:Package_TO_SOT_SMD/SOT-23-6"
      supplierPartNumbers={{ jlcpcb: ["C43698"] }}
      pinLabels={{ pin1: "RESET_N", pin2: "GND", pin3: "MR_N", pin4: "CT", pin5: "SENSE", pin6: "VDD" }}
      connections={{ RESET_N: "net.ILK_RESET_N", GND: "net.GND", MR_N: "net.LID_CLOSED",
        SENSE: "net.V3V3_AON", VDD: "net.V3V3_AON" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-26} pcbY={38} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_SCHMITT" manufacturerPartNumber="SN74LVC2G17DCKR" footprint="kicad:Package_TO_SOT_SMD/SOT-363_SC-70-6"
      supplierPartNumbers={{ jlcpcb: ["C50714"] }}
      pinLabels={{ pin1: "A1", pin2: "GND", pin3: "A2", pin4: "Y2", pin5: "VCC", pin6: "Y1" }}
      connections={{ A1: "net.ILK_RESET_N", GND: "net.GND", A2: "net.MCU_ARM",
        Y2: "net.ARM_CLK", VCC: "net.V3V3_AON", Y1: "net.LATCH_CLR_N" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-26} pcbY={29} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_LATCH" manufacturerPartNumber="SN74LVC1G74DCUR" footprint="kicad:Package_SO/VSSOP-8_2.3x2mm_P0.5mm"
      supplierPartNumbers={{ jlcpcb: ["C70285"] }}
      pinLabels={{ pin1: "CLK", pin2: "D", pin3: "Q_N", pin4: "GND", pin5: "Q", pin6: "CLR_N", pin7: "PRE_N", pin8: "VCC" }}
      connections={{ CLK: "net.ARM_CLK", D: "net.V3V3_AON", GND: "net.GND", Q: "net.MAIN_EN",
        CLR_N: "net.LATCH_CLR_N", PRE_N: "net.V3V3_AON", VCC: "net.V3V3_AON" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-26} pcbY={20} />
    {[20, 29, 38].map((y, i) => <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`ilk-cap-${i}`} name={`C_ILK${i + 1}`} capacitance="100nF"
      footprint="0603" connections={{ pin1: "net.V3V3_AON", pin2: "net.GND" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-31} pcbY={y} />)}
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_RESET_PU" resistance="10k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.ILK_RESET_N" }}
      schSectionName="Hardware interlock" layer="top" pcbX={-21} pcbY={38} />

    {/* Factory-wired B3F power key, independent of replaceable front modules. */}
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="J_KEY" footprint={wirePair}
      connections={{ pin1: "net.POWER_KEY_N", pin2: "net.GND" }}
      schSectionName="Supervisor" layer="bottom" pcbX={23} pcbY={46} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_KEY_PU" resistance="10k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.POWER_KEY_N" }}
      schSectionName="Supervisor" layer="bottom" pcbX={21} pcbY={41} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_KEY" capacitance="10nF" footprint="0603"
      connections={{ pin1: "net.POWER_KEY_N", pin2: "net.GND" }}
      schSectionName="Supervisor" layer="bottom" pcbX={26} pcbY={41} />

    {/* ADC source impedance is 50k: 100nF reservoirs require settling in firmware. */}
    {[{ name: "BAT", rail: "BAT_RAW", y: 12 }, { name: "SYS", rail: "SYS_RAW", y: 6 }].flatMap((s) => [
      <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`adc-top-${s.name}`} name={`R_${s.name}_TOP`} resistance="100k" footprint="0603"
        connections={{ pin1: `net.${s.rail}`, pin2: `net.${s.name}_ADC` }}
        schSectionName="Battery sensing" layer="bottom" pcbX={-30} pcbY={s.y} />,
      <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`adc-bot-${s.name}`} name={`R_${s.name}_BOT`} resistance="100k" footprint="0603"
        connections={{ pin1: `net.${s.name}_ADC`, pin2: "net.GND" }}
        schSectionName="Battery sensing" layer="bottom" pcbX={-25} pcbY={s.y} />,
      <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} key={`adc-cap-${s.name}`} name={`C_${s.name}_ADC`} capacitance="100nF" footprint="0603"
        connections={{ pin1: `net.${s.name}_ADC`, pin2: "net.GND" }}
        schSectionName="Battery sensing" layer="bottom" pcbX={-20} pcbY={s.y} />
    ])}
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="J_MCU_NTC" footprint={wirePair}
      connections={{ pin1: "net.NTC_ADC", pin2: "net.GND" }}
      schSectionName="Battery sensing" layer="bottom" pcbX={-28} pcbY={0} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_NTC_PU" resistance="10k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.NTC_ADC" }}
      schSectionName="Battery sensing" layer="bottom" pcbX={-21} pcbY={0} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_NTC" capacitance="10nF" footprint="0603"
      connections={{ pin1: "net.NTC_ADC", pin2: "net.GND" }}
      schSectionName="Battery sensing" layer="bottom" pcbX={-21} pcbY={-3} />
  </>
);
