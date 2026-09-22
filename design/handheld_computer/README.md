# Pi4B terminal — 1mm front rise, screen installation space

## Goal and scope
Active user request: 按现在1mm前沿的造型继续完善屏幕安装和FPC空间. CAD only, no PCB. Partial delivery: rear-loading glass locator and tail entry relief implemented; mechanical retention and full FPC routing NOT finished because printed screw joint candidates failed.

## Exterior direction
Base85x115x27mm, housing77mm wide/65mm face at13deg unchanged. Housing[0,21.521201483,27.3], front body height0.7mm. Nominal front rise1mm includes0.3mm seam, measured at theoretical sharp slope/front-plane intersection before0.6mm roundover; not uniform wall thickness. Overall height42.467515mm. Bezel origin[0,21.521201483,35.310909266],rotation[13,0,0] unchanged. Its depth now49mm, thickness3.6/recess3.5, preserving top elevation. Glass negative pocket63.4x43.42, centerY=-1.77 in active-area frame. Nominal side clearance0.3.12mm tail exit,14x10x5mm housing underside relief;1.5mm remaining local roof. Deck interior opening68x54mm atY21.5 clears inward bezel extension.

## Port layout and evidence
USB/RJ45 rear, two micro-HDMI/nativeAV right, charging left. No front port. PiUSB-C blind clearance is NOT a working interlock; microSD service after bottom removal/power isolation remains unverified. Pi placement[39,-30.5,7],rotation[90,90,0] unchanged; base, button and all external port shapes unchanged. Shell interior opening alone changed.
Pi asset SHA1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe, step.parts version c6113328a5695b976a010a203a90fe86191769bf; provider license not returned. Exact Sharp LS027B7DH01 p5/26 governs the negative pocket; no matching LCD STEP found. FH12 family model researched but not imported/positioned, suffix not certified by that asset.

## Model boundary and checks
Five custom solids plus89-solid Pi reference,94 valid solids. Isolated underside and ISO inspected; automaticPi/shell test exceeds89 candidate limit. Fresh supplementary per-solid OCC test found no overlap>1e-5mm³, recorded in screen-space-check.json. This is NOT whole-hardware clearance: LCD, FPC, connector, PCB and battery are absent. No rear retention frame, standoffs or fasteners were successfully generated. Current bezel is only a locator, cannot retain glass. FPC relief is only entry space, not validated bend/latch/assembly path. Full tolerance/driver-light-shielding/polarizer-pressure/print-strength tests pending. See screen-installation.md and screen-part-plan.json. No final hardware-fit or manufacturing claim.

## Interfaces and downstream
Preserve compute_mount,sharp_display_fit,usb_access,battery_fit,control_access,gpio_dock,pi_native_ports. Parameters and absolute placements require coordinated edits, not auto-linked. Finish rear support/retention and complete FPC endpoint/open-latch envelope before treating the display installation as complete. GPIO stack, battery, cooling, bottom/pod fixation and working interlock remain outstanding. No PCB this query.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.

Rear-loading locator pocket is now present but cannot hold the screen by itself. Proposed later assembly is screen into removed pod from rear, fit low-stress support/retainer, connect tail with full latch access, then attach pod. Do not suspend LCD by FPC, stick adhesive on polarizer or bend at glass edge. Enlarged interior deck opening and thin front regions require strength checks. Failed printed-screw-kit candidates committed no geometry; retain their failure record rather than substituting hand-modeled screw joints.
