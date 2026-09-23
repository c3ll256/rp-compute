export const board = {
  width: "70mm",
  height: "104mm",
};

// Provisional upper-board coordinates from the committed Pi/FPC CAD reference.
// These are placement targets; the single-board stack is not yet fit-qualified.
export const interfaces = {
  piDock: { x: -13.5, y: 15.2, rotation: 90, side: "bottom" as const },
  // The retained pod reference mounts this bottom-contact connector below a
  // 13-degree-sloped board datum. Bottom/0 is a planar fit hypothesis only;
  // actual tail length and board stack must be measured before release.
  displayFpc: { x: 0, y: 6.7, rotation: 0, side: "bottom" as const },
  frontModule: { x: 0, y: -34, rotation: 0, side: "top" as const },
};

export const placement = {
  origin: { x: 0, y: 0 },
};

export const OPENING_ROTATION_DEG = {
  up: 0,
  left: 90,
  down: 180,
  right: 270,
} as const;

export type OpeningDirection = keyof typeof OPENING_ROTATION_DEG;

/** Rotation (deg) to apply when a footprint's native opening differs from the target opening. */
export function rotationForOpening(
  nativeOpening: OpeningDirection,
  targetOpening: OpeningDirection,
): number {
  return (
    (OPENING_ROTATION_DEG[targetOpening] - OPENING_ROTATION_DEG[nativeOpening] + 360) % 360
  );
}

export type XY = { x: number; y: number };
