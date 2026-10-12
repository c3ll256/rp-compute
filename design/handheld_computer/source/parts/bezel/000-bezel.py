bezel_width=param('bezel_width',66.0)
bezel_height=param('bezel_height',49.0)
bezel_thickness=param('bezel_thickness',3.6)
bezel_recess=param('bezel_recess',3.5)
bezel_radius=param('bezel_radius',2.5)
bezel_window_clearance=param('bezel_window_clearance',0.3)
bezel_window_radius=param('bezel_window_radius',0.35)
bezel_pocket_clearance=param('bezel_pocket_clearance',0.3)
bezel_front_lip=param('bezel_front_lip',1.2)
bezel_glass_airgap=param('bezel_glass_airgap',0.2)
bezel_fpc_width=param('bezel_fpc_width',12.0)
bezel_fpc_relief_height=param('bezel_fpc_relief_height',2.3)
# Exact Sharp drawing p26, active-area datum. Pocket is negative installation space,
# NOT an invented LCD model. Orient tail to -Y (front).
ACTIVE_W=58.8
ACTIVE_H=35.28
GLASS_W=62.8
GLASS_H=42.82
GLASS_T=1.64
GLASS_Y=-1.77
bezel=Pos(0,0,-bezel_recess)*extrude(RectangleRounded(bezel_width,bezel_height,bezel_radius)-RectangleRounded(ACTIVE_W+2*bezel_window_clearance,ACTIVE_H+2*bezel_window_clearance,bezel_window_radius),amount=bezel_thickness)
# Rear-loading locator pocket; no press fit or adhesive on polarizer.
seat_z=-bezel_front_lip
bezel-=Pos(0,GLASS_Y,-bezel_recess-1)*extrude(Rectangle(GLASS_W+2*bezel_pocket_clearance,GLASS_H+2*bezel_pocket_clearance),amount=bezel_recess+1+seat_z)
# Open-ended tail relief avoids pinching the glass/FPC bond zone.
bezel-=Pos(0,-bezel_height/2,-bezel_recess+bezel_fpc_relief_height/2)*Box(bezel_fpc_width,6,bezel_fpc_relief_height)
assert bezel_pocket_clearance>0
print('GLASS_TOP_TARGET',seat_z-bezel_glass_airgap,'GLASS_BOTTOM_TARGET',seat_z-bezel_glass_airgap-GLASS_T)
# Back flange traps the inner bezel between housing roof and rear frame.
# The original glass pocket, window and 1mm housing rise are unchanged.
bezel_flange_width=param('bezel_flange_width',70.0)
bezel_flange_depth=param('bezel_flange_depth',47.0)
bezel_flange_thickness=param('bezel_flange_thickness',1.2)
bezel_flange_top=param('bezel_flange_top',-3.0)
bezel_flange_tail_gap=param('bezel_flange_tail_gap',16.0)
flange=Pos(0,GLASS_Y,bezel_flange_top-bezel_flange_thickness)*extrude(Rectangle(bezel_flange_width,bezel_flange_depth)-Rectangle(GLASS_W+2*bezel_pocket_clearance,GLASS_H+2*bezel_pocket_clearance),amount=bezel_flange_thickness)
flange-=Pos(0,-bezel_flange_depth/2+GLASS_Y,bezel_flange_top)*Box(bezel_flange_tail_gap,6,4*bezel_flange_thickness)
bezel_flange_mount_clearance=param('bezel_flange_mount_clearance',0.3)
# Notches affect only new flange; original 66x49 locator is preserved.
for xx in [-20,20]:
 flange-=Pos(xx,-28,bezel_flange_top)*Box(5.4+2*bezel_flange_mount_clearance,6+2*bezel_flange_mount_clearance,4*bezel_flange_thickness)
bezel=bezel.fuse(flange)
assert len(bezel.solids())==1
bezel.color=Color(0.08,0.09,0.09)
publish('bezel',bezel,'LCD locating bezel',role='part')