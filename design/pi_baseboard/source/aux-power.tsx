// TI TPS2553 SLVS841F pp5,6,15,25. TPS2553 is active-high, current-limiting.
// RILIM=169k 1% gives ~136..187mA corners; normal module budget is 100mA.
// Module power originates at V5_MAIN; Pi3V3 is enable/sense only, never fed back.
export const AuxPower = () => (
  <>
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_AUX_LIMIT" manufacturerPartNumber="TPS2553DBVR"
      footprint="kicad:Package_TO_SOT_SMD/SOT-23-6"
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "FAULT_N", pin5: "ILIM", pin6: "OUT" }}
      connections={{ IN: "net.V5_MAIN", GND: "net.GND", EN: "net.V3V3_PI",
        FAULT_N: "net.AUX_FAULT_N", ILIM: "net.AUX_ILIM", OUT: "net.V5_AUX" }}
      schSectionName="Module power" layer="top" pcbX={-24} pcbY={-18} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_AUX_ILIM" resistance="169k" footprint="0603"
      connections={{ pin1: "net.AUX_ILIM", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-20} pcbY={-18} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_AUX_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_MAIN", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-29} pcbY={-18} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_AUX_EN_OFF" resistance="100k" footprint="0603"
      connections={{ pin1: "net.V3V3_PI", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-24} pcbY={-22} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_AUX_FAULT_PU" resistance="10k" footprint="0603"
      connections={{ pin1: "net.V3V3_PI", pin2: "net.AUX_FAULT_N" }}
      schSectionName="Module power" layer="top" pcbX={-19} pcbY={-22} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="U_AUX_LDO" manufacturerPartNumber="TLV75533PDBVR"
      footprint="jlcpcb:C404027" supplierPartNumbers={{ jlcpcb: ["C404027"] }}
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "NC", pin5: "OUT" }}
      connections={{ IN: "net.V5_AUX", GND: "net.GND", EN: "net.V5_AUX", OUT: "net.AUX_3V3" }}
      schSectionName="Module power" layer="top" pcbX={-24} pcbY={-27} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_AUX_LDO_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_AUX", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-24} pcbY={-31} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="C_AUX_LDO_OUT" capacitance="4.7uF" footprint="0805"
      connections={{ pin1: "net.AUX_3V3", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-19} pcbY={-27} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} name="R_AUX_BLEED" resistance="10k" footprint="0603"
      connections={{ pin1: "net.AUX_3V3", pin2: "net.GND" }}
      schSectionName="Module power" layer="top" pcbX={-19} pcbY={-31} />
  </>
);
