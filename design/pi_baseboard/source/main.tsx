import { board, interfaces } from "./layout";
import {
  boardPropsFromRules,
  groundPourPropsFromRules,
  keepoutPropsFromRules,
  netPropsFor,
  pcbRules,
} from "./lib/replicator-pcb";

// Interface placement study only. V5_PI, V5_LCD, and AUX_3V3 have no source in
// this draft, and the LCD control pins are intentionally unconnected. Do not
// release or energize this partial circuit as a functional baseboard.

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
    <connector
      name="J_PI"
      manufacturerPartNumber="SSQ-120-02-G-D"
      footprint="jlcpcb:C7370433"
      supplierPartNumbers={{ jlcpcb: ["C7370433"] }}
      pinLabels={piPins}
      layer={interfaces.piDock.side}
      pcbX={interfaces.piDock.x}
      pcbY={interfaces.piDock.y}
      pcbRotation={interfaces.piDock.rotation}
    />
    <connector
      name="J_LCD"
      manufacturerPartNumber="FH12-10S-0.5SH(55)"
      footprint="jlcpcb:C506791"
      supplierPartNumbers={{ jlcpcb: ["C506791"] }}
      pinLabels={lcdPins}
      layer={interfaces.displayFpc.side}
      pcbX={interfaces.displayFpc.x}
      pcbY={interfaces.displayFpc.y}
      pcbRotation={interfaces.displayFpc.rotation}
    />
    <connector
      name="J_MOD"
      manufacturerPartNumber="BM16B-GHDS-TF(LF)(SN)"
      footprint="jlcpcb:C594409"
      supplierPartNumbers={{ jlcpcb: ["C594409"] }}
      pinLabels={modulePins}
      layer={interfaces.frontModule.side}
      pcbX={interfaces.frontModule.x}
      pcbY={interfaces.frontModule.y}
      pcbRotation={interfaces.frontModule.rotation}
    />
    {[6, 9, 14, 20, 25, 30, 34, 39].map((pin) => (
      <trace key={`pi-gnd-${pin}`} from={`.J_PI > .pin${pin}`} to="net.GND" />
    ))}
    {[1, 16].map((pin) => (
      <trace key={`mod-gnd-${pin}`} from={`.J_MOD > .pin${pin}`} to="net.GND" />
    ))}
    {[9, 10].map((pin) => (
      <trace key={`lcd-gnd-${pin}`} from={`.J_LCD > .pin${pin}`} to="net.GND" />
    ))}
    {[2, 4].map((pin) => (
      <trace key={`pi-power-${pin}`} from={`.J_PI > .pin${pin}`} to="net.V5_PI" />
    ))}
    {[1, 17].map((pin) => (
      <trace key={`pi-3v3-${pin}`} from={`.J_PI > .pin${pin}`} to="net.V3V3_PI" />
    ))}
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
