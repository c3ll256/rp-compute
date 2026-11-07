# cell: base
# cell: base
layout=part('shell')
# Printed flat, outer face down; every feature grows straight up, so no supports.
# Closure only; Pi is carried by the separate upper-shell carrier.
base_width=layout.case_width
base_depth=param('base_depth',115.0)
base_corner=param('base_corner',9.0)
base_thickness=param('base_thickness',2.4)
base_edge_radius=param('base_edge_radius',0.7)
base=extrude(RectangleRounded(base_width,base_depth,base_corner),amount=base_thickness)
base=fillet(base.edges().filter_by(Plane.XY),base_edge_radius)

from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole

# Shared bottom-cover attachment datums (same names and values as the shell columns).
base_mount_front_x=param('base_mount_front_x',32.0)
base_mount_front_y=param('base_mount_front_y',-48.0)
base_mount_left_front_x=param('base_mount_left_front_x',-32.0)
base_mount_left_front_y=param('base_mount_left_front_y',-15.0)
base_mount_left_rear_x=param('base_mount_left_rear_x',-32.0)
base_mount_left_rear_y=param('base_mount_left_rear_y',51.5)
base_mount_right_mid_x=param('base_mount_right_mid_x',32.0)
base_mount_right_mid_y=param('base_mount_right_mid_y',-35.0)
base_mount_axes=[(base_mount_left_front_x,base_mount_left_front_y),(base_mount_front_x,base_mount_front_y),(base_mount_left_rear_x,base_mount_left_rear_y),(base_mount_right_mid_x,base_mount_right_mid_y)]

# Seats share exactly the shell's source-owned joint tooling.
# Shallow inside rim registers the shell edge below the Pi's lowest connector Z=3.45.
base_rim_height=param('base_rim_height',0.8)
base_rim_thickness=param('base_rim_thickness',1.2)
base_rim_clearance=param('base_rim_clearance',0.3)
shell_wall=param('shell_wall',2.4)
shell_base_pad_width=param('shell_base_pad_width',8.0)
inset=shell_wall+base_rim_clearance
rim_outer=Pos(0,0,base_thickness)*extrude(RectangleRounded(base_width-2*inset,base_depth-2*inset,base_corner-inset),amount=base_rim_height)
rim_inner=Pos(0,0,base_thickness-0.1)*extrude(RectangleRounded(base_width-2*(inset+base_rim_thickness),base_depth-2*(inset+base_rim_thickness),base_corner-inset-base_rim_thickness),amount=base_rim_height+0.2)
rim=rim_outer-rim_inner
for xx,yy in base_mount_axes:
 sx=1 if xx>0 else -1
 tip=abs(xx)-shell_base_pad_width/2-base_rim_clearance
 root=base_width/2
 rim=rim-(Pos(sx*(tip+root)/2,yy,base_thickness+base_rim_height/2)*Box(root-tip,shell_base_pad_width+2*base_rim_clearance,base_rim_height+0.2))
base=base+rim

# Imported Pi PCB underside datum, retained for port-filler corner relief only.
PI_BOARD_BOTTOM_Z=5.3+getattr(layout,'pi_stack_lift',0.0)

# One continuous rear sill closes the shared lower-edge aperture.
# All opening limits are owned by the shell, so both pieces track together.
base_port_filler_clearance=param('base_port_filler_clearance',0.25)
wall_ring=extrude(RectangleRounded(base_width,base_depth,base_corner)-RectangleRounded(base_width-2*shell_wall,base_depth-2*shell_wall,base_corner-shell_wall),amount=40)
# The Pi's rear-right board corner reaches into the rounded wall (same relief as the
# shell); fillers stop below the board there. Fixed by the imported Pi placement.
PI_REAR_CORNER_RELIEF=(35.5+layout.pi_offset_x,39.5+layout.pi_offset_x,51.3,55.3)
rx0,rx1,ry0,ry1=PI_REAR_CORNER_RELIEF
corner_relief=Pos((rx0+rx1)/2,(ry0+ry1)/2,PI_BOARD_BOTTOM_Z-0.2+5)*Box(rx1-rx0,ry1-ry0,10)
sill=layout.rear_window_sill
z0=base_thickness-base_edge_radius
tongue=wall_ring & (Pos(layout.rear_window_center,base_depth/2,(z0+sill)/2)*Box(layout.rear_window_width-2*base_port_filler_clearance,4*shell_wall,sill-z0))
base=base+(tongue-corner_relief)


# Sliding pockets brace the separator tips without preloading or snap hooks.
base_rear_divider_clearance=param('base_rear_divider_clearance',0.25)
base_rear_divider_floor_clearance=param('base_rear_divider_floor_clearance',0.3)
base_rear_divider_pocket_floor=layout.rear_divider_tip_z-base_rear_divider_floor_clearance
assert base_rear_divider_pocket_floor>base_thickness
for xx in layout.rear_divider_x:
 pocket=Pos(xx,base_depth/2,(base_rear_divider_pocket_floor+layout.rear_window_sill+0.2)/2)*Box(
  layout.rear_divider_width+2*base_rear_divider_clearance,
  4*shell_wall,
  layout.rear_window_sill+0.2-base_rear_divider_pocket_floor)
 base=base-pocket
print('REAR_DIVIDER_POCKETS',dict(side_clearance=base_rear_divider_clearance,floor_z=base_rear_divider_pocket_floor,tip_floor_clearance=base_rear_divider_floor_clearance))

# A continuous L-shaped internal reinforcement carries the free rear-right corner
# toward the existing right-mid and left-rear screw columns. The outer bottom
# face stays flat on the print bed; no new fasteners or cantilever clips.
base_corner_rail_width=param('base_corner_rail_width',1.5)
base_corner_rail_height=param('base_corner_rail_height',2.4)
base_rear_web_height=param('base_rear_web_height',0.65)
base_rear_web_depth=param('base_rear_web_depth',11.0)
rail_start=layout.base_mount_right_mid_y+shell_base_pad_width/2+base_rim_clearance
rail_end=base_depth/2-base_corner
rail_outer=base_width/2-inset
reinforcement_floor=base_thickness-0.2
reinforcement_clip=extrude(RectangleRounded(base_width-2*inset,base_depth-2*inset,base_corner-inset),amount=base_thickness+base_corner_rail_height)
corner_rail=Pos(rail_outer-base_corner_rail_width/2,(rail_start+rail_end)/2,(reinforcement_floor+base_thickness+base_corner_rail_height)/2)*Box(base_corner_rail_width,rail_end-rail_start,base_corner_rail_height+0.2)
corner_rail=corner_rail & reinforcement_clip
web_rear=base_depth/2-inset
rear_web=Pos(0,web_rear-base_rear_web_depth/2,(reinforcement_floor+base_thickness+base_rear_web_height)/2)*Box(base_width,base_rear_web_depth,base_rear_web_height+0.2)
rear_web=rear_web & reinforcement_clip
# Register around, rather than on, existing receiving columns.
for xx,yy in layout.base_mount_axes:
 clearance=Pos(xx,yy,base_thickness+base_corner_rail_height/2)*Box(shell_base_pad_width+2*base_rim_clearance,shell_base_pad_width+2*base_rim_clearance,base_corner_rail_height+0.2)
 corner_rail-=clearance
 rear_web-=clearance
base=base+corner_rail+rear_web
assert base.is_valid
print('CORNER_STIFFENING',dict(rail_top=base_thickness+base_corner_rail_height,rear_web_top=base_thickness+base_rear_web_height,rail_start_y=rail_start,rail_end_y=rail_end))

# Cover screws into the shell columns.
for seat in layout.base_mount_seats:
 base=base-seat

assert len(base.solids())==1, ('base',[round(s.volume,1) for s in base.solids()])

base.color=Color(0.88,0.86,0.79)
publish('base',base,'Bottom closure',material='pla',role='part')
