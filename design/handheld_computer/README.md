# Pi4B terminal — retained screen and replaceable front GPIO module

## Goal and scope
Current user request: retain the screen locating slot, 1mm front rise, rear screen retainer, FPC path and tightened I/O while making the marked front deck user-replaceable for future GPIO function modules.
This CAD delivery adds a removable blank and shared mount datum. It preserves the rear screen retainer, bezel rear flange, native-tail negative route, connector reference and port apertures. The GPIO board connector and electrical circuit remain a separate PCB implementation.

## Preserved exterior and locator
Base85x115x27mm, housing77mm wide/65mm face at13deg. Housing origin[0,21.521201483,27.3], front body height0.7mm. Nominal front rise1mm includes0.3mm seam, at theoretical sharp slope/front-plane intersection before roundover. Overall height42.467515mm unchanged. Bezel origin[0,21.521201483,35.310909266],rotation[13,0,0], original outer66x49,thickness3.6/recess3.5, window,63.4x43.42 glass locator and Y=-1.77 offset unchanged.
Bezel adds an under-roof70x47x1.2mm flange at normalZ=-4.2..-3.0. Existing pocket is not resized. Shell opening is71x54mm centeredY21.5 with four concealed mount wells; base/button/Pi placements unchanged. The former front cosmetic groove is replaced by the module seat described below. Exterior port aperture dimensions are updated below, with centers retained.

## Tightened I/O apertures
Rear RJ45 is 17x15mm, middle USB stack 15x17mm and right USB stack 16x18mm. The two right-side micro-HDMI apertures are each 8.5x5.2mm, the AV aperture is diameter8.5mm, and the left charging aperture is 10.5x4.4mm. Centers are unchanged. The Pi4B STEP rear board corner now has an internal blind relief while the outer right USB aperture remains tight; at least 2.2mm rear outer material remains there. The committed final build passes supplementary per-solid exact intersection checks against all89 Pi solids. This does not verify molded plug bodies, latch/finger access, charging socket placement or printed tolerances; test those on a prototype before ordering a working enclosure.

## Replaceable front GPIO module
The marked front deck now has a flush 70x37x1.4mm removable blank at X0,Y-34,Z25.6..27, a 70.3x37.3mm locating seat 1.4mm deep, and a true 54x26mm access aperture. A 0.6mm underside tongue has nominal 0.3mm lateral clearance. Four top-access kit-generated M2x4 self-forming screw joints use X+-31,Y-49/-19mm. They hold the blank in the shell rather than relying on a GPIO connector for mechanical strength. This is a shared prototype datum for future custom faceplates; the JST GHD electrical interface is specified in product/front-module-interface.md but has no placed board or harness here. Power must be removed and the battery isolated before swapping modules; printed thread life and module load have not been tested.

## Retention and FPC
Four ISO4762 M2x5 underside joints, X=+-20,Y=-28/+25.5 in screen plane,2mm through thickness,3mm selected engagement. Printed-screw-joint-v1 generates holes and hardware. Receiver faces and retainer ears are hard stops; glass is not in screw clamping stack. Retainer supports nominal0.20mm front and1.00mm rear nonadhesive die-cut cushions. Pad material/compression, polarizer stress and print strength are NOT verified. Use low-outgassing non-chloroprene compatible material, no adhesive on polarizer; nominal pads are not a qualified supplier product.
Native FPC starts atY=-23.18,Z=-2.23;1mm straight,180deg back fold, innerR1.35, centerR1.5. Unfolded bend interval1..5.712389mm is within Sharp0.8..6.0mm; minimumR0.45 and max3 bend cycles retained.11mm-wide negative route includes0.25mm surface clearance and ends atY=-16.192389,Z=-5.23, with4mm straight stiffener and3.4mm nominal insertion.
IMPORTANT:13.7mm free-tail total is a disclosed layout estimate from drawing proportions, not an exact toleranced Sharp dimension. Physical tail length, actual insertion stop and pin1 must be verified before freezing the board interface. Thus the route is complete as a CAD target, not certified physical fit.
FH12 bottom-contact identity retained. Invert reference around localY so folded copper still faces the future PCB. Connector worldposition[0,6.7628506593,27.254517899],XYZ[-167,0,-180]; local board datumZ=-4.53. Asset includes6.4mm full terminal depth.4.8mm open latch plus clearance reserved for operation on removed pod. No supporting PCB or connector fixation is modeled. The imported model proves family geometry only, not(55)suffix.
See screen-installation.md and fpc-route.json for full path, assembly order and remaining physical checks.

## Evidence and model boundary
Sharp LS027B7DH01 original PDF pp5,26; Hirose exact(55) drawing pp1,5. Panel model search previously found no exact STEP; drawing-based negative envelopes are used for clearance without publishing a fake panel/FPC.
Pi assetSHA1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe remains unchanged. Connector family assetSHAe9d0b14513dfc84f1e9be9e3b1d0c5c710fa12b2abdcae6ad9b5880e4097a0e9 from step.parts/KiCad, sourceversionc6113328a5695b976a010a203a90fe86191769bf. Source licenses not inferred.
Workbench overlap observations and supplementary exact-export checks are recorded in screen-space-check.json. Only exact final export is the handoff; physical tests have not occurred.

## Out of scope
Pi attachment, GPIO docking stack, battery size/compartment, cooling, pod/base overall fasteners, working USB-C interlock and complete electrical implementation remain outstanding. PiUSB-C blind wall is not an electrical interlock. This query does not generate a PCB. Do not judge this screen-only prototype as a complete production terminal.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.

The rear-loading locator pocket is supplemented by the retained rear frame as described above. Proposed later assembly is screen into removed pod from rear, fit low-stress support/retainer, connect tail with full latch access, then attach pod. Do not suspend LCD by FPC, stick adhesive on polarizer or bend at glass edge. Enlarged interior deck opening and thin front regions require strength checks. Failed printed-screw-kit candidates committed no geometry; retain their failure record rather than substituting hand-modeled screw joints.


### Current prototype update
The preceding making notes are retained historical records: the statements about no rear retainer/fasteners and entry-only FPC describe the previous revision and are superseded by this query's geometry above. There has still been no physical print or assembly test.
Default PLA is a CAD prototype assumption; calibrate M2 holes and verify local thin-wall strength. Print screw axes upright where possible; sloping housing and mounting receivers may need supports. Soft pads are die-cut, not FDM parts. Assemble glass/pads/frame on the removed inverted pod, alternate the four screws only to their hard stops, shape the tail once with a radius guide, insert its stiffener and close the latch before pod installation. Remove Pi for tool access if necessary. Verify pad chemistry/compression and display image uniformity before powered integration. The future supported connector board is not part of this delivery.

Front module making update: print the blank separately with the tongue facing upward if possible, calibrate its 0.3mm lateral seat clearance and the four kit M2 holes, then verify screw head access and repeated removal before user-facing use. Turn all power off and isolate the battery before releasing the four screws and unplugging a future module harness. There is no printed or tested electrical harness in this CAD handoff.
