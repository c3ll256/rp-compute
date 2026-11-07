// Baseboard outline and board-frame interface datums for the handheld terminal.
//
// FRAME: the board is centred on its own origin. Y+ is toward the Pi's rear
// (USB/Ethernet) edge; Y- is toward the screen pod and the front module deck.
// All values here are BOARD frame; world placement is the dock transform in
// design/handheld_computer (see the README there).
//
// Compact rectangular board: remove the unused front15mm and straighten the
// former left relief/rear step. Full width connects both mount pads to the
// GPIO spine without a narrow neck. All interface and mounting datums stay put.
// Strength bias: retain0.8mm FR4, two M2 holes and the rear shell edge support.
export const board = {
  width: "43.5mm", height: "68.5mm", centerX: -1.75, centerY: 13.75,
  outline: [
    {x:-23.5,y:-20.5}, {x:20,y:-20.5},
    {x:20,y:48}, {x:-23.5,y:48}
  ]
};

// Pin 1 datum. The Pi's official mechanical drawing puts the 40-pin header
// centroid 32.5mm behind the Pi board's front edge and 3.5mm in from its left
// edge. Docking J_PI onto that centroid is what makes this board a baseboard,
// so this value is a datum, not a preference.
export const PI_GPIO_CENTROID_FROM_PI_BOARD_FRONT_MM = 32.5;

// M2 fixture holes. Reference only: upper-shell mounts now share these datums, with
// two fixed upper-shell beam joints; holes are2.2mm NPTH.
export const mountingHoles = [
  { name: "H1", x: -16, y: -13 },
  { name: "H2", x: 16, y: -13 }
];

// Placement-only service corridor in front of J_LCD. Copper and flush vias may
// cross it. Agent default: 8mm width versus a 5.5 +/-0.05mm panel tail;
// covers 13.67mm ahead of the closed body front at Y=21.1699924 and the
// supplier slider's additional 1.5mm forward stroke. Not a certified bend path.
// verify-front-side-layout.py checks every top component land envelope.
export const fpcInsertionClearance = {
  minX: -4, maxX: 4, minY: 7.5, maxY: 21.1699924,
  source: "default", purpose: "top component exclusion for insertion and service"
};

export function rotationForOpening(
  native: "up" | "right" | "down" | "left",
  target: "up" | "right" | "down" | "left"
) {
  const angle = { right: 0, up: 90, left: 180, down: 270 };
  return (angle[target] - angle[native] + 360) % 360;
}

export const interfaces = {
  // Native KiCad2x20 is long alongY; bottom-side mirror plus180deg
  // preserves the Pi physical pin datums with identity Pn-to-padn labels.
  // Generic housing8mm; tails3.5mm. Exact coordinates audited after compile.
  piDock: { centerX: -18.5, centerY: 21, x: -18.5, y: 21, rotation: 180, side: "bottom" },

  // Horizontal top-side FPC, entry down/front (-Y) per user. Shifted rearward
  // with upward contacts matching the return-folded native tail. Position is a fit default.
  displayFpc: {
    x: 0,
    y: 24.65,
    rotation: rotationForOpening("down", "down"),
    side: "top",
    contactFace: "away from PCB / exposed copper upward",
    opening: "-Y / down in board top view"
  },

  // Generic5mm-height2x4 PTH socket.90deg rotates native longY
  // to longX; physical pin1 remains upper/left,2 lower/left.
  frontModule: { centerX: 0, centerY: -15, x: 0, y: -15, rotation: 90, side: "top", mating: "+Z" },

  // Keepout the socket body needs through the deck aperture.
  frontModuleAperture: { width: 54.0, depth: 26.0, centreY: -34.0 }
};

// Placement-only cleanup: fixed interfaces, outline, holes and the FPC service
// corridor above are assembly datums. Movable electronics use these functional
// clusters on top; only J_PI is on bottom. Values are engineering defaults.
// Display buffers share a row behind the FPC, with their input pull-downs behind
// them and bypass capacitors at VCC. Parallel LCD/module power clusters place
// each limiter, LDO and its support parts together instead of at opposite ends.
export const placements = {
  U_BUF1: { pcbX: -7.5, pcbY: 32, pcbRotation: 90 },
  U_BUF2: { pcbX: 11.5, pcbY: 32, pcbRotation: 90 },
  C_BUF1: { pcbX: -13, pcbY: 30.05, pcbRotation: 90 },
  C_BUF2: { pcbX: 6, pcbY: 30.05, pcbRotation: 90 },
  C_LCD_A: { pcbX: -2, pcbY: 29.5, pcbRotation: 0 },
  C_LCD_D: { pcbX: 2, pcbY: 29.5, pcbRotation: 0 },
  R_OFF_CLK: { pcbX: -4, pcbY: 35.5, pcbRotation: 0 },
  R_OFF_DATA: { pcbX: 0, pcbY: 35.5, pcbRotation: 0 },
  R_OFF_CS: { pcbX: -12, pcbY: 35.5, pcbRotation: 0 },
  R_OFF_DISP: { pcbX: -8, pcbY: 35.5, pcbRotation: 0 },
  R_OFF_COM: { pcbX: 12, pcbY: 35.5, pcbRotation: 0 },
  U_LCD_LIMIT: { pcbX: -9, pcbY: 2, pcbRotation: 90 },
  C_LCD_IN: { pcbX: -13, pcbY: 1, pcbRotation: 90 },
  R_LCD_EN: { pcbX: -6, pcbY: -1, pcbRotation: 0 },
  R_LCD_ILIM: { pcbX: -9, pcbY: 6, pcbRotation: 0 },
  U_LCD_LDO: { pcbX: -9, pcbY: -7.5, pcbRotation: 180 },
  C_LCD_LIN: { pcbX: -13, pcbY: -6.5, pcbRotation: 90 },
  C_LCD_LOUT: { pcbX: -5, pcbY: -6.5, pcbRotation: 90 },
  R_LCD_BLEED: { pcbX: -9, pcbY: -11.0, pcbRotation: 0 },
  U_AUX_LIMIT: { pcbX: 10, pcbY: 2, pcbRotation: 90 },
  C_AUX_IN: { pcbX: 6, pcbY: 1, pcbRotation: 90 },
  R_AUX_EN: { pcbX: 13, pcbY: -1, pcbRotation: 0 },
  R_AUX_ILIM: { pcbX: 10, pcbY: 6, pcbRotation: 0 },
  U_AUX_LDO: { pcbX: 10, pcbY: -7.5, pcbRotation: 180 },
  C_AUX_LIN: { pcbX: 6, pcbY: -6.5, pcbRotation: 90 },
  C_AUX_LOUT: { pcbX: 14, pcbY: -6.5, pcbRotation: 90 },
  R_AUX_BLEED: { pcbX: 10, pcbY: -11.0, pcbRotation: 0 },
  R_FAULT_PU: { pcbX: 0, pcbY: 1, pcbRotation: 0 },
} as const;

export const functionalLabels = [
  { text: "U_BUF1", pcbX: -7.5, pcbY: 28.2 },
  { text: "U_BUF2", pcbX: 11.5, pcbY: 28.2 },
  { text: "LCD / FPC", pcbX: 0, pcbY: 18 },
  { text: "LCD PWR", pcbX: -9, pcbY: 9 },
  { text: "AUX PWR", pcbX: 10, pcbY: 9 },
  { text: "MODULE", pcbX: 0, pcbY: -11 },
  { text: "PI LITE", pcbX: 10, pcbY: 22 },
] as const;
