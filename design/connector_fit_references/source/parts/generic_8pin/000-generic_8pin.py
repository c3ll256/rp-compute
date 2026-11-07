# Nominal user-specification reference, not a manufacturer STEP.
# KiCad socket local frame: pin1 at(0,0); native y is negative here.
rows = int(param("generic_8pin_positions_per_row", 4))
width = param("generic_8pin_body_width", 5.08)
length = param("generic_8pin_body_length", 10.16)
height = param("generic_8pin_body_height", 5)
tail = param("generic_8pin_tail_length", 3)
pin = param("generic_8pin_square_tail", 0.64)
aperture = param("generic_8pin_aperture", 1.0)
visual_depth = param("generic_8pin_visual_cavity_depth", 3.0)
PITCH_MM = 2.54
center_x = -PITCH_MM/2
center_y = -(rows-1)*PITCH_MM/2
body = Pos(center_x, center_y, height/2)*Box(width, length, height)
openings = [Pos(x,-i*PITCH_MM,height-visual_depth/2+0.005)*Box(aperture,aperture,visual_depth+0.01) for i in range(rows) for x in (0,-PITCH_MM)]
body = body - openings
body.color = srgb("#202126")
tails = [Pos(x,-i*PITCH_MM,-tail/2)*Box(pin,pin,tail) for i in range(rows) for x in (0,-PITCH_MM)]
for metal in tails:
    metal.color = srgb("#b89b42")
reference = Compound(children=[body]+tails)
assert abs(reference.bounding_box().min.Z + tail) < 0.001
assert abs(reference.bounding_box().max.Z - height) < 0.001
publish("generic_8pin", reference, "8 pin nominal socket", material="nylon", role="reference")
