// Baseboard outline and board-frame interface datums for the handheld terminal.
//
// FRAME: the board is centred on its own origin. Y+ is toward the Pi's rear
// (USB/Ethernet) edge; Y- is toward the screen pod and the front module deck.
// All values here are BOARD frame; world placement is the dock transform in
// design/handheld_computer (see the README there).
//
// Compact L outline: 15mm GPIO spine and 40x25.5mm front electronics island.
// Defaults for this layout iteration, not a qualified shell mounting pattern.
export const board = {
  width: "40mm", height: "83.5mm", centerY: 6.25,
  outline: [
    {x:-20,y:-35.5}, {x:20,y:-35.5}, {x:20,y:-10},
    {x:-2,y:-10}, {x:-3,y:-7}, {x:-3,y:14}, {x:10,y:14},
    {x:10,y:38}, {x:-5,y:38}, {x:-5,y:48}, {x:-20,y:48},
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

// M2 fixture holes. Reference only: the shell has no matching bosses yet, so
// these are prototype attachment points and do not constrain the enclosure.
export const mountingHoles = [
  { name: "H1", x: -16, y: -13 },
  { name: "H2", x: 16, y: -13 }
];

export function rotationForOpening(
  native: "up" | "right" | "down" | "left",
  target: "up" | "right" | "down" | "left"
) {
  const angle = { right: 0, up: 90, left: 180, down: 270 };
  return (angle[target] - angle[native] + 360) % 360;
}

export const interfaces = {
  // Pi dock. J_PI is on the board underside; the Pi's header rises into it.
  // Standard KiCad socket pin1 origin; intended pad centroid remains(-13.5,21).
  // Stack height and insertion depth still require mechanical validation.
  piDock: { x: -12.23, y: -3.13, rotation: 180, side: "bottom" },

  // Screen FPC. A top-side horizontal ZIF socket, flush with the screen's
  // prior proposed tail approach. Native tail reach is NOT yet verified. Rotated 180deg so the latch
  // reads from the front module side while the pod is off the shell.
  displayFpc: {
    x: 0,
    y: 25.7628506593,
    rotation: rotationForOpening("down", "up"),
    side: "top",
    contactFace: "toward PCB",
    opening: "+Y in board top view"
  },

  // Replaceable front module: top-side 2x4 female socket, mating toward +Z.
  // The shell aperture is a separate mechanical datum, not verified fit.
  // The module's own strain relief must be mechanical, not the header.
  frontModule: { x: -3.81, y: -13.73, rotation: 90, side: "top", mating: "+Z" },

  // Keepout the socket body needs through the deck aperture.
  frontModuleAperture: { width: 54.0, depth: 26.0, centreY: -34.0 }
};
