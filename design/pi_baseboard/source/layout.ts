export const board = {
  width: "110mm",
  height: "72mm",
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
