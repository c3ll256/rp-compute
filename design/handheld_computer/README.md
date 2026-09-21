# Pi4B terminal — styling first

## Goal and scope
User explicitly requests CAD before PCB because appearance matters. Deliver an editable visual study and STEP, not a production enclosure. Reference the two uploaded photos for colour blocking and compact rounded character only. Keep the simplified power/display-only product: no keyboard, trackpad or navigation bank added.

## Exterior direction
85mm wide,115mm deep,40mm maximum target; shallow 8-degree rising top, warm light body, orange large display surround, dark narrow inner bezel. One power button on the lower right of the top. Understated perimeter seam, separate bottom cover, rear and right side service panels, front charging opening. Interface positions are styling proposals, NOT native Pi connector coordinates. Rear/right panels are intentionally blank until actual Pi orientation is fixed. Colour fields may render with automatic part colours; labels define intended CMF.

## Model boundary
Only custom exterior parts are modeled. No placeholder Pi, battery, purchased LCD, cooler, switch or PCB solids. Display aperture follows stored Sharp active-area dimensions with clearance; this is not glass retention or FPC-fit verification. No screw joints, standoffs, snap-fits or functioning interlock modeled. Blank service panels are not functioning port covers. All final product requirements remain: cold-plug GPIO, independent Pi fixation, native ports exposed except interlocked PiUSB-C, battery clearance, airflow and controlled shutdown.

## Interfaces and downstream
sharp_display_fit: aperture styling only. control_access: one cosmetic cap and hole, switch mechanics deferred. usb_access: proposed baseboard charging opening. compute_mount/gpio_dock/pi_native_ports/battery_fit: deferred physical integration, not accepted. PCB must be designed within a future validated internal allocation; no fabricated PCB source/release exists yet. Keep the editable envelope so later actual stack or battery can resize without losing the styling intent.

## Making and assembly
Visual study only: do not order/print as a working enclosure. Walls nominal2.4mm, detachable bottom with a visual seam; no retention features or fasteners yet. Parts may sit with intentional assembly clearances and are not fixed together. Material colours: ivory shell/lid, orange fascia/button, charcoal bezel/service panels. No physical assembly, support strategy, print calibration or fit test has been performed. Powered use and battery installation are not authorized by this CAD deliverable.
