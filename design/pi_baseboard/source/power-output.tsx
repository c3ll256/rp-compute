// Provisional 5.1 V supply chain. TI TPS61088 ZHCSDP8D pp11,14-19 gives
// divider, current limit and compensation equations; the 5.1V/3.3A loop,
// capacitor DC-bias, battery-side 6A ceiling and thermals require bench proof.
const fusePins = {
  pin1: "EN", pin2: "OVLO", pin3: "AUXOFF", pin4: "FLT",
  pin5: "IN", pin6: "OUT", pin7: "DVDT", pin8: "GND",
  pin9: "ILM", pin10: "ITIMER",
};

export const PowerOutput = () => (
  <>
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="U_BOOST" manufacturerPartNumber="TPS61088RHLR"
      footprint="vendor:Texas_VQFN-RHL-20_RectangularEP" supplierPartNumbers={{ jlcpcb: ["C87357"] }}
      pinLabels={{ pin1: "VCC", pin2: "EN", pin3: "FSW", pin4: "SW4",
        pin5: "SW5", pin6: "SW6", pin7: "SW7", pin8: "BOOT",
        pin9: "VIN", pin10: "SS", pin11: "NC11", pin12: "NC12",
        pin13: "MODE", pin14: "OUT14", pin15: "OUT15", pin16: "OUT16",
        pin17: "FB", pin18: "COMP", pin19: "ILIM", pin20: "AGND",
        pin21: "PGND" }}
      connections={{ VCC: "net.BOOST_VCC", EN: "net.BOOST_EN",
        FSW: "net.BOOST_FSW", SW4: "net.BOOST_SW", SW5: "net.BOOST_SW",
        SW6: "net.BOOST_SW", SW7: "net.BOOST_SW", BOOT: "net.BOOST_BOOT",
        VIN: "net.SYS_RAW", SS: "net.BOOST_SS", NC11: "net.GND",
        NC12: "net.GND", OUT14: "net.V5_BOOST", OUT15: "net.V5_BOOST",
        OUT16: "net.V5_BOOST", FB: "net.BOOST_FB", COMP: "net.BOOST_COMP",
        ILIM: "net.BOOST_ILIM", AGND: "net.GND", PGND: "net.GND" }}
      layer="top" pcbX={14} pcbY={4} />
    <inductor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="L_BOOST" inductance="2.2uH" manufacturerPartNumber="74437349022"
      footprint="vendor:L_Wurth_WE-LHMI-7050" supplierPartNumbers={{ jlcpcb: ["C6101073"] }}
      connections={{ pin1: "net.SYS_RAW", pin2: "net.BOOST_SW" }}
      layer="top" pcbX={25} pcbY={4} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_IN" capacitance="22uF" footprint="1206"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.GND" }}
      layer="top" pcbX={10} pcbY={-3} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_VIN_HF" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.GND" }}
      layer="top" pcbX={8} pcbY={4} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_VCC" capacitance="2.2uF" footprint="0805"
      connections={{ pin1: "net.BOOST_VCC", pin2: "net.GND" }}
      layer="top" pcbX={9} pcbY={7} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_BOOT" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.BOOST_BOOT", pin2: "net.BOOST_SW" }}
      layer="top" pcbX={20} pcbY={-3} />
    {/* R_FSW ~=267k for 600kHz at VIN 3.5/VOUT5.1 per TI p11. */}
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_FSW" resistance="267k" footprint="0603"
      connections={{ pin1: "net.BOOST_FSW", pin2: "net.BOOST_SW" }}
      layer="top" pcbX={22} pcbY={10} />
    {/* R_ILIM 150k => 7.93A typical, ~6.63A minimum (TI p12). At VIN 3.5,
        VOUT5.1/3.3A, 85% efficiency, 2.2uH/600kHz: peak ~6.08A.
        Very small worst-case margin; actual efficiency and limits must be tested. */}
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_ILIM" resistance="150k" footprint="0603"
      connections={{ pin1: "net.BOOST_ILIM", pin2: "net.GND" }}
      layer="top" pcbX={4} pcbY={-2} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_SS" capacitance="47nF" footprint="0603"
      connections={{ pin1: "net.BOOST_SS", pin2: "net.GND" }}
      layer="top" pcbX={16} pcbY={-1} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_EN_OFF" resistance="100k" footprint="0603"
      connections={{ pin1: "net.BOOST_EN", pin2: "net.GND" }}
      layer="top" pcbX={4} pcbY={5} />
    {/* Feedback 56k lower / 182k upper gives 5.117V nominal. */}
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_FB_TOP" resistance="182k" footprint="0603"
      connections={{ pin1: "net.V5_BOOST", pin2: "net.BOOST_FB" }}
      layer="top" pcbX={21} pcbY={15} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_FB_BOT" resistance="56k" footprint="0603"
      connections={{ pin1: "net.BOOST_FB", pin2: "net.GND" }}
      layer="top" pcbX={17} pcbY={15} />
    {/* Candidate type-II loop for >=30uF effective COUT / 5kHz crossover;
        confirm ceramic bias, ESR and gain/phase margin on prototype. */}
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_BOOST_COMP" resistance="2.49k" footprint="0603"
      connections={{ pin1: "net.BOOST_COMP", pin2: "net.BOOST_COMP_RC" }}
      layer="top" pcbX={9} pcbY={15} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_COMP_Z" capacitance="10nF" footprint="0603"
      connections={{ pin1: "net.BOOST_COMP_RC", pin2: "net.GND" }}
      layer="top" pcbX={5} pcbY={15} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_COMP_P" capacitance="120pF" footprint="0603"
      connections={{ pin1: "net.BOOST_COMP", pin2: "net.GND" }}
      layer="top" pcbX={16} pcbY={20} />
    {[0, 1, 2].map((index) => (
      <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" key={index} name={`C_BOOST_OUT${index + 1}`} capacitance="22uF" footprint="1206"
        connections={{ pin1: "net.V5_BOOST", pin2: "net.GND" }}
        layer="top" pcbX={12 + index * 5} pcbY={-9} />
    ))}
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_BOOST_OUT_HF" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_BOOST", pin2: "net.GND" }}
      layer="top" pcbX={27} pcbY={-9} />
    {/* TPS22990 DML pin map TI ZHCSF87C p3; thermal pad belongs to VIN. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="U_MAIN_SW" manufacturerPartNumber="TPS22990DMLR"
      footprint="jlcpcb:C962990" supplierPartNumbers={{ jlcpcb: ["C962990"] }}
      pinLabels={{ pin1: "CT", pin2: "NC", pin3: "VIN", pin4: "VBIAS",
        pin5: "ON", pin6: "GND", pin7: "PG", pin8: "VOUT1",
        pin9: "VOUT2", pin10: "VOUT3", pin11: "PAD" }}
      connections={{ CT: "net.MAIN_CT", VIN: "net.V5_BOOST", VBIAS: "net.V5_BOOST",
        ON: "net.MAIN_EN", GND: "net.GND", PG: "net.GND",
        VOUT1: "net.V5_MAIN", VOUT2: "net.V5_MAIN", VOUT3: "net.V5_MAIN",
        PAD: "net.V5_BOOST" }}
      layer="top" pcbX={18} pcbY={26} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_MAIN_CT" capacitance="10nF" footprint="0603"
      connections={{ pin1: "net.MAIN_CT", pin2: "net.GND" }}
      layer="top" pcbX={24} pcbY={26} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_MAIN_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_BOOST", pin2: "net.GND" }}
      layer="top" pcbX={12} pcbY={26} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_MAIN_EN_OFF" resistance="100k" footprint="0603"
      connections={{ pin1: "net.MAIN_EN", pin2: "net.GND" }}
      layer="top" pcbX={18} pcbY={32} />
    {/* Two separately switched 5V domains: Pi may be back-powered at its own
        USB-C, while Sharp must never see >5.5V or the Pi-reversible rail. */}
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="U_PI_EFUSE" manufacturerPartNumber="TPS259470LRPWR"
      footprint="jlcpcb:C3662793" supplierPartNumbers={{ jlcpcb: ["C3662793"] }}
      pinLabels={fusePins}
      connections={{ EN: "net.V5_MAIN", OVLO: "net.PI_OVLO",
        IN: "net.V5_MAIN", OUT: "net.V5_PI", GND: "net.GND",
        ILM: "net.PI_ILM", DVDT: "net.PI_DVDT" }}
      layer="top" pcbX={6} pcbY={35} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="U_LCD_EFUSE" manufacturerPartNumber="TPS259470LRPWR"
      footprint="jlcpcb:C3662793" supplierPartNumbers={{ jlcpcb: ["C3662793"] }}
      pinLabels={fusePins}
      connections={{ EN: "net.V5_MAIN", OVLO: "net.LCD_OVLO",
        IN: "net.V5_MAIN", OUT: "net.V5_LCD", GND: "net.GND",
        ILM: "net.LCD_ILM", DVDT: "net.LCD_DVDT" }}
      layer="top" pcbX={6} pcbY={23} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_PI_OVLO_TOP" resistance="34.4k" footprint="0603"
      connections={{ pin1: "net.V5_MAIN", pin2: "net.PI_OVLO" }}
      layer="top" pcbX={1} pcbY={40} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_PI_OVLO_BOT" resistance="10k" footprint="0603"
      connections={{ pin1: "net.PI_OVLO", pin2: "net.GND" }}
      layer="top" pcbX={6} pcbY={40} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_LCD_OVLO_TOP" resistance="34.4k" footprint="0603"
      connections={{ pin1: "net.V5_MAIN", pin2: "net.LCD_OVLO" }}
      layer="top" pcbX={1} pcbY={18} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_LCD_OVLO_BOT" resistance="10k" footprint="0603"
      connections={{ pin1: "net.LCD_OVLO", pin2: "net.GND" }}
      layer="top" pcbX={6} pcbY={18} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_PI_ILM" resistance="1.07k" footprint="0603"
      connections={{ pin1: "net.PI_ILM", pin2: "net.GND" }}
      layer="top" pcbX={11} pcbY={40} />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="R_LCD_ILM" resistance="6.65k" footprint="0603"
      connections={{ pin1: "net.LCD_ILM", pin2: "net.GND" }}
      layer="top" pcbX={9.5} pcbY={23.225} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_PI_DVDT" capacitance="1nF" footprint="0603"
      connections={{ pin1: "net.PI_DVDT", pin2: "net.GND" }}
      layer="top" pcbX={12} pcbY={35} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_LCD_DVDT" capacitance="1nF" footprint="0603"
      connections={{ pin1: "net.LCD_DVDT", pin2: "net.GND" }}
      layer="top" pcbX={12} pcbY={20.5} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_LCD_FUSE_IN" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V5_MAIN", pin2: "net.GND" }}
      layer="top" pcbX={1} pcbY={23} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_LCD_FUSE_OUT" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V5_LCD", pin2: "net.GND" }}
      layer="top" pcbX={12} pcbY={28} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_PI_FUSE_IN" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.V5_MAIN", pin2: "net.GND" }}
      layer="top" pcbX={1} pcbY={35} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }} pcbSx={{ "& silkscreentext": { visibility: "hidden" } }} schSectionName="Power outputs" name="C_PI_FUSE_OUT" capacitance="22uF" footprint="1206"
      connections={{ pin1: "net.V5_PI", pin2: "net.GND" }}
      layer="top" pcbX={13} pcbY={44} />
  </>
);
