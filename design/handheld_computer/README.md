# Pi4B terminal — raised compact PCB and upper-shell mounting

The current compact PCB release e78739c43849def0c023a90a7fb0cc0085085dc75e25b5e5d1f3f54d51e985fa is imported and placed at[-100,81,21.8]mm, zero rotation. This is the new routed board, not the preceding17.5mm assembly. Its envelope is40x83.5mm, area2284.54mm², finished thickness0.8mm, four copper layers at1oz. The Pi, glass locator,13degree screen angle,1mm front rise and exterior shell dimensions are retained.

## Connectors and attachment

User requested taller GPIO, lower8pin and a horizontal FPC entrance toward down/front(-Y in board top view). J_PI is Samtec ESQ-120-12-G-D, housing11.05mm/tail2.29mm; J_MOD is HLE-104-02-G-DV, housing3.66mm. Nominal Pi insertion is4.75mm at the official Pi datum, inside3.68..6.35mm. The retained third-party Pi reference has1.5mm taller pins; its STEP-derived6.335mm engagement has only0.015mm upper allowance and is not a tolerance-qualified assembly basis.

Two ISO4762 M2x4 kit joints at worldX±16,Y-32 fasten the PCB to2mm thick,6mm wide sidewall-rooted beams in the upper shell. A rear shelf/guide atX-20,Y24 supports the spine with0.3mm clearance. The lower cover and removable70x37mm front module blank do not carry PCB mounting loads. The blank has11.2x6.2mm socket access, local beam/lead relief and3mm screw-tip clearance holes. Its beam pockets leave1.9mm minimum roof; their vertical gap over the beams is0.5mm.

## Verified geometry and PCB

Current per-solid OCC checks find no PCB substrate/component volume intersections with shell, blank, fascia, retainer, checked mounting screws, bezel, cushions, Pi or nominal glass probe. The retained screen screw has1.292813mm substrate clearance. Ordinary top components have at least1.555001mm geometric air clearance; the buffer/front-frame pocket was enlarged to achieve this. HLE top isZ26.254999,0.745001mm below deckZ27. PCB DRC has0errors/0unconnected,40physical GPIO pin locations passed. This is geometry and routing validation, not a temperature or airflow test. Existing side-button/shell overlap15.473387mm³/0.2744mm remains outside this PCB connector correction and is not a qualified button assembly.

## FPC conflict still open

J_LCD remains the current FH12-10S-0.5SH(55) bottom-contact horizontal socket at worldorigin[0,9.8], rotation0, entrance toward-Y. The retained source=user requirement specifies bottom contacts. Sharp p26 recommends folding toward the panel back; after the return fold, the exposed contacts face upward. This needs a horizontal top-contact socket such as FH12A-10S-0.5SH(55), or a reworked installation. The user has been asked to choose; neither the requirement nor this part is substituted yet. Tail13.7±0.5mm is an authorized estimate. Raised board removes the earlier optimistic height deficit but does not prove reach, contact face, pin1 or insertion. The old tilted-return negative channel remains historical clearance only and is not a qualified current route.

## Model evidence and limits

The exact released PCB brings real supplier FPC/IC/passive bodies. ESQ and HLE are deliberately modeled nominal manufacturer-drawing fit references because the supplier ESQ had wrong tail lengths and no HLE STEP was available. Their reference cavities omit internal contact geometry. Sources are Samtec esq_th.pdf and HLE series print; source/provenance and tool-generated models accompany the board. Sharp glass62.8x42.82x1.64mm is a drawing-based negative clearance probe. STEP substrate0.71mm excludes finished-stack details; manufacturing uses0.8mm. Physical connector mating, tail insertion, PLA strength/thread life, cushioning stress and temperatures remain untested.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange display housing/button, charcoal bezel. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.

The rear-loading locator pocket is supplemented by the retained rear frame as described above. Proposed later assembly is screen into removed pod from rear, fit low-stress support/retainer, connect tail with full latch access, then attach pod. Do not suspend LCD by FPC, stick adhesive on polarizer or bend at glass edge. Enlarged interior deck opening and thin front regions require strength checks. Failed printed-screw-kit candidates committed no geometry; retain their failure record rather than substituting hand-modeled screw joints.


### Current prototype update
The preceding making notes are retained historical records: the statements about no rear retainer/fasteners and entry-only FPC describe the previous revision and are superseded by this query's geometry above. There has still been no physical print or assembly test.
Default PLA is a CAD prototype assumption; calibrate M2 holes and verify local thin-wall strength. Print screw axes upright where possible; sloping housing and mounting receivers may need supports. Soft pads are die-cut, not FDM parts. Assemble glass/pads/frame on the removed inverted pod, alternate the four screws only to their hard stops, shape the tail once with a radius guide, insert its stiffener and close the latch before pod installation. Remove Pi for tool access if necessary. Verify pad chemistry/compression and display image uniformity before powered integration. The future supported connector board is not part of this delivery.

Front module making update: print the blank separately with the tongue facing upward if possible, calibrate its 0.3mm lateral seat clearance and the four kit M2 holes, then verify screw head access and repeated removal before user-facing use. Turn all power off and isolate the battery before releasing the four screws and unplugging a future module harness. There is no printed or tested electrical harness in this CAD handoff.

Current PCB review addendum: historical making instructions above do not validate the new horizontal tail route. Do not treat the current assembly as fitted until the height and contact-direction conflict is resolved.


### Raised board assembly update

The prior no-fastener/17.5mm/socket-height-conflict notes above are historical. Current PCB is mounted to the upper-shell beams and rear guide atZ21.8 with higher ESQ and lower HLE. Fit the board and start both M2x4 screws loosely before tightening to contact; the removable module blank is not its support. Keep screw-tip holes clear. Assemble the screen pod off the case for latch access. Do not force or repeatedly bend the tail; current bottom-contact installation remains unresolved, so do not treat this draft as a powered or fully fitted screen assembly. The1.555mm air gap is not a cooling-performance claim.
