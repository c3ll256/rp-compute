# Pi4B terminal — corrected styling

## Goal and scope
Correct the rejected single shallow wedge using the user's two new screenshots, correction_reference_1 and correction_reference_2 in product/contract.json. Deliver revised editable visual CAD and STEP only. Do not begin PCB. No claim of final Pi/battery/LCD fit.

## Exterior direction
The key is a low horizontal ivory base with an independently raised orange sloping display housing at the rear and exposed flat front deck. Not a tablet or a single sloped slab. Default base footprint85x115mm, height20mm; orange housing width77mm, face depth65mm, slope30deg from horizontal, rounded but defined edges. Front deck has one shallow horizontal cosmetic groove. Single existing power control moves to right side; no inferred speaker, keyboard, navigation array or extra ports. All numerical proportions are adjustable defaults, not measured photo dimensions. Target overall height60mm replaces the agent's old40mm styling target. Bezel aperture retains Sharp active-area clearance. Colour fields may display grey in Workbench; do not claim a photoreal colour match.

## Model boundary
Only custom exterior shells, bottom and bezel/cap are modeled. No invented Pi, LCD, battery, PCB or switch solids. Rear/right blank panel objects are removed in favour of clean low-base sidewalls; actual native ports must be cut during real integration. Current open screen window is an aperture, not a missing claimed LCD asset. No screws, standoffs, snaps, retention or working interlock. Unfastened visual assembly only.

## Interfaces and downstream
All final compute_mount, sharp_display_fit, usb_access, battery_fit, control_access, gpio_dock and pi_native_ports requirements remain. Raised housing/FPC routing and side-button transfer need real layout. Charging aperture is provisional. No release PCB exists. Do not freeze board outline from the hollow shell. Absolute placements must be recomputed when shell height, screen angle or housing depth changes.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.
