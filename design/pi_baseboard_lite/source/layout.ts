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
export const board = {
  width: "40mm", height: "83.5mm", centerY: 6.25,
  outline: [
    {x:-20,y:-35.5}, {x:20,y:-35.5},
    // Exact old-enclosure retainer/fascia intersection at sourceX17.3..20,
    // sourceY11.66..22.31; retain >=0.5mm physical relief.
    {x:20,y:10.5}, {x:16.3,y:11.1}, {x:16.3,y:23.8}, {x:20,y:24.4},
    {x:20,y:38}, {x:-5,y:38}, {x:-5,y:48}, {x:-20,y:48},
    // Retained screen M2 screw1 world bbox x=-21.99..-18.01,y=-5.676..-1.378.
    // Source Y=worldY+19; notch keeps >=0.5mm nominal screw clearance.
    {x:-20,y:18.8}, {x:-19.4,y:18.2}, {x:-17.8,y:18.2},
    {x:-17.3,y:17.7}, {x:-17.3,y:13.2}, {x:-17.8,y:12.7},
    {x:-19.4,y:12.7}, {x:-20,y:12.1}
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
  piDock: { x: -13.5, y: 21, rotation: 270, side: "bottom" },

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
