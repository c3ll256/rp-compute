# Pi4B terminal — 1mm screen front rise

## Goal and scope
User's screen_front_1mm_markup requests the raised screen housing front edge only1mm above the deck, not a thinner base. Preserve two-level style,13deg slope, existing port layout and Pi placement. Editable visual CAD and STEP only; no PCB or final hardware-fit claim.

## Exterior direction
Base85x115x27mm unchanged; housing77mm wide,65mm face length,13deg. Housing Y21.521201483,Z27.3,front body height0.7mm. Total nominal front rise above deckZ27 is1mm including0.3mm seam, measured to the sharp slope/front-plane intersection before the existing0.6mm roundover. Rounded edge falls below this nominal line;1mm is not a uniform shell wall thickness. Overall enclosure height42.467515mm. Bezel Y21.521201483,Z35.310909266,rotation[13,0,0],down5.3mm to follow housing top. Front housing Y=-10.145825723 unchanged. Ivory/orange/charcoal source colours; gray previews do not prove colour matching.

## Port layout and evidence
USB stacks/RJ45 rear, two micro-HDMI/native3.5mm AV right,12x5mm charging proposal leftY=-37,Z12. No front interface. PiUSB-C behind a blind-clearance outer wall, not a working interlock. microSD service after bottom removal and power isolation remains unverified. Pi4B object, base, shell and button unchanged in shape and placement this query.
Exact-model step.parts Pi4B imported asset SHA1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe,version c6113328a5695b976a010a203a90fe86191769bf. Source https://www.step.parts/parts/raspberry_pi_4_model_b ; RAM not mechanically distinguished. Placement[39,-30.5,7],rotation[90,90,0]. Provider license not returned; do not infer the different missing FreeCAD seed's license.

## Model boundary and checks
Five custom exterior solids plus89-solid Pi reference,94valid solids. ISO and right side show a low front edge with unchanged slope and base. No newly reported intersections. Pi/shell pair still exceeds automatic exact-check limit; prior supplemental per-solid STEP check in port-clearance-check.json remains applicable only to this unchanged pair. Nominal rise and unchanged-object comparison recorded in front-rise-check.json. Do not claim full automatic collision clearance or real plug-fit verification.
No LCD, battery, PCB or switch stand-ins, fastening, retention, thermal solution or working interlock. Screen aperture remains empty. Thin front lip requires strength/printing refinement. Lowered screen reduces LCD/FPC clearance; final panel fit is not established. All final hardware interface requirements remain.

## Interfaces and downstream
Preserve compute_mount, sharp_display_fit, usb_access, battery_fit, control_access, gpio_dock and pi_native_ports. Base height, housing front rise/slope and bezel absolute placement need coordinated updates; not auto-linked. GPIO socket/daughterboard stack, charge socket on final PCB, plug/latch/finger access and battery/LCD/cooling remain unverified. No manufacturing-ready claim.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.
