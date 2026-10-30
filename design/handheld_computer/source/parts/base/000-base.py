# cell: base
layout=part('shell')
# Printed flat, outer face down; every feature grows straight up, so no supports.
# The Pi 4 + P165-B stack is screwed onto four posts here first; the upper shell then
# drops straight down over it, so nothing on the shell has to be bent to fit the Pi.
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

# Pi 4 support posts on the official 49 x 58 hole pattern at the imported board placement.
# The board underside sits at Z5.3 (board top 7.1 minus the 1.8 board stack).
PI_HOLE_X=tuple(x+layout.pi_offset_x for x in (-13.5,35.5))
PI_HOLE_Y=(-27.0,31.0)
PI_BOARD_BOTTOM_Z=5.3
PI_PCB_T=1.8
base_pi_post_diameter=param('base_pi_post_diameter',5.6)
for xx in PI_HOLE_X:
 for yy in PI_HOLE_Y:
  base+=Pos(xx,yy,(base_thickness-0.2+PI_BOARD_BOTTOM_Z)/2)*Cylinder(base_pi_post_diameter/2,PI_BOARD_BOTTOM_Z-base_thickness+0.2)

# Rear port fillers: tongues in the wall plane fill the open-bottom slots of the shell's
# USB/RJ45 windows up to the original window sill, so the closed case looks unchanged.
shell_rj45_x=layout.shell_rj45_x
shell_rj45_z=param('shell_rj45_z',14.0)
shell_rj45_width=param('shell_rj45_width',17.0)
shell_rj45_height=param('shell_rj45_height',15.0)
shell_usb_mid_x=layout.shell_usb_mid_x
shell_usb_mid_z=param('shell_usb_mid_z',15.0)
shell_usb_mid_width=param('shell_usb_mid_width',15.0)
shell_usb_mid_height=param('shell_usb_mid_height',17.0)
shell_usb_right_x=layout.shell_usb_right_x
shell_usb_right_z=param('shell_usb_right_z',14.5)
shell_usb_right_width=param('shell_usb_right_width',16.0)
shell_usb_right_height=param('shell_usb_right_height',18.0)
base_port_filler_clearance=param('base_port_filler_clearance',0.25)
wall_ring=extrude(RectangleRounded(base_width,base_depth,base_corner)-RectangleRounded(base_width-2*shell_wall,base_depth-2*shell_wall,base_corner-shell_wall),amount=40)
# The Pi's rear-right board corner reaches into the rounded wall (same relief as the
# shell); fillers stop below the board there. Fixed by the imported Pi placement.
PI_REAR_CORNER_RELIEF=(35.5+layout.pi_offset_x,39.5+layout.pi_offset_x,51.3,55.3)
rx0,rx1,ry0,ry1=PI_REAR_CORNER_RELIEF
corner_relief=Pos((rx0+rx1)/2,(ry0+ry1)/2,PI_BOARD_BOTTOM_Z-0.2+5)*Box(rx1-rx0,ry1-ry0,10)
for x,z,w,h in [(shell_rj45_x,shell_rj45_z,shell_rj45_width,shell_rj45_height),(shell_usb_mid_x,shell_usb_mid_z,shell_usb_mid_width,shell_usb_mid_height),(shell_usb_right_x,shell_usb_right_z,shell_usb_right_width,shell_usb_right_height)]:
 sill=z-h/2
 z0=base_thickness-base_edge_radius
 tongue=wall_ring & (Pos(x,base_depth/2,(z0+sill)/2)*Box(w-2*base_port_filler_clearance,4*shell_wall,sill-z0))
 base=base+(tongue-corner_relief)

# Cover screws into the shell columns.
for seat in layout.base_mount_seats:
 base=base-seat

# Pi screws: ISO7046 M2.5x10 from below, through cover + post + Pi board into the
# P165-B heatsink's own M2.5 metal threads (2.9 mm engagement). No printed thread.
PI_SCREW_LENGTH=10.0
pi_mount_screws=[]
for xx in PI_HOLE_X:
 for yy in PI_HOLE_Y:
  screw=CounterSunkScrew('M2.5-0.45',length=PI_SCREW_LENGTH,fastener_type='iso7046')
  assert base_thickness>=screw.head_height
  frame=Location((xx,yy,0),(180,0,0))
  seat=frame*layout.printed_seat(screw,PI_BOARD_BOTTOM_Z)
  base=base-seat
  pi_mount_screws.append(frame*Pos(0,0,-layout.countersink_settle_depth)*screw)
  print('PI_METAL_JOINT',dict(axis=(xx,yy),metal_engagement=PI_SCREW_LENGTH-PI_BOARD_BOTTOM_Z-PI_PCB_T))
assert len(base.solids())==1, ('base',[round(s.volume,1) for s in base.solids()])

base.color=Color(0.88,0.86,0.79)
publish('base',base,'Bottom cover and Pi carrier',material='pla',role='part')
for i,screw in enumerate(pi_mount_screws):
 publish('pi_mount_screw_'+str(i+1),screw,'Pi M2.5x10 screw',material='stainless_steel',role='fastener')

connection_inventory={**{'module_'+str(i+1):'kit' for i in range(len(layout.front_module_screws))},**{'pcb_'+str(i+1):'kit' for i in range(len(layout.pcb_mount_screws))},**{'fan_'+str(i+1):'kit' for i in range(len(layout.cooling_screws))},**{'bottom_'+str(i+1):'kit' for i in range(len(layout.base_mount_screws))},**{'pod_'+str(i+1):'kit' for i in range(len(layout.screen_mount_screws))},**{'pi_'+str(i+1):'metal M2.5 receiver, free standard screw' for i in range(len(pi_mount_screws))}}
assert len(connection_inventory)==20
