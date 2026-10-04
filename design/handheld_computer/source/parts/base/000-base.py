base_width=param('base_width',85.0)
base_depth=param('base_depth',115.0)
base_corner=param('base_corner',9.0)
base_thickness=param('base_thickness',2.4)
base_edge_radius=param('base_edge_radius',0.7)
base=extrude(RectangleRounded(base_width,base_depth,base_corner),amount=base_thickness)
base=fillet(base.edges().filter_by(Plane.XY),base_edge_radius)

from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole

# Shared bottom-cover attachment datums; asymmetric to avoid Pi rear USB bodies.
base_mount_front_x=param('base_mount_front_x',32.0)
base_mount_front_y=param('base_mount_front_y',-48.0)
base_mount_left_rear_x=param('base_mount_left_rear_x',-32.0)
base_mount_left_rear_y=param('base_mount_left_rear_y',47.0)
base_mount_right_mid_x=param('base_mount_right_mid_x',32.0)
base_mount_right_mid_y=param('base_mount_right_mid_y',-35.0)
base_mount_axes=[(-base_mount_front_x,base_mount_front_y),(base_mount_front_x,base_mount_front_y),(base_mount_left_rear_x,base_mount_left_rear_y),(base_mount_right_mid_x,base_mount_right_mid_y)]

# ISO7046 head/seat follows shell's explicit kit rejection fallback.
BASE_FASTENER_SIZE='M2-0.4'
BASE_FASTENER_LENGTH=6.0
base_screw=CounterSunkScrew(BASE_FASTENER_SIZE,length=BASE_FASTENER_LENGTH,fastener_type='iso7046')
for xx,yy in base_mount_axes:
 base=base-(Location((xx,yy,0),(180,0,0))*ClearanceHole(base_screw,depth=base_thickness,counter_sunk=True,mode=Mode.PRIVATE))
# A shallow inside rim registers the edge below Pi's lowest connector Z=3.45.
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
assert len(base.solids())==1

base.color=Color(0.88,0.86,0.79)
publish('base',base,'Fixed bottom cover',material='pla')