# Pi4B terminal — shallow screen styling

## Goal and scope
Follow correction_reference_1/2 for two-level form and shallow_angle_markup for the user's request to reduce screen slope. Current13deg is an agent-selected approximation of the red-line direction, not an exact user-specified dimension. Deliver visual CAD and STEP only; no PCB or final hardware-fit claim.

## Exterior direction
Low horizontal ivory base with raised orange shallow screen housing at rear and exposed flat front deck. Base85x115mm,height20mm; housing77mm wide,65mm face length,13deg from horizontal,6mm nominal front height above housing base. Hold the front housing edge at Y=-10.145825723 and housing baseZ20.3; preserve face dimensions. Housing centerY21.521201483 lets its rear extend7.0424mm farther back as the angle decreases. Overall height about40.77mm, below the provisional60mm envelope cap. Single side power control, front shallow cosmetic groove and charge opening unchanged. Colours remain ivory/orange/charcoal; Workbench gray views do not prove a colour match.

## Model boundary
Five custom exterior parts only, no invented Pi, LCD, battery, PCB or switch solids. Screen opening is an aperture, not a physical display model. No fasteners, snaps, retention, thermal solution or working interlock; unfastened visual study. Lowering screen reduces internal room, so final LCD/FPC clearance needs real geometry later.

## Interfaces and downstream
All final compute_mount, sharp_display_fit, usb_access, battery_fit, control_access, gpio_dock and pi_native_ports requirements remain. No release PCB exists. Side control and charge aperture are proposals. Absolute housing and bezel placements were recomputed together; future changes to angle, screen-face length or front height must repeat this calculation. Bezel placement=[0,21.521201483,33.610909266], rotation=[13,0,0].

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.
