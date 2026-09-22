# Pi4B terminal — rear and side ports

## Goal and scope
User requests all external cable ports at rear or sides, with real Pi USB/RJ45 space. Preserve low horizontal base, shallow raised rear screen and open front deck from correction_reference_1/2 and shallow_angle_markup. Current13deg is a disclosed default, not a measured user angle. Deliver editable visual CAD and STEP; no PCB or final hardware-fit claim.

## Exterior direction
Base85x115mm raised from20 to27mm to accommodate imported Pi4B connector geometry and underside. Overall enclosure height47.767515mm. Housing77mm wide,65mm face length,13deg from horizontal,6mm nominal front height above housing base. Housing Y21.521201483,Z27.3; bezel Y21.521201483,Z40.610909266,rotation[13,0,0]. Front housing edge Y=-10.145825723 unchanged. Single right-side power button and shallow cosmetic deck groove retained. Front charging aperture removed. Ivory/orange/charcoal source colours; gray previews do not prove a colour match.

## Port layout and evidence
USB stacks and RJ45 rear; two micro-HDMI and native3.5mm AV right;12x5mm charging proposal left atY=-37,Z12. Pi ownUSB-C has blind internal clearance and continuous external wall; this is NOT a working interlock. microSD service requires bottom removal with all power isolated; removal path and hand access not yet verified. No addedUSB-A or hub, no added audio function.
Exact-model step.parts Raspberry Pi4 Model B asset imported as pi4b with checksum1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe, source version c6113328a5695b976a010a203a90fe86191769bf. Asset placement[39,-30.5,7],rotation[90,90,0]; worldX=assetZ+39,Y=assetX-30.5,Z=assetY+7. RAM not geometrically distinguished. Source https://www.step.parts/parts/raspberry_pi_4_model_b . Bundled FreeCAD seed missing; no fake board geometry substituted. Provider license not returned, do not infer another asset's license.

## Model boundary and checks
Five custom exterior solids plus89-solid Pi reference. Kernel reports valid94solid assembly. Workbench Pi/shell pair exceeds automatic exact-check limit; supplemental read-only per-solid OCC check on committed STEP found no intersections above1e-5mm3 (port-clearance-check.json). Other object pairs had no reported interference. This verifies static modeled solids only, not insertion, plugs, RJ45 latch/finger room, manufacturing tolerances or load-bearing strength. Rear narrow webs and slot bridges need manufacturing refinement.
No LCD, battery, PCB or switch stand-ins. LCD window remains empty; no fastening, snaps, retention, thermal solution or working interlock. GPIO socket stack remains unverified and could move this layout. Charge socket not yet positioned on real PCB. All final product interface requirements remain.

## Interfaces and downstream
Preserve compute_mount, sharp_display_fit, usb_access, battery_fit, control_access, gpio_dock and pi_native_ports requirements. No release PCB exists. Changing base height/width, board pose or screen angle requires recalculating absolute object placements and aperture coordinates together; they are not auto-linked. Opening decisions remain editable parameters. No production/print-ready claim.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.
