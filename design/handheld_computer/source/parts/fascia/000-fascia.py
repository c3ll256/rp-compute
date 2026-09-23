import math
fascia_width=param('fascia_width',77.0)
fascia_depth=param('fascia_depth',65.0)
fascia_radius=param('fascia_radius',6.0)
fascia_thickness=param('fascia_thickness',3.0)
fascia_window_width=param('fascia_window_width',66.5)
fascia_window_height=param('fascia_window_height',49.5)
fascia_window_radius=param('fascia_window_radius',2.75)
fascia_edge_radius=param('fascia_edge_radius',0.6)
fascia_slope=param('fascia_slope',13.0)
fascia_front_height=param('fascia_front_height',0.7)
fascia_wall=param('fascia_wall',2.4)
fascia_window_x=param('fascia_window_x',0.0)
fascia_window_y=param('fascia_window_y',0.0)
fascia_fpc_width=param('fascia_fpc_width',14.0)
fascia_fpc_length=param('fascia_fpc_length',10.0)
fascia_fpc_y=param('fascia_fpc_y',-25.0)
fascia_fpc_roof=param('fascia_fpc_roof',1.5)
fascia_fpc_depth=param('fascia_fpc_depth',5.0)
a=math.radians(fascia_slope)
d=fascia_depth*math.cos(a)
zc=fascia_front_height+fascia_depth*math.sin(a)/2
h=fascia_front_height+fascia_depth*math.sin(a)
F=Pos(0,0,zc)*Rot(fascia_slope,0,0)
outer=extrude(RectangleRounded(fascia_width,d,fascia_radius),amount=h+fascia_thickness)
outer=outer & (F*Pos(0,0,-2*h)*Box(4*fascia_width,4*fascia_depth,4*h))
edges=[e for e in outer.edges() if all(abs(v.Z-zc-v.Y*math.tan(a))<0.001 for v in e.vertices())]
outer=fillet(edges,fascia_edge_radius)
inner=Pos(0,0,-fascia_wall)*extrude(RectangleRounded(fascia_width-2*fascia_wall,d-2*fascia_wall,fascia_radius-fascia_wall),amount=h+2*fascia_wall)
innerclip=Pos(0,0,zc-fascia_thickness/math.cos(a))*Rot(fascia_slope,0,0)*Pos(0,0,-2*h)*Box(4*fascia_width,4*fascia_depth,4*h)
body=outer-(inner & innerclip)
window=F*Pos(fascia_window_x,fascia_window_y,-2*fascia_thickness)*extrude(RectangleRounded(fascia_window_width,fascia_window_height,fascia_window_radius),amount=4*fascia_thickness)
body-=window
# Underside relief, not an external port. No connector/PCB placeholder.
body-=F*Pos(0,fascia_fpc_y,-fascia_fpc_roof-fascia_fpc_depth/2)*Box(fascia_fpc_width,fascia_fpc_length,fascia_fpc_depth)
# Rear retaining assembly; local frame is the unchanged screen plane.
from screwjoint import make_screw_joint_v1
retainer_width=param('retainer_width',66.0)
retainer_depth=param('retainer_depth',44.0)
retainer_y=param('retainer_y',-1.77)
retainer_thickness=param('retainer_thickness',2.0)
retainer_back_gap=param('retainer_back_gap',1.0)
retainer_rail_width=param('retainer_rail_width',3.0)
retainer_tail_gap=param('retainer_tail_gap',16.0)
retainer_screw_x=param('retainer_screw_x',20.0)
retainer_screw_y_front=param('retainer_screw_y_front',-28.0)
retainer_screw_y_rear=param('retainer_screw_y_rear',25.5)
retainer_ear_width=param('retainer_ear_width',5.4)
retainer_ear_depth=param('retainer_ear_depth',6.0)
retainer_seat_z=param('retainer_seat_z',-7.0)
retainer_engagement=param('retainer_engagement',3.0)
# Sharp p26 stack; existing locator target glass rear is -3.04.
GLASS_BACK=-3.04
ret_top=GLASS_BACK-retainer_back_gap
ret_bottom=ret_top-retainer_thickness
ring=Pos(0,retainer_y,ret_bottom)*extrude(Rectangle(retainer_width,retainer_depth)-Rectangle(retainer_width-2*retainer_rail_width,retainer_depth-2*retainer_rail_width),amount=retainer_thickness)
ring-=Pos(0,retainer_y-retainer_depth/2,ret_top)*Box(retainer_tail_gap,2*retainer_rail_width+2,4*retainer_thickness)
host=F.inverse()*body
screws=[]
for sx in [-1,1]:
 for yy in [retainer_screw_y_front,retainer_screw_y_rear]:
  xx=sx*retainer_screw_x
  # Solid receiver is a wall reinforcement rooted in the housing side/roof.
  receiver=Pos(xx,yy,(retainer_seat_z-0.8)/2)*Box(retainer_ear_width,retainer_ear_depth,-retainer_seat_z-0.8)
  receiver=receiver-(Pos(0,0,-3.6)*extrude(Rectangle(fascia_window_width,fascia_window_height),amount=4.0))
  host=host+receiver
  # Ear and short web set screw-stack height independently of soft glass support.
  ear=Pos(xx,yy,retainer_seat_z-retainer_thickness/2)*Box(retainer_ear_width,retainer_ear_depth,retainer_thickness)
  edge_y=retainer_y+(-retainer_depth/2 if yy<0 else retainer_depth/2)
  web=Pos(xx,(edge_y+yy)/2,(ret_bottom+0.2+retainer_seat_z-retainer_thickness)/2)*Box(retainer_ear_width,abs(edge_y-yy)+retainer_ear_depth,ret_bottom+0.2-retainer_seat_z+retainer_thickness)
  ring=ring.fuse(web,ear)
# Hard-stop ears cannot intrude into the receiver or existing housing walls.
ring=Compound(children=list(ring.solids()))-host
if isinstance(ring,ShapeList): ring=Compound(children=list(ring))
# Seat the bezel's added rear flange, leaving original glass pocket unchanged.
flange_seat=Pos(0,-1.77,-4.2)*extrude(Rectangle(70,47)-Rectangle(63.4,43.42),amount=2)
ring=ring-flange_seat
if isinstance(ring,ShapeList): ring=Compound(children=list(ring))
# U-shaped tail guard, open to rear servicing and clear of the bend.
guard_width=param('retainer_guard_width',19.0)
guard_depth=param('retainer_guard_depth',7.0)
guard_wall=param('retainer_guard_wall',1.5)
guard_y=param('retainer_guard_y',-24.75)
guard=Pos(0,guard_y,ret_bottom)*extrude(Rectangle(guard_width,guard_depth)-Pos(0,guard_wall/2)*Rectangle(guard_width-2*guard_wall,guard_depth-guard_wall),amount=retainer_thickness)
# Side arms overlap the front ring outside its 16mm tail notch.
ring=ring.fuse(guard)
ring=ring-flange_seat
if isinstance(ring,ShapeList): ring=Compound(children=list(ring))
# Full negative FPC path: one 180-degree fold behind the panel.
# 0.30mm is the manufacturer's stiffened-tail thickness, used conservatively
# over the flex span. Overall free length is a disclosed 13.7mm layout target,
# not a toleranced manufacturer length; actual tail measurement remains required.
fpc_bend_start=param('fpc_bend_start',1.0)
fpc_inner_radius=param('fpc_inner_radius',1.35)
fpc_free_length=param('fpc_free_length',13.7)
fpc_path_clearance=param('fpc_path_clearance',0.25)
FPC_T=0.30
FPC_Z=-2.23
GLASS_EDGE=-23.18
r=fpc_inner_radius+FPC_T/2
cy=GLASS_EDGE-fpc_bend_start
cz=FPC_Z-r
tail_end_y=cy+fpc_free_length-fpc_bend_start-math.pi*r
assert fpc_bend_start>=0.8 and fpc_bend_start+math.pi*r<=6.0
assert fpc_inner_radius>=0.45
assert fpc_free_length-fpc_bend_start-math.pi*r>4.0
t=FPC_T+2*fpc_path_clearance
route_arc=Pos(0,cy,cz)*Rot(0,90,0)*(Cylinder(r+t/2,11)-Cylinder(r-t/2,12))
route_arc=route_arc & (Pos(0,cy-r-t/2,cz)*Box(12,2*r+t,2*r+t))
route_start=Pos(0,(GLASS_EDGE+cy)/2,FPC_Z)*Box(11,fpc_bend_start,t)
route_return=Pos(0,(cy+tail_end_y)/2,FPC_Z-2*r)*Box(11,tail_end_y-cy,t)
# Negative clearance only: no invented purchased FPC solid is published.
for keepout in [route_arc,route_start,route_return]:
 host=host-keepout
 ring=ring-keepout
print('FPC_LAYOUT',dict(bend_start=fpc_bend_start,bend_end=fpc_bend_start+math.pi*r,inner_radius=fpc_inner_radius,tail_end_y=tail_end_y,tail_z=FPC_Z-2*r))
# Every joint sees final host and retainer; do not add empty Compound bosses.
for sx in [-1,1]:
 for yy in [retainer_screw_y_front,retainer_screw_y_rear]:
  xx=sx*retainer_screw_x
  joint=make_screw_joint_v1(size="M2",at=Location((xx,yy,retainer_seat_z-retainer_thickness),(180,0,0)),through=[(ring,retainer_thickness)],engage_depth=retainer_engagement,into=host,head="socket_cap",material="PLA",boss="none",label="lcd-retainer")
  ring=ring-joint.through_cuts[0]
  if len(joint.bosses.solids())>0:
   host=host+joint.bosses
  host=host-joint.engage_cuts
  screws.append(joint.hardware)
  print("RETAINER_JOINT",xx,yy,joint.screw_length_mm,joint.boss_length_mm,joint.hole_profile)
assert len(ring.solids())==1, ('ring solids',len(ring.solids()),[(round(s.volume,3),str(s.bounding_box())) for s in ring.solids()])
assert len(host.solids())==1
host.color=Color(0.96,0.31,0.07)
ring.color=Color(0.17,0.18,0.19)
publish('fascia',F*host,'Screen housing mounts')
publish('retainer',ring,'Rear retaining frame')
for i,sc in enumerate(screws):
 publish('retainer_screw_'+str(i+1),sc,'M2 retaining screw')
