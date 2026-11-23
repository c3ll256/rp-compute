import { electrical, unusedPiPins } from "./electrical";
import { board, mountingHoles, interfaces, placements, functionalLabels } from "./layout";
import { boardPropsFromRules, groundPourPropsFromRules, keepoutPropsFromRules, netPropsFor, pcbRules } from "./lib/replicator-pcb";

// Lite variant: Pi USB-C is the only input. Pins 2/4 feed this PCB, never the Pi.
// TI DBV/PW pin maps and Sharp external-COM mode: see implementation.md.
// Leave Pi reserved/unused pins, LDO NC and disabled buffer outputs unconnected.
// Ordinary parts target >=2mm land-envelope clearance from every outline edge.
// The Pi/display interfaces retain their mechanical datums; decouplers follow their ICs.
// Wider outline removes the recess bottleneck. Only J_PI remains on bottom.
// Functional clusters and side map are declared in layout.ts; bypass caps follow VCC.
export default () => (
  <board width={board.width} height={board.height} center_x={board.centerX} center_y={board.centerY} outline={board.outline} {...boardPropsFromRules()}>
    {Object.keys(pcbRules.nets).map(n => <net key={n} name={n} {...netPropsFor(n)} />)}
    {groundPourPropsFromRules().map(p => <copperpour key={p.name} {...p} />)}
    {keepoutPropsFromRules().map(k => <keepout {...k} />)}
    {["Touch and audio", "Pi dock", "LCD interface", "LCD SPI buffer", "LCD COM buffer", "LCD supply"].map(n => <schematicsection key={n} name={n} />)}
    {functionalLabels.map(label => <silkscreentext key={label.text} {...label} fontSize="1mm" layer="top" />)}
    {mountingHoles.map(h => <hole key={h.name} name={h.name} pcbX={h.x} pcbY={h.y} diameter="2.2mm" />)}
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="J_PI"
      pinAttributes={electrical.J_PI}
      noConnect={unusedPiPins}
      // Generic user-selected2x20 PTH socket; native KiCad2.54mm grid,1mm drills.
      // Copper is the unchanged KiCad library; model is the explicit8mm/3.5mm user-spec reference.
      cadModel={{stepUrl:"./source/models/generic_40pin-nominal.step",modelOriginPosition:{x:-1.27,y:-24.13,z:0},positionOffset:{x:0,y:0,z:0},rotationOffset:{x:0,y:0,z:0},modelUnitToMmScale:1,modelBoardNormalDirection:"z+"}}
      footprint="vendor:KiCad_PinSocket_2x20_P2.54mm_GenericH8"
      pinLabels={{"pin1": "P1", "pin2": "P2", "pin3": "P3", "pin4": "P4", "pin5": "P5", "pin6": "P6", "pin7": "P7", "pin8": "P8", "pin9": "P9", "pin10": "P10", "pin11": "P11", "pin12": "P12", "pin13": "P13", "pin14": "P14", "pin15": "P15", "pin16": "P16", "pin17": "P17", "pin18": "P18", "pin19": "P19", "pin20": "P20", "pin21": "P21", "pin22": "P22", "pin23": "P23", "pin24": "P24", "pin25": "P25", "pin26": "P26", "pin27": "P27", "pin28": "P28", "pin29": "P29", "pin30": "P30", "pin31": "P31", "pin32": "P32", "pin33": "P33", "pin34": "P34", "pin35": "P35", "pin36": "P36", "pin37": "P37", "pin38": "P38", "pin39": "P39", "pin40": "P40"}}
      connections={{"P3": "net.SDA", "P5": "net.SCL", "P13": "net.NRST", "P11": "net.RDY", "P12": "net.BCLK", "P35": "net.WS", "P38": "net.MIC_SD", "P40": "net.AMP_DIN", "P2": "net.V5_PI_IN", "P4": "net.V5_PI_IN", "P1": "net.V3V3_PI", "P17": "net.V3V3_PI", "P19": "net.GPIO10", "P23": "net.GPIO11", "P24": "net.GPIO8", "P32": "net.GPIO12", "P22": "net.GPIO25", "P18": "net.GPIO24", "P36": "net.FAULT_N", "P6": "net.GND", "P9": "net.GND", "P14": "net.GND", "P20": "net.GND", "P25": "net.GND", "P30": "net.GND", "P34": "net.GND", "P39": "net.GND"}}
      layer="bottom"
      pcbX={interfaces.piDock.x}
      pcbY={interfaces.piDock.y}
      pcbRotation={interfaces.piDock.rotation}
      schSectionName="Pi dock" />
    <connector pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="J_LCD"
      pinAttributes={electrical.J_LCD}
      noConnect={["pin11", "pin12"]}
      manufacturerPartNumber="0.5-10P CTSJ-H2.0 119"
      // Downloaded JLCEDA/EasyEDA official STEP, SHA504b9584...; actual slot/latch.
      // Supplier head-to-model Y=-1.2800076mm, footprint loader recenters lands +0.35mm.
      // Use net offset -0.9300076mm; raw Z=-1mm is normalized to seating Z=0.
      cadModel={{stepUrl:"./source/models/C5373447-easyeda.step",modelOriginPosition:{x:0,y:0,z:0},positionOffset:{x:0,y:-0.9300076,z:1},rotationOffset:{x:0,y:0,z:0},modelUnitToMmScale:1,modelBoardNormalDirection:"z+"}}
      footprint="jlcpcb:C5373447"
      // Sharp back-side-up drawing p26 has terminal1 left; in display/front
      // assembly coordinates it is right. A return fold about X preserves X.
      // SHOU HAN supplier top view also has pin1 left; retain 11-panel terminal mapping.
      pinLabels={{"pin1": "VSSA", "pin2": "VSS", "pin3": "EXTMODE", "pin4": "VDD", "pin5": "VDDA", "pin6": "DISP", "pin7": "EXTCOMIN", "pin8": "SCS", "pin9": "SI", "pin10": "SCLK"}}
      connections={{"SCLK": "net.LCD_SCLK", "SI": "net.LCD_SI", "SCS": "net.LCD_SCS", "EXTCOMIN": "net.LCD_COM", "DISP": "net.LCD_DISP", "VDDA": "net.V5_LCD", "VDD": "net.V5_LCD", "EXTMODE": "net.V5_LCD", "VSS": "net.GND", "VSSA": "net.GND"}}
      layer="top"
      pcbX={interfaces.displayFpc.x}
      pcbY={interfaces.displayFpc.y}
      pcbRotation={interfaces.displayFpc.rotation}
      schSectionName="LCD interface"
      supplierPartNumbers={{"jlcpcb": ["C5373447"]}} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="U_BUF1"
      pinAttributes={electrical.U_BUF1}
      // Functional symbol: inputs left, outputs right, supply above, ground below.
      schPinArrangement={{
        leftSide: ["OE1_N", "A1", "OE2_N", "A2", "OE3_N", "A3", "OE4_N", "A4"],
        rightSide: ["Y1", "Y2", "Y3", "Y4"],
        topSide: ["VCC"], bottomSide: ["GND"],
      }}
      manufacturerPartNumber="SN74AHC125PWR"
      footprint="jlcpcb:C54529"
      pinLabels={{"pin1": "OE1_N", "pin2": "A1", "pin3": "Y1", "pin4": "OE2_N", "pin5": "A2", "pin6": "Y2", "pin7": "GND", "pin8": "Y3", "pin9": "A3", "pin10": "OE3_N", "pin11": "Y4", "pin12": "A4", "pin13": "OE4_N", "pin14": "VCC"}}
      connections={{"VCC": "net.V3V3_LCD", "GND": "net.GND", "OE1_N": "net.GND", "A1": "net.GPIO11", "Y1": "net.LCD_SCLK", "OE2_N": "net.GND", "A2": "net.GPIO10", "Y2": "net.LCD_SI", "OE3_N": "net.GND", "A3": "net.GPIO8", "Y3": "net.LCD_SCS", "OE4_N": "net.GND", "A4": "net.GPIO25", "Y4": "net.LCD_DISP"}}
      layer="top"
      {...placements.U_BUF1}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C54529"]}} />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="U_BUF2"
      pinAttributes={electrical.U_BUF2}
      // Functional symbol: inputs left, outputs right, supply above, ground below.
      schPinArrangement={{
        leftSide: ["OE1_N", "A1", "OE2_N", "A2", "OE3_N", "A3", "OE4_N", "A4"],
        rightSide: ["Y1", "Y2", "Y3", "Y4"],
        topSide: ["VCC"], bottomSide: ["GND"],
      }}
      noConnect={["Y2", "Y3", "Y4"]}
      manufacturerPartNumber="SN74AHC125PWR"
      footprint="jlcpcb:C54529"
      pinLabels={{"pin1": "OE1_N", "pin2": "A1", "pin3": "Y1", "pin4": "OE2_N", "pin5": "A2", "pin6": "Y2", "pin7": "GND", "pin8": "Y3", "pin9": "A3", "pin10": "OE3_N", "pin11": "Y4", "pin12": "A4", "pin13": "OE4_N", "pin14": "VCC"}}
      connections={{"VCC": "net.V3V3_LCD", "GND": "net.GND", "OE1_N": "net.GND", "A1": "net.GPIO12", "Y1": "net.LCD_COM", "OE2_N": "net.V3V3_LCD", "A2": "net.GND", "OE3_N": "net.V3V3_LCD", "A3": "net.GND", "OE4_N": "net.V3V3_LCD", "A4": "net.GND"}}
      layer="top"
      {...placements.U_BUF2}
      schSectionName="LCD COM buffer"
      supplierPartNumbers={{"jlcpcb": ["C54529"]}} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_BUF1"
      manufacturerPartNumber="CC0603KRX7R9BB104"
      footprint="jlcpcb:C14663"
      connections={{"pin1": "net.V3V3_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_BUF1}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C14663"]}}
      capacitance="100nF" />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_BUF2"
      manufacturerPartNumber="CC0603KRX7R9BB104"
      footprint="jlcpcb:C14663"
      connections={{"pin1": "net.V3V3_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_BUF2}
      schSectionName="LCD COM buffer"
      supplierPartNumbers={{"jlcpcb": ["C14663"]}}
      capacitance="100nF" />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_LCD_A"
      manufacturerPartNumber="CC0603KRX7R9BB104"
      footprint="jlcpcb:C14663"
      connections={{"pin1": "net.V5_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_LCD_A}
      schSectionName="LCD interface"
      supplierPartNumbers={{"jlcpcb": ["C14663"]}}
      capacitance="100nF" />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_LCD_D"
      manufacturerPartNumber="CL21A225KBQNNNE"
      footprint="jlcpcb:C377773"
      connections={{"pin1": "net.V5_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_LCD_D}
      schSectionName="LCD interface"
      supplierPartNumbers={{"jlcpcb": ["C377773"]}}
      capacitance="2.2uF" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_OFF_CLK"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO11", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_OFF_CLK}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_OFF_DATA"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO10", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_OFF_DATA}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_OFF_CS"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO8", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_OFF_CS}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_OFF_DISP"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO25", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_OFF_DISP}
      schSectionName="LCD SPI buffer"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_OFF_COM"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO12", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_OFF_COM}
      schSectionName="LCD COM buffer"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="U_LCD_LIMIT"
      pinAttributes={electrical.U_LCD_LIMIT}
      manufacturerPartNumber="TPS2553DBVR"
      footprint="kicad:Package_TO_SOT_SMD/SOT-23-6"
      pinLabels={{"pin1": "IN", "pin2": "GND", "pin3": "EN", "pin4": "FAULT_N", "pin5": "ILIM", "pin6": "OUT"}}
      connections={{"IN": "net.V5_PI_IN", "GND": "net.GND", "EN": "net.GPIO24", "FAULT_N": "net.FAULT_N", "ILIM": "net.LCD_ILIM", "OUT": "net.V5_LCD"}}
      layer="top"
      {...placements.U_LCD_LIMIT}
      schSectionName="LCD supply" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_LCD_ILIM" schRotation={90}
      manufacturerPartNumber="0603WAF1693T5E"
      footprint="jlcpcb:C22817"
      connections={{"pin1": "net.LCD_ILIM", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_LCD_ILIM}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C22817"]}}
      resistance="169k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_LCD_EN"
      manufacturerPartNumber="0603WAF1003T5E"
      footprint="jlcpcb:C25803"
      connections={{"pin1": "net.GPIO24", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_LCD_EN}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C25803"]}}
      resistance="100k" />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_LCD_IN"
      manufacturerPartNumber="CL21A225KBQNNNE"
      footprint="jlcpcb:C377773"
      connections={{"pin1": "net.V5_PI_IN", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_LCD_IN}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C377773"]}}
      capacitance="2.2uF" />
    <chip pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="U_LCD_LDO"
      pinAttributes={electrical.U_LCD_LDO}
      noConnect={["NC"]}
      manufacturerPartNumber="TLV75533PDBVR"
      footprint="jlcpcb:C404027"
      pinLabels={{"pin1": "IN", "pin2": "GND", "pin3": "EN", "pin4": "NC", "pin5": "OUT"}}
      connections={{"IN": "net.V5_LCD", "GND": "net.GND", "EN": "net.V5_LCD", "OUT": "net.V3V3_LCD"}}
      layer="top"
      {...placements.U_LCD_LDO}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C404027"]}} />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_LCD_LIN"
      manufacturerPartNumber="CL21A225KBQNNNE"
      footprint="jlcpcb:C377773"
      connections={{"pin1": "net.V5_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_LCD_LIN}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C377773"]}}
      capacitance="2.2uF" />
    <capacitor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="C_LCD_LOUT"
      manufacturerPartNumber="CL21A225KBQNNNE"
      footprint="jlcpcb:C377773"
      connections={{"pin1": "net.V3V3_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.C_LCD_LOUT}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C377773"]}}
      capacitance="2.2uF" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_LCD_BLEED"
      manufacturerPartNumber="0603WAF1002T5E"
      footprint="jlcpcb:C25804"
      connections={{"pin1": "net.V5_LCD", "pin2": "net.GND"}}
      layer="top"
      {...placements.R_LCD_BLEED}
      schSectionName="LCD supply"
      supplierPartNumbers={{"jlcpcb": ["C25804"]}}
      resistance="10k" />
    <resistor pcbStyle={{ silkscreenTextVisibility: "hidden" }}
      name="R_FAULT_PU"
      manufacturerPartNumber="0603WAF1002T5E"
      footprint="jlcpcb:C25804"
      connections={{"pin1": "net.V3V3_PI", "pin2": "net.FAULT_N"}}
      layer="top"
      {...placements.R_FAULT_PU}
      schSectionName="Pi dock"
      supplierPartNumbers={{"jlcpcb": ["C25804"]}}
      resistance="10k" />
    <connector name="J_TP"
      manufacturerPartNumber="FH12-6S-0.5SH(55)" supplierPartNumbers={{ jlcpcb: ["C202118"] }}
      footprint="kicad:Connector_FFC-FPC/Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal" layer="top" {...placements.J_TP}
      connections={{"pin3": "net.V3V3_PI", "pin4": "net.GND", "pin1": "net.SDA", "pin2": "net.SCL", "pin5": "net.NRST", "pin6": "net.RDY"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" pinLabels={{"pin1": "SDA", "pin2": "SCL", "pin3": "VDD", "pin4": "GND", "pin5": "NRST", "pin6": "RDY"}} pinAttributes={{RDY:{isOutput:true,canUseOpenDrain:true,isUsingOpenDrain:true}}}/>
    <chip name="U_MIC"
      manufacturerPartNumber="ICS-43434" supplierPartNumbers={{ jlcpcb: ["C5656610"] }}
      // Library STEP uses the same pin-1 datum as the copper; JLC tape zero is rotated 270° here.
      cadModel={{stepUrl:"./source/models/InvenSense_ICS-43434-6_3.5x2.65mm.step", modelOriginPosition:{x:0,y:0,z:0}, modelUnitToMmScale:1, modelBoardNormalDirection:"z+"}}
      footprint="vendor:ICS43434_Acoustic_0p60" layer="top" {...placements.U_MIC}
      connections={{"pin1": "net.WS", "pin2": "net.GND", "pin3": "net.GND", "pin4": "net.BCLK", "pin5": "net.V3V3_PI", "pin6": "net.MIC_SD"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" pinLabels={{pin1:"WS",pin2:"LR",pin3:"GND",pin4:"SCK",pin5:"VDD",pin6:"SD"}} pinAttributes={{VDD:{requiresPower:true,requiresVoltage:3.3},GND:{requiresGround:true},SD:{isOutput:true},WS:{isInput:true},SCK:{isInput:true},LR:{isInput:true}}}/>
    <capacitor name="C_MIC"
      manufacturerPartNumber="CC0603KRX7R9BB104" supplierPartNumbers={{ jlcpcb: ["C14663"] }}
      footprint="jlcpcb:C14663" layer="top" {...placements.C_MIC}
      connections={{"pin1": "net.V3V3_PI", "pin2": "net.GND"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" capacitance="100nF"/>
    <connector name="J_SPK"
      manufacturerPartNumber="SM02B-SRSS-TB(LF)(SN)" supplierPartNumbers={{ jlcpcb: ["C160402"] }}
      footprint="kicad:Connector_JST/JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal" layer="top" {...placements.J_SPK}
      connections={{"pin1": "net.SPK_P", "pin2": "net.SPK_N"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" pinLabels={{"pin1": "SPKP", "pin2": "SPKN"}}/>
    <chip name="U_AMP"
      manufacturerPartNumber="MAX98357AETE+T" supplierPartNumbers={{ jlcpcb: ["C910544"] }}
      footprint="jlcpcb:C910544" layer="top" {...placements.U_AMP}
      connections={{"pin3": "net.GND", "pin11": "net.GND", "pin15": "net.GND", "pin17": "net.GND", "pin7": "net.V5_PI_IN", "pin8": "net.V5_PI_IN", "pin4": "net.V5_PI_IN", "pin16": "net.BCLK", "pin14": "net.WS", "pin1": "net.AMP_DIN", "pin2": "net.AMP_GAIN", "pin9": "net.OUTP", "pin10": "net.OUTN"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" pinAttributes={{"pin1": {"isInput": true, "mustBeConnected": true}, "pin2": {"isInput": true, "mustBeConnected": true}, "pin4": {"isInput": true, "mustBeConnected": true}, "pin14": {"isInput": true, "mustBeConnected": true}, "pin16": {"isInput": true, "mustBeConnected": true}, "pin7": {"requiresPower": true, "requiresVoltage": 5}, "pin8": {"requiresPower": true, "requiresVoltage": 5}, "pin9": {"isOutput": true}, "pin10": {"isOutput": true}, "pin3": {"requiresGround": true}, "pin11": {"requiresGround": true}, "pin15": {"requiresGround": true}, "pin17": {"requiresGround": true}}} noConnect={["pin5","pin6","pin12","pin13"]} pinLabels={{"pin1": "DIN", "pin2": "GAIN_SLOT", "pin3": "GND1", "pin4": "SD_MODE", "pin5": "NC5", "pin6": "NC6", "pin7": "VDD1", "pin8": "VDD2", "pin9": "OUTP", "pin10": "OUTN", "pin11": "GND2", "pin12": "NC12", "pin13": "NC13", "pin14": "LRCLK", "pin15": "GND3", "pin16": "BCLK", "pin17": "EP"}}/>
    <capacitor name="C_AMP_HF"
      manufacturerPartNumber="CC0603KRX7R9BB104" supplierPartNumbers={{ jlcpcb: ["C14663"] }}
      footprint="jlcpcb:C14663" layer="top" {...placements.C_AMP_HF}
      connections={{"pin2": "net.GND", "pin1": "net.V5_PI_IN"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" capacitance="100nF"/>
    <capacitor name="C_AMP_BULK"
      manufacturerPartNumber="CL31B106KOHNNNE" supplierPartNumbers={{ jlcpcb: ["C47971"] }}
      footprint="jlcpcb:C47971" layer="top" {...placements.C_AMP_BULK}
      connections={{"pin2": "net.GND", "pin1": "net.V5_PI_IN"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" capacitance="10uF"/>
    <resistor name="R_GAIN"
      manufacturerPartNumber="0603WAF1003T5E" supplierPartNumbers={{ jlcpcb: ["C25803"] }}
      footprint="jlcpcb:C25803" layer="top" {...placements.R_GAIN}
      connections={{"pin1": "net.V5_PI_IN", "pin2": "net.AMP_GAIN"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="100k"/>
    <resistor name="R_MIC_SD"
      manufacturerPartNumber="0603WAF1003T5E" supplierPartNumbers={{ jlcpcb: ["C25803"] }}
      footprint="jlcpcb:C25803" layer="top" {...placements.R_MIC_SD}
      connections={{"pin2": "net.GND", "pin1": "net.MIC_SD"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="100k"/>
    <resistor name="R_SPK_P"
      manufacturerPartNumber="25121WJ047JT4E" supplierPartNumbers={{ jlcpcb: ["C25489"] }}
      footprint="jlcpcb:C25489" layer="top" {...placements.R_SPK_P}
      connections={{"pin1": "net.OUTP", "pin2": "net.SPK_P"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="4.7"/>
    <resistor name="R_SPK_N"
      manufacturerPartNumber="25121WJ047JT4E" supplierPartNumbers={{ jlcpcb: ["C25489"] }}
      footprint="jlcpcb:C25489" layer="top" {...placements.R_SPK_N}
      connections={{"pin1": "net.OUTN", "pin2": "net.SPK_N"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="4.7"/>
    <resistor name="R_TP_RST"
      manufacturerPartNumber="0603WAF1002T5E" supplierPartNumbers={{ jlcpcb: ["C25804"] }}
      footprint="jlcpcb:C25804" layer="top" {...placements.R_TP_RST}
      connections={{"pin1": "net.V3V3_PI", "pin2": "net.NRST"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="10k"/>
    <resistor name="R_TP_RDY"
      manufacturerPartNumber="0603WAF1002T5E" supplierPartNumbers={{ jlcpcb: ["C25804"] }}
      footprint="jlcpcb:C25804" layer="top" {...placements.R_TP_RDY}
      connections={{"pin1": "net.V3V3_PI", "pin2": "net.RDY"}}
      pcbStyle={{ silkscreenTextVisibility: "hidden" }} schSectionName="Touch and audio" resistance="10k"/>
  </board>
);
