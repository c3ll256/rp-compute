// Baseboard outline and board-frame interface datums for the handheld terminal.
//
// FRAME: the board is centred on its own origin. Y+ is toward the Pi's rear
// (USB/Ethernet) edge; Y- is toward the screen pod and the front module deck.
// All values here are BOARD frame; world placement is the dock transform in
// design/handheld_computer (see the README there).
//
// Wider continuous electronics area: all populated parts on top except J_PI.
// Original overall envelope and mounting datums are preserved; filled former recess
// buys area for one-sided SMT and relaxed buffer placement.
// Defaults for this layout iteration, not a qualified shell mounting pattern.
// Narrow 76mm enclosure: Pi moves -5mm in X, while LCD and module stay fixed.
// Front retainer screws now sit at X+/-27; the left outline clears their ear.
export const board = {
  width: "44.5mm", height: "83.5mm", centerX: -2.25, centerY: 6.25,
  outline: [
    {x:-24.5,y:-35.5}, {x:20,y:-35.5},
    {x:20,y:38}, {x:-5,y:38}, {x:-5,y:48}, {x:-24.5,y:48},
    {x:-24.5,y:20}, {x:-23.5,y:19},
    {x:-23.5,y:11.5}, {x:-24.5,y:10.5}
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
  // ESQ underside,11.05mm housing. Native supplier numbering is paired
  // across the opposite row from Pi top-view numbering: main.tsx swaps each pair.
  // This preserves every original Pi world pin datum; no GPIO net swap.
  piDock: { x: -18.5, y: 21, rotation: 270, side: "bottom" },

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

  // Top-side3.66mm HLE SMT2x4. Physical mating pitch2.54mm, land-row
  // separation5.05mm. Pin1 is front-view upper/left, same module net order.
  frontModule: { x: 0, y: -15, rotation: 0, side: "top", mating: "+Z" },

  // Keepout the socket body needs through the deck aperture.
  frontModuleAperture: { width: 54.0, depth: 26.0, centreY: -34.0 }
};
