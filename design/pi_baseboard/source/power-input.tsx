// USB-C input is a sink only. TI TUSB320LAI GPIO mode reports the advertised
// current. Its two open-drain outputs both go low only for a 3 A source
// (datasheet ZHCSEB3D p12). The OR gate makes the TPS259531 active-low EN
// low only in that state. This intentionally rejects default/1.5 A adapters
// until a separately proven lower-current startup path is designed.
export const PowerInput = () => (
  <>
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="J_USB_IN" manufacturerPartNumber="USB4105-GF-A"
      footprint="kicad:Connector_USB/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"
      connections={{
        A1: "net.GND", A12: "net.GND", B1: "net.GND", B12: "net.GND",
        SH: "net.GND", A4: "net.USB_VBUS", A9: "net.USB_VBUS",
        B4: "net.USB_VBUS", B9: "net.USB_VBUS",
        A5: "net.USB_CC1", B5: "net.USB_CC2",
      }}
      layer="top" pcbX={-30} pcbY={-42} pcbRotation={90} />
    {/* USB data and SBU contacts are deliberately unconnected: charging only. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="U_CC" manufacturerPartNumber="TUSB320LAIRWBR"
      footprint="jlcpcb:C132554" supplierPartNumbers={{ jlcpcb: ["C132554"] }}
      pinLabels={{ pin1: "CC1", pin2: "CC2", pin3: "PORT", pin4: "VBUS_DET",
        pin5: "ADDR", pin6: "OUT3", pin7: "OUT1", pin8: "OUT2",
        pin9: "ID", pin10: "GND", pin11: "EN_N", pin12: "VDD" }}
      connections={{ CC1: "net.USB_CC1", CC2: "net.USB_CC2", PORT: "net.GND",
        VBUS_DET: "net.USB_VBUS_SENSE", OUT1: "net.USB_OUT1",
        OUT2: "net.USB_OUT2", GND: "net.GND", EN_N: "net.GND",
        VDD: "net.USB_VBUS" }}
      layer="top" pcbX={-18} pcbY={-43} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="R_USB_VDET" resistance="900k" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.USB_VBUS_SENSE" }}
      layer="top" pcbX={-22} pcbY={-37} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="R_CC_OUT1" resistance="10k" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.USB_OUT1" }}
      layer="top" pcbX={-15} pcbY={-37} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="R_CC_OUT2" resistance="10k" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.USB_OUT2" }}
      layer="top" pcbX={-12} pcbY={-37} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="C_CC_VDD" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.GND" }}
      layer="top" pcbX={-18} pcbY={-48} />
    {/* DBV pin map: A=1, B=2, GND=3, Y=4, VCC=5 (TI SCLS317 p3). */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="U_CC_OR" manufacturerPartNumber="SN74AHC1G32DBVR"
      footprint="jlcpcb:C7470" supplierPartNumbers={{ jlcpcb: ["C7470"] }}
      pinLabels={{ pin1: "A", pin2: "B", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      connections={{ A: "net.USB_OUT1", B: "net.USB_OUT2", GND: "net.GND",
        Y: "net.USB_INPUT_DISABLE", VCC: "net.USB_VBUS" }}
      layer="top" pcbX={-8} pcbY={-43} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="C_CC_OR" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.GND" }}
      layer="top" pcbX={-7} pcbY={-48} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="R_USB_DISABLE" resistance="47k" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.USB_INPUT_DISABLE" }}
      layer="top" pcbX={-3} pcbY={-43} />
    {/* TPS259531 is the active-low EN/OVLO variant. TI TPS2595 p4, p7, p21:
        ~2.48 A nominal with 820 ohm ILM, datasheet ratios imply ~2.63 A
        at the specified high corner before resistor tolerance. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="U_USB_EFUSE" manufacturerPartNumber="TPS259531DSGR"
      footprint="jlcpcb:C2155674" supplierPartNumbers={{ jlcpcb: ["C2155674"] }}
      pinLabels={{ pin1: "DVDT", pin2: "EN_OVLO", pin3: "IN1", pin4: "IN2",
        pin5: "OUT", pin6: "FLT", pin7: "ILM", pin8: "GND" }}
      connections={{ EN_OVLO: "net.USB_INPUT_DISABLE", IN1: "net.USB_VBUS",
        IN2: "net.USB_VBUS", OUT: "net.CHG_VBUS", GND: "net.GND",
        ILM: "net.USB_ILM", DVDT: "net.USB_DVDT" }}
      layer="top" pcbX={2} pcbY={-43} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="R_USB_ILM" resistance="820" footprint="0603"
      connections={{ pin1: "net.USB_ILM", pin2: "net.GND" }}
      layer="top" pcbX={10} pcbY={-44} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="C_USB_DVDT" capacitance="4.7nF" footprint="0603"
      connections={{ pin1: "net.USB_DVDT", pin2: "net.GND" }}
      layer="top" pcbX={9} pcbY={-38} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="USB input" name="C_USB_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.USB_VBUS", pin2: "net.GND" }}
      layer="top" pcbX={-1} pcbY={-48} />
  </>
);
