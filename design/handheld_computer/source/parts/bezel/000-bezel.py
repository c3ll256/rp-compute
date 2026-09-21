bezel_width=param('bezel_width',66.0)
bezel_height=param('bezel_height',46.0)
bezel_thickness=param('bezel_thickness',2.3)
bezel_recess=param('bezel_recess',2.2)
bezel_radius=param('bezel_radius',2.5)
bezel_window_clearance=param('bezel_window_clearance',0.3)
bezel_window_radius=param('bezel_window_radius',0.35)
# Sharp LS027B7DH01 active area from product requirements; not a panel model.
ACTIVE_W=58.8
ACTIVE_H=35.28
bezel=Pos(0,0,-bezel_recess)*extrude(RectangleRounded(bezel_width,bezel_height,bezel_radius)-RectangleRounded(ACTIVE_W+2*bezel_window_clearance,ACTIVE_H+2*bezel_window_clearance,bezel_window_radius),amount=bezel_thickness)
bezel.color=Color(0.08,0.09,0.09)
publish('bezel',bezel,'Charcoal aperture bezel')