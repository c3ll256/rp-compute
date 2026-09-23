// BQ25622 charger / power-path application based on TI SLUSEG2D figure 9-2,
// pp 5-6, 23, 27 and 69. Charging is held disabled at startup by CE pullup;
// firmware must qualify battery temperature, pack limits and input allowance.
export const Charger = () => (
  <>
    <chip name="U_CHARGER" manufacturerPartNumber="BQ25622RYKR"
      footprint="jlcpcb:C6135214" supplierPartNumbers={{ jlcpcb: ["C6135214"] }}
      pinLabels={{
        pin1: "BTST", pin2: "REGN", pin3: "PG", pin4: "ILIM",
        pin5: "TS_BIAS", pin6: "TS", pin7: "QON", pin8: "BAT",
        pin9: "SYS", pin10: "STAT", pin11: "INT", pin12: "SDA",
        pin13: "SCL", pin14: "CE", pin15: "GND", pin16: "SW",
        pin17: "PMID", pin18: "VBUS",
      }}
      connections={{
        BTST: "net.CHG_BTST", REGN: "net.CHG_REGN", PG: "net.CHG_PG",
        ILIM: "net.CHG_ILIM", TS_BIAS: "net.CHG_TS_BIAS", TS: "net.CHG_TS",
        BAT: "net.BAT_RAW", SYS: "net.SYS_RAW", STAT: "net.CHG_STAT",
        INT: "net.CHG_INT", SDA: "net.CHG_SDA", SCL: "net.CHG_SCL",
        CE: "net.CHG_CE_N", GND: "net.GND", SW: "net.CHG_SW",
        PMID: "net.CHG_PMID", VBUS: "net.CHG_VBUS",
      }}
      layer="bottom" pcbX={12} pcbY={-26} />
    <inductor name="L_CHG" inductance="1uH" manufacturerPartNumber="74437349010"
      footprint="vendor:L_Wurth_WE-LHMI-7030" supplierPartNumbers={{ jlcpcb: ["C1332247"] }}
      connections={{ pin1: "net.CHG_SW", pin2: "net.SYS_RAW" }}
      layer="bottom" pcbX={20} pcbY={-26} />
    <capacitor name="C_CHG_VBUS" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.CHG_VBUS", pin2: "net.GND" }}
      layer="bottom" pcbX={5} pcbY={-24} />
    <capacitor name="C_CHG_PMID_BULK" capacitance="10uF" footprint="0805"
      connections={{ pin1: "net.CHG_PMID", pin2: "net.GND" }}
      layer="bottom" pcbX={5} pcbY={-30} />
    <capacitor name="C_CHG_PMID_HF" capacitance="100nF" footprint="0603"
      connections={{ pin1: "net.CHG_PMID", pin2: "net.GND" }}
      layer="bottom" pcbX={8} pcbY={-32} />
    <capacitor name="C_CHG_BTST" capacitance="47nF" footprint="0603"
      connections={{ pin1: "net.CHG_BTST", pin2: "net.CHG_SW" }}
      layer="bottom" pcbX={14} pcbY={-19} />
    <capacitor name="C_CHG_REGN" capacitance="4.7uF" footprint="0805"
      connections={{ pin1: "net.CHG_REGN", pin2: "net.GND" }}
      layer="bottom" pcbX={6} pcbY={-18} />
    <capacitor name="C_CHG_SYS1" capacitance="10uF" footprint="0805"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.GND" }}
      layer="bottom" pcbX={25} pcbY={-21} />
    <capacitor name="C_CHG_SYS2" capacitance="10uF" footprint="0805"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.GND" }}
      layer="bottom" pcbX={29} pcbY={-21} />
    <capacitor name="C_CHG_BAT" capacitance="10uF" footprint="0805"
      connections={{ pin1: "net.BAT_RAW", pin2: "net.GND" }}
      layer="bottom" pcbX={23} pcbY={-32} />
    {/* K_ILIM 2250..2750 AΩ: 1.1k/1% yields roughly 2.05..2.53 A.
        Its EN_EXTILIM register can reset; upstream eFuse remains independent. */}
    <resistor name="R_CHG_ILIM" resistance="1.1k" footprint="0603"
      connections={{ pin1: "net.CHG_ILIM", pin2: "net.GND" }}
      layer="bottom" pcbX={6} pcbY={-36} />
    {/* 103AT-2 TS network: TI pp27 RT1=5.23k, RT2=30.1k.
        One external NTC occupies J_CHG_NTC; open wire must inhibit charging. */}
    <resistor name="R_CHG_TS_TOP" resistance="5.23k" footprint="0603"
      connections={{ pin1: "net.CHG_TS_BIAS", pin2: "net.CHG_TS" }}
      layer="bottom" pcbX={14} pcbY={-36} />
    <resistor name="R_CHG_TS_BOTTOM" resistance="30.1k" footprint="0603"
      connections={{ pin1: "net.CHG_TS", pin2: "net.GND" }}
      layer="bottom" pcbX={19} pcbY={-36} />
    <connector name="J_CHG_NTC"
      footprint="kicad:Connector_Wire/SolderWire-0.25sqmm_1x02_P4.2mm_D0.65mm_OD1.7mm_Relief2x"
      pinLabels={{ pin1: "TS", pin2: "GND" }}
      connections={{ TS: "net.CHG_TS", GND: "net.GND" }}
      layer="bottom" pcbX={-28} pcbY={-12} />
    <connector name="J_BAT_WIRE"
      footprint="kicad:Connector_Wire/SolderWire-1sqmm_1x02_P5.4mm_D1.4mm_OD2.7mm_Relief"
      pinLabels={{ pin1: "BAT_POS", pin2: "BAT_NEG" }}
      connections={{ BAT_POS: "net.BAT_RAW", BAT_NEG: "net.GND" }}
      layer="bottom" pcbX={27} pcbY={16} pcbRotation={180} />
    {/* CE high disables charging until the supervisor pulls the open-drain
        CHG_CE_N low after checking the actual pack; reference source is SYS. */}
    <resistor name="R_CHG_CE_OFF" resistance="10k" footprint="0603"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.CHG_CE_N" }}
      layer="bottom" pcbX={3} pcbY={-38} />
    {/* Always-on supervisor supply from the charger SYS rail. */}
    <chip name="U_AON_LDO" manufacturerPartNumber="TLV75533PDBVR"
      footprint="jlcpcb:C404027" supplierPartNumbers={{ jlcpcb: ["C404027"] }}
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "NC", pin5: "OUT" }}
      connections={{ IN: "net.SYS_RAW", GND: "net.GND", EN: "net.SYS_RAW",
        OUT: "net.V3V3_AON" }}
      layer="bottom" pcbX={25} pcbY={-9} />
    <capacitor name="C_AON_IN" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.SYS_RAW", pin2: "net.GND" }}
      layer="bottom" pcbX={21} pcbY={-9} />
    <capacitor name="C_AON_OUT" capacitance="1uF" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.GND" }}
      layer="bottom" pcbX={29} pcbY={-9} />
    <resistor name="R_CHG_SDA_PU" resistance="4.7k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.CHG_SDA" }}
      layer="bottom" pcbX={16} pcbY={-43} />
    <resistor name="R_CHG_SCL_PU" resistance="4.7k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.CHG_SCL" }}
      layer="bottom" pcbX={20} pcbY={-43} />
    <resistor name="R_CHG_INT_PU" resistance="10k" footprint="0603"
      connections={{ pin1: "net.V3V3_AON", pin2: "net.CHG_INT" }}
      layer="bottom" pcbX={13} pcbY={-43} />
  </>
);
