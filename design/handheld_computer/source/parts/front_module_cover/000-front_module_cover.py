# Flat removable cover. Shared kit cuts and hole datums are owned by shell.
layout=part('shell')
front_module_width=param('front_module_width',70.0)
front_module_depth=param('front_module_depth',37.0)
front_module_blank_corner=param('front_module_blank_corner',4.0)
front_module_blank_edge_chamfer=param('front_module_blank_edge_chamfer',0.4)
t=layout.front_module_blank_thickness
cover=Pos(0,0,-t)*extrude(RectangleRounded(front_module_width,front_module_depth,front_module_blank_corner),amount=t)
cover=chamfer(cover.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1],front_module_blank_edge_chamfer)
MODULE_WORLD=Pos(0,layout.front_module_y,layout.case_top_center+t)
for seat in layout.front_module_seats: cover-=seat.moved(MODULE_WORLD.inverse())
assert len(cover.solids())==1 and cover.is_valid
assert abs(cover.bounding_box().min.Z+t)<1e-6
cover.color=srgb('#84898e')
publish('front_module_blank',cover,'Independent expansion cover',material='pla',role='part')