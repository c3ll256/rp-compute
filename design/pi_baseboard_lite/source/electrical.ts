// Pin directions describe the connected device, including the Pi at J_PI.
// Evidence: TI SN74AHC125 SCLS256O p4, TPS2553 SLVS841F p5,
// TLV755P SBVS320D p3; Sharp LCY-1210401A terminal table.
// https://www.ti.com/lit/ds/symlink/sn74ahc125.pdf
// https://www.ti.com/lit/ds/symlink/tps2553.pdf
// https://www.ti.com/lit/ds/symlink/tlv755p.pdf
// Existing verified physical pin mappings in main.tsx remain authoritative.

const input = { isInput: true, mustBeConnected: true };
const output = { isOutput: true, canUseTriState: true };
const gpio = { isBidirectional: true };
const ground = { requiresGround: true, mustBeConnected: true };
const supply3v3 = { requiresPower: true, requiresVoltage: 3.3 };
const supply5 = { requiresPower: true, requiresVoltage: 5 };

const buffer = {
  VCC: supply3v3, GND: ground,
  OE1_N: input, A1: input, Y1: output,
  OE2_N: input, A2: input, Y2: output,
  OE3_N: input, A3: input, Y3: output,
  OE4_N: input, A4: input, Y4: output,
};
const limiter = {
  IN: supply5, GND: ground, EN: input,
  // Both FAULT outputs are deliberately wired-OR and pulled up to Pi 3.3 V.
  FAULT_N: { isOutput: true, canUseOpenDrain: true, isUsingOpenDrain: true },
  ILIM: { isOutput: true, mustBeConnected: true },
  OUT: { providesPower: true, providesVoltage: 5 },
};
const ldo = {
  IN: supply5, GND: ground, EN: input,
  NC: { doNotConnect: true },
  OUT: { providesPower: true, providesVoltage: 3.3 },
};

export const electrical = {
  U_BUF1: buffer, U_BUF2: buffer,
  U_LCD_LIMIT: limiter, U_AUX_LIMIT: limiter,
  U_LCD_LDO: ldo, U_AUX_LDO: ldo,
  J_PI: {
    // The Pi has one external source per rail, with redundant header contacts.
    // Represent its drive once; the other contacts are passive continuations
    // of that same source, not independent supplies connected in parallel.
    P2: { providesPower: true, providesVoltage: 5 },
    P4: { isPassive: true },
    P1: { providesPower: true, providesVoltage: 3.3 },
    P17: { isPassive: true },
    P6: { providesGround: true }, P9: { isPassive: true },
    P14: { isPassive: true }, P20: { isPassive: true },
    P25: { isPassive: true }, P30: { isPassive: true },
    P34: { isPassive: true }, P39: { isPassive: true },
    P3: gpio, P5: gpio,
    P19: output, P21: input, P23: output, P24: output, P26: output,
    P32: output, P22: output, P18: output, P36: input,
  },
  J_LCD: {
    SCLK: input, SI: input, SCS: input, EXTCOMIN: input, DISP: input,
    VDDA: supply5, VDD: supply5,
    EXTMODE: input, VSS: ground, VSSA: ground,
  },
  J_MOD: {
    M1: supply3v3, M2: ground,
    M3: gpio, M4: gpio,
    M5: input, M6: output, M7: input, M8: input,
  },
};

// Reserved/unused Pi contacts are intentionally not routed, not missing wires.
export const unusedPiPins = [
  "P7", "P8", "P10", "P11", "P12", "P13", "P15", "P16", "P27",
  "P28", "P29", "P31", "P33", "P35", "P37", "P38", "P40",
];
