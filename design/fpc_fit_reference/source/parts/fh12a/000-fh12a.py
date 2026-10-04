# Deliberately modeled manufacturer-drawing outer envelope, not a vendor STEP.
# Hirose FH12A catalog p16 (PDF11): A9.1, D9.5, depth6.2, closed2.0, open3.6.
# https://docs.rs-online.com/f450/0900766b813ce339.pdf
# Alignment to C5139870 supplier footprint: front silk datum Y=-4.825,
# rear signal-row pads Y=+1.85. Datum alignment is inferred, not a tolerance.
margin = param("fh12a_envelope_margin", 0.0)
WIDTH_MAX, DEPTH, CLOSED_H, FRONT_Y = 9.5, 6.2, 2.0, -4.825
body = Pos(0, FRONT_Y + DEPTH/2, CLOSED_H/2) * Box(WIDTH_MAX+2*margin, DEPTH+2*margin, CLOSED_H+2*margin)
body.color = Color(0.76,0.73,0.60)
# The outer envelope is deliberately filled: internal contact/slot/latch geometry
# is not certified by the drawing and must not create false clearance passes.
publish("fh12a_reference", body, "FH12A closed envelope", material="nylon")
