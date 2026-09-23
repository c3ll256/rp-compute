import { board, interfaces } from "./layout";
import { PowerInput } from "./power-input";
import { Charger } from "./charger";
import { PowerOutput } from "./power-output";
import { Controller } from "./controller";
import { AuxPower } from "./aux-power";
import {
  boardPropsFromRules,
  groundPourPropsFromRules,
  keepoutPropsFromRules,
  netPropsFor,
  pcbRules,
} from "./lib/replicator-pcb";

// Integrated electrical draft: MCU, charging permission and module supply added.
// Compile, routing, power transient and mechanical gates remain open; not for fabrication.

const PcbRuleElements = () => (
  <>
    {Object.keys(pcbRules.nets).map((netName) => (
      <net key={netName} name={netName} {...netPropsFor(netName)} />
    ))}
    {groundPourPropsFromRules().map((pour) => (
      <copperpour key={pour.name} {...pour} />
    ))}
    {keepoutPropsFromRules().map((keepout) => (
      <keepout {...keepout} />
    ))}
  </>
);

const piPins = Object.fromEntries(
  Array.from({ length: 40 }, (_, index) => [`pin${index + 1}`, [`P${index + 1}`]]),
);
const lcdPins = Object.fromEntries(
  ["SCLK", "SI", "SCS", "EXTCOMIN", "DISP", "VDDA", "VDD", "EXTMODE", "VSS", "VSSA"].map(
    (name, index) => [`pin${index + 1}`, [name]],
  ),
);
const modulePins = Object.fromEntries(
  Array.from({ length: 16 }, (_, index) => [`pin${index + 1}`, [`M${index + 1}`]]),
);

// TI SN74AHC125 (PW), datasheet SCLS256 / supplier C54529 pp3, 5-7.
const ahc125Pins = {
  pin1: "OE1_N", pin2: "A1", pin3: "Y1", pin4: "OE2_N",
  pin5: "A2", pin6: "Y2", pin7: "GND", pin8: "Y3",
  pin9: "A3", pin10: "OE3_N", pin11: "Y4", pin12: "A4",
  pin13: "OE4_N", pin14: "VCC",
};

// Pin numbers below are Pi physical header numbers, verified against the official Pi 4B pinout.
const moduleSignalPins: Array<[number, number, string]> = [
  [3, 3, "GPIO2"], [4, 5, "GPIO3"], [5, 19, "GPIO10"],
  [6, 21, "GPIO9"], [7, 23, "GPIO11"], [8, 26, "GPIO7"],
  [9, 29, "GPIO5"], [10, 31, "GPIO6"], [11, 33, "GPIO13"],
  [12, 36, "GPIO16"], [13, 35, "GPIO19"], [14, 38, "GPIO20"],
  [15, 40, "GPIO21"],
];

export default () => (
  <board
    width={board.width}
    height={board.height}
    center_x={0}
    center_y={0}
    {...boardPropsFromRules()}
  >
    <PcbRuleElements />
    <silkscreentext text="GPIO 3V3 / 100mA" fontSize="1mm" pcbX={0} pcbY={-27} layer="top" />
    <silkscreentext text="UPDI" fontSize="1mm" pcbX={-10} pcbY={49} layer="bottom" />
    <silkscreentext text="LID" fontSize="1mm" pcbX={-29} pcbY={49} layer="top" />
    <silkscreentext text="KEY" fontSize="1mm" pcbX={25} pcbY={49} layer="bottom" />
    <silkscreentext text="FAN" fontSize="1mm" pcbX={27} pcbY={-14} layer="top" />
    <PowerInput />
    <Charger />
    <PowerOutput />
    <Controller />
    <AuxPower />
    {["Supervisor", "Host and permits", "Hardware interlock", "Battery sensing", "Module power", "USB input", "Charger", "Power outputs", "Display and interfaces"].map((name) =>
      <schematicsection key={name} name={name} />)}
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="J_PI"
      manufacturerPartNumber="SSQ-120-02-G-D"
      footprint="jlcpcb:C7370433"
      supplierPartNumbers={{ jlcpcb: ["C7370433"] }}
      pinLabels={piPins}
      connections={Object.fromEntries([6, 9, 14, 20, 25, 30, 34, 39].map((pin) => [`P${pin}`, "net.GND"]))}
      layer={interfaces.piDock.side}
      pcbX={interfaces.piDock.x}
      pcbY={interfaces.piDock.y}
      pcbRotation={interfaces.piDock.rotation}
    />
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="J_LCD"
      manufacturerPartNumber="FH12-10S-0.5SH(55)"
      footprint="jlcpcb:C506791"
      supplierPartNumbers={{ jlcpcb: ["C506791"] }}
      pinLabels={lcdPins}
      connections={{
        SCLK: "net.LCD_SCLK", SI: "net.LCD_SI", SCS: "net.LCD_SCS",
        EXTCOMIN: "net.LCD_COM", DISP: "net.LCD_DISP",
        VSS: "net.GND", VSSA: "net.GND",
      }}
      layer={interfaces.displayFpc.side}
      pcbX={interfaces.displayFpc.x}
      pcbY={interfaces.displayFpc.y}
      pcbRotation={interfaces.displayFpc.rotation}
    />
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="J_MOD"
      manufacturerPartNumber="BM16B-GHDS-TF(LF)(SN)"
      footprint="jlcpcb:C594409"
      supplierPartNumbers={{ jlcpcb: ["C594409"] }}
      pinLabels={modulePins}
      connections={{ M1: "net.GND", M16: "net.GND" }}
      layer={interfaces.frontModule.side}
      pcbX={interfaces.frontModule.x}
      pcbY={interfaces.frontModule.y}
      pcbRotation={interfaces.frontModule.rotation}
    />
    {/* LCD logic rail is derived from the independently switched LCD 5 V rail.
        TI TLV75533 DBV: IN=1, GND=2, EN=3, NC=4, OUT=5. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="U_LCD_LDO" manufacturerPartNumber="TLV75533PDBVR"
      footprint="jlcpcb:C404027" supplierPartNumbers={{ jlcpcb: ["C404027"] }}
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "NC", pin5: "OUT" }}
      connections={{ IN: "net.V5_LCD", GND: "net.GND", EN: "net.V5_LCD", OUT: "net.V3V3_LCD" }}
      layer="bottom" pcbX={-24} pcbY={-8}
    />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_LDO_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_LCD", pin2: "net.GND" }} layer="bottom" pcbX={-28} pcbY={-8} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_LDO_OUT" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V3V3_LCD", pin2: "net.GND" }} layer="bottom" pcbX={-20} pcbY={-8} />
    {/* Five independent LCD inputs. AHC inputs tolerate 5.5 V even with VCC=0;
        outputs are powered only from V3V3_LCD. Active-low OE is grounded for
        used channels. Unused channels are disabled at their own local rail. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="U_LCD_BUF1" manufacturerPartNumber="SN74AHC125PWR"
      footprint="jlcpcb:C54529" supplierPartNumbers={{ jlcpcb: ["C54529"] }}
      pinLabels={ahc125Pins} layer="bottom" pcbX={12} pcbY={-8}
      connections={{
        VCC: "net.V3V3_LCD", GND: "net.GND",
        OE1_N: "net.GND", A1: "net.GPIO11", Y1: "net.LCD_SCLK",
        OE2_N: "net.GND", A2: "net.GPIO10", Y2: "net.LCD_SI",
        OE3_N: "net.GND", A3: "net.GPIO8", Y3: "net.LCD_SCS",
        OE4_N: "net.GND", A4: "net.MCU_DISP", Y4: "net.LCD_DISP",
      }}
    />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces"
      name="U_LCD_BUF2" manufacturerPartNumber="SN74AHC125PWR"
      footprint="jlcpcb:C54529" supplierPartNumbers={{ jlcpcb: ["C54529"] }}
      pinLabels={ahc125Pins} layer="bottom" pcbX={0} pcbY={-8}
      connections={{
        VCC: "net.V3V3_LCD", GND: "net.GND",
        OE1_N: "net.GND", A1: "net.MCU_COM", Y1: "net.LCD_COM",
        OE2_N: "net.V3V3_LCD", A2: "net.GND",
        OE3_N: "net.V3V3_LCD", A3: "net.GND",
        OE4_N: "net.V3V3_LCD", A4: "net.GND",
      }}
    />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_BUF1" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V3V3_LCD", pin2: "net.GND" }} layer="bottom" pcbX={12} pcbY={-13} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_BUF2" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V3V3_LCD", pin2: "net.GND" }} layer="bottom" pcbX={0} pcbY={-13} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="R_LCD_CS_OFF" resistance="100k" footprint="0603"
      connections={{ pin1: "net.GPIO8", pin2: "net.GND" }} layer="bottom" pcbX={-8} pcbY={-15} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="R_LCD_DISP_OFF" resistance="100k" footprint="0603"
      connections={{ pin1: "net.MCU_DISP", pin2: "net.GND" }} layer="bottom" pcbX={-4} pcbY={-15} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_VDDA" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V5_LCD", pin2: "net.GND" }} layer="bottom" pcbX={8} pcbY={1} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_VDD" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_LCD", pin2: "net.GND" }} layer="bottom" pcbX={12} pcbY={1} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="C_LCD_DISP" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.LCD_DISP", pin2: "net.GND" }} layer="bottom" pcbX={16} pcbY={1} />
    {[2, 4].map((pin) => (
      <trace key={`pi-power-${pin}`} from={`.J_PI > .pin${pin}`} to="net.V5_PI" />
    ))}
    {[1, 17].map((pin) => (
      <trace key={`pi-3v3-${pin}`} from={`.J_PI > .pin${pin}`} to="net.V3V3_PI" />
    ))}
    <trace from=".J_PI > .pin24" to="net.GPIO8" />
    <trace from=".J_PI > .pin8" to="net.PI_TX" />
    <trace from=".J_PI > .pin10" to="net.PI_RX" />
    <trace from=".J_PI > .pin11" to="net.PI_REQ_N" />
    <trace from=".J_PI > .pin13" to="net.PI_ACK_N" />
    <trace from=".J_PI > .pin32" to="net.FAN_PWM" />
    <trace from=".J_PI > .pin22" to="net.AUX_FAULT_N" />
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Display and interfaces" name="J_FAN" footprint="kicad:Connector_PinHeader_2.54mm/PinHeader_1x03_P2.54mm_Vertical"
      connections={{ pin1: "net.V5_PI", pin2: "net.GND", pin3: "net.FAN_PWM" }}
      layer="top" pcbX={27} pcbY={-18} pcbRotation={90} />
    {[6, 7].map((pin) => (
      <trace key={`lcd-power-${pin}`} from={`.J_LCD > .pin${pin}`} to="net.V5_LCD" />
    ))}
    {/* Sharp LCY-1210401A p8: EXTMODE high selects external COM inversion. */}
    <trace from=".J_LCD > .pin8" to="net.V5_LCD" />
    {moduleSignalPins.flatMap(([modPin, piPin, netName]) => [
      <trace key={`pi-${netName}`} from={`.J_PI > .pin${piPin}`} to={`net.${netName}`} />,
      <trace key={`mod-${netName}`} from={`.J_MOD > .pin${modPin}`} to={`net.${netName}`} />,
    ])}
    <trace from=".J_MOD > .pin2" to="net.AUX_3V3" />
  </board>
);
