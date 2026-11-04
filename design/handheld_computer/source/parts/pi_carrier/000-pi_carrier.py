# cell: pi_carrier

layout=part('shell')
# Pi datums from the existing imported Pi4B placement and official hole pattern.
PI_HOLE_X=tuple(x+layout.pi_offset_x for x in (-13.5,35.5))
PI_HOLE_Y=(-27.0,31.0)
PI_BOARD_BOTTOM_Z=5.3
PI_PCB_T=1.8
pi_carrier_bottom=layout.pi_carrier_ear_bottom  # common bed plane and shell mating datum
pi_carrier_rail_thickness=param('pi_carrier_rail_thickness',2.0)
pi_carrier_rail_width=param('pi_carrier_rail_width',3.2)
pi_carrier_left_rail_x=param('pi_carrier_left_rail_x',-24.8)
pi_carrier_right_rail_x=param('pi_carrier_right_rail_x',26.0)
pi_carrier_rear_rail_y=param('pi_carrier_rear_rail_y',36.0)
pi_carrier_front_rail_y=param('pi_carrier_front_rail_y',-38.0)
pi_carrier_pad_diameter=param('pi_carrier_pad_diameter',6.0)
pi_carrier_pad_bottom=param('pi_carrier_pad_bottom',3.3)
pi_carrier_metal_screw_length=param('pi_carrier_metal_screw_length',6.0)
z=pi_carrier_bottom
t=pi_carrier_rail_thickness
w=pi_carrier_rail_width
left=pi_carrier_left_rail_x
right=pi_carrier_right_rail_x
front=pi_carrier_front_rail_y
rear=pi_carrier_rear_rail_y+w/2
carrier=Pos((left+right)/2,front,z+t/2)*Box(right-left+w,w,t)
carrier+=Pos(left,(front+layout.pi_carrier_left_rear_y)/2,z+t/2)*Box(w,layout.pi_carrier_left_rear_y-front+w,t)
carrier+=Pos(right,(front+rear)/2,z+t/2)*Box(w,rear-front,t)
carrier+=Pos((left+right)/2,pi_carrier_rear_rail_y,z+t/2)*Box(right-left+w,w,t)
for yy in PI_HOLE_Y:
 carrier+=Pos((right+PI_HOLE_X[1])/2,yy,z+t/2)*Box(PI_HOLE_X[1]-right,w,t)
 carrier+=Pos((left+PI_HOLE_X[0])/2,yy,z+t/2)*Box(PI_HOLE_X[0]-left,w,t)
for xx in PI_HOLE_X:
 for yy in PI_HOLE_Y:
  carrier+=Pos(xx,yy,(z+PI_BOARD_BOTTOM_Z)/2)*Cylinder(pi_carrier_pad_diameter/2,PI_BOARD_BOTTOM_Z-z)
# Flat lugs share the rail bed plane. No raised ear or undercut neck.
# Their complete footprint is present on the first printed layer.
for i,(xx,yy) in enumerate(layout.pi_carrier_axes):
 tab=layout.pi_carrier_tabs[i]
 if i<2:
  carrier+=Pos((left+xx)/2,yy,z+t/2)*Box(abs(left-xx)+w,layout.pi_carrier_ear_width,t)
 else:
  carrier+=Pos(xx,(yy+front)/2,z+t/2)*Box(layout.pi_carrier_ear_width,abs(yy-front)+w,t)
 carrier+=tab
 carrier-=layout.pi_carrier_tab_seats[i]
# Existing Pi mounting holes remain cylindrical; heads sit only in printed pads.
from bd_warehouse.fastener import CounterSunkScrew
pi_mount_screws=[]
for xx in PI_HOLE_X:
 for yy in PI_HOLE_Y:
  screw=CounterSunkScrew('M2.5-0.45',length=pi_carrier_metal_screw_length,fastener_type='iso7046')
  frame=Location((xx,yy,pi_carrier_pad_bottom),(180,0,0))
  carrier-=frame*layout.printed_seat(screw,PI_BOARD_BOTTOM_Z-pi_carrier_pad_bottom)
  carrier-=Pos(xx,yy,(z+pi_carrier_pad_bottom)/2)*Cylinder((screw.head_diameter+2*layout.countersink_print_radial_allowance)/2,pi_carrier_pad_bottom-z+0.02)
  pi_mount_screws.append(frame*Pos(0,0,-layout.countersink_settle_depth)*screw)
engagement=pi_carrier_pad_bottom-layout.countersink_settle_depth+pi_carrier_metal_screw_length-(PI_BOARD_BOTTOM_Z+PI_PCB_T)
assert engagement>=2.0-1e-6
assert len(carrier.solids())==1,('carrier solid count',len(carrier.solids()))
assert carrier.is_valid
carrier.color=srgb('#54656b')
publish('pi_carrier',carrier,'Pi independent carrier',material='pla',role='part')
for i,screw in enumerate(pi_mount_screws):
 publish('pi_mount_screw_'+str(i+1),screw,'Pi M2.5x6 screw',material='stainless_steel',role='fastener')
for i,screw in enumerate(layout.pi_carrier_hardware):
 publish('pi_carrier_shell_screw_'+str(i+1),screw,'Carrier M2 shell screw',material='stainless_steel',role='fastener')
connection_inventory={**{'carrier_to_shell_'+str(i+1):'printed-screw-joint-v1, compensated standard countersink' for i in range(3)},**{'Pi_to_carrier_'+str(i+1):'free standard M2.5 screw into purchased metal receiver' for i in range(4)}}
assert len(connection_inventory)==7
print('PI_CARRIER',dict(board_z=PI_BOARD_BOTTOM_Z,frame_bottom=z,frame_top=z+t,pad_thickness=PI_BOARD_BOTTOM_Z-z,metal_engagement=engagement))
