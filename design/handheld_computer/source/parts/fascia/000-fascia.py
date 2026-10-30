# cell: fascia
# cell: fascia
import math
housing=part('shell')
# Equal nominal border on the screen plane. The purchased glass, bezel and FPC
# keep their existing pose; only the outside pod silhouette contracts.
fascia_width=housing.case_width
fascia_thickness=param('fascia_thickness',3.0)
fascia_window_width=param('fascia_window_width',66.5)
fascia_window_height=param('fascia_window_height',49.5)
fascia_window_radius=param('fascia_window_radius',2.75)
fascia_edge_radius=param('fascia_edge_radius',0.6)
fascia_slope=param('fascia_slope',13.0)
fascia_wall=param('fascia_wall',2.4)
fascia_window_x=param('fascia_window_x',0.0)
fascia_window_y=param('fascia_window_y',0.0)
fascia_fpc_width=param('fascia_fpc_width',14.0)
fascia_fpc_length=param('fascia_fpc_length',10.0)
fascia_fpc_y=param('fascia_fpc_y',-25.0)
fascia_fpc_roof=param('fascia_fpc_roof',1.5)
fascia_fpc_depth=param('fascia_fpc_depth',5.0)
fascia_screen_center_z=param('fascia_screen_center_z',8.010909266)
fascia_center_y=param('fascia_center_y',21.521201483)
fascia_border=(fascia_width-fascia_window_width)/2
fascia_depth=fascia_window_height+2*fascia_border
fascia_radius=fascia_window_radius+fascia_border
assert fascia_border>=fascia_wall
assert abs(fascia_window_x)<1e-6 and abs(fascia_window_y)<1e-6
a=math.radians(fascia_slope)
zc=fascia_screen_center_z
F=Pos(0,0,zc)*Rot(fascia_slope,0,0)
d=fascia_depth*math.cos(a)
front_y=-d/2
rear_y=housing.case_depth/2-fascia_center_y
fascia_front_height=zc-fascia_depth*math.sin(a)/2
h=zc+fascia_depth*math.sin(a)/2
rear_lean=(rear_y-d/2)/h
fascia_rear_lean_deg=math.degrees(math.atan(rear_lean))
assert fascia_front_height>0 and 0<=fascia_rear_lean_deg<=35
# Bottom rear corners match the case. The face is a true rounded 76x59
# rectangle on the 13deg screen plane, including equal-offset corner radii.
def pod_foot(z,inset=0.0):
 front=front_y+inset
 rear=rear_y-inset*math.sqrt(1+rear_lean**2)
 radius=housing.case_corner-inset
 return Pos(0,(front+rear)/2,z)*RectangleRounded(fascia_width-2*inset,rear-front,radius)
def pod_face(inset=0.0):
 return F*RectangleRounded(fascia_width-2*inset,fascia_depth-2*inset,fascia_radius-inset)
outer=loft([pod_foot(0),pod_face()],ruled=True)
edges=[e for e in outer.edges() if all(abs(v.Z-zc-v.Y*math.tan(a))<0.001 for v in e.vertices())]
outer=fillet(edges,fascia_edge_radius)
# Extend the negative interior below the part, then clip to the roof underside.
# This avoids crossing loft sections at the very low front lip.
inner=loft([pod_foot(-fascia_wall,fascia_wall),pod_face(fascia_wall)],ruled=True)
innerclip=Pos(0,0,zc-fascia_thickness/math.cos(a))*Rot(fascia_slope,0,0)*Pos(0,0,-2*h)*Box(4*fascia_width,4*fascia_depth,4*h)
# Protect four roof-backed ribs during hollowing.
POD_WORLD=Pos(0,fascia_center_y,housing.SCREEN_POD_BASE_Z)
raw_mounts=Compound(children=[s.moved(POD_WORLD.inverse()) for s in housing.screen_mount_receiver_blanks])
hollow=(inner & innerclip)-raw_mounts
body=outer-hollow
gap=housing.SCREEN_POD_BASE_Z-housing.case_top_center
feet=raw_mounts & (Pos(0,0,-gap/2)*Box(4*fascia_width,4*fascia_depth,gap))
body=body.fuse(*list(feet.solids()))
print('EQUAL_FRAME_DATUMS',dict(face_width=fascia_width,face_depth=fascia_depth,borders=[fascia_border]*4,front_rise_with_seam=fascia_front_height+0.3,rear_lean_deg=fascia_rear_lean_deg))
# Integral optical lip replaces the independent bezel and its thin rear flange.
fascia_optical_clearance=param('fascia_optical_clearance',0.3)
fascia_glass_clearance=param('fascia_glass_clearance',0.3)
fascia_front_lip=param('fascia_front_lip',1.2)
fascia_optical_radius=param('fascia_optical_radius',0.35)
# Sharp LCY-1210401A p26: glass and active-area datums are frozen.
GLASS_W,GLASS_H,GLASS_Y,GLASS_BACK=62.8,42.82,-1.77,-3.04
optical=F*Pos(0,0,-12)*extrude(RectangleRounded(58.8+2*fascia_optical_clearance,35.28+2*fascia_optical_clearance,fascia_optical_radius),amount=24)
pocket=F*Pos(0,GLASS_Y,-12)*extrude(Rectangle(GLASS_W+2*fascia_glass_clearance,GLASS_H+2*fascia_glass_clearance),amount=12-fascia_front_lip)
body=body-optical-pocket
# Shallow 0.5mm-wide marking preserves the equal outer border without a third piece.
fascia_border_line_width=param('fascia_border_line_width',0.5)
fascia_border_line_depth=param('fascia_border_line_depth',0.3)
border_line=RectangleRounded(fascia_window_width,fascia_window_height,fascia_window_radius)-RectangleRounded(fascia_window_width-2*fascia_border_line_width,fascia_window_height-2*fascia_border_line_width,fascia_window_radius-fascia_border_line_width)
body=body-F*Pos(0,0,-fascia_border_line_depth)*extrude(border_line,amount=2*fascia_border_line_depth)
# Underside relief, not an external port. No connector/PCB placeholder.
body-=F*Pos(0,fascia_fpc_y,-fascia_fpc_roof-fascia_fpc_depth/2)*Box(fascia_fpc_width,fascia_fpc_length,fascia_fpc_depth)
from screwjoint import make_screw_joint_v1, ScrewJointNotApplicableV1
from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole
# M2 countersunk kit rejects ISO10642 (starts at M3). Explicit free head/seat
# fallback uses verified ISO7046 M2; compensated printed receiver stays kit-owned.
# Same printed head allowance as the other enclosure joints.
m2_flush_joint=housing.flush_joint

# Shared mechanical interface. All four stops share the glass-support plane.
retainer_thickness=param('retainer_thickness',2.0)
retainer_back_gap=param('fascia_rear_pad_thickness',2.0)
retainer_engagement=param('fascia_stop_engagement',2.0)
retainer_screw_x=param('retainer_screw_x',20.0)
retainer_screw_x_front=param('retainer_screw_x_front',27.0)
retainer_screw_y_front=param('retainer_screw_y_front',-26.25)
retainer_screw_y_rear=param('retainer_screw_y_rear',25.5)
retainer_ear_width=param('retainer_ear_width',5.4)
retainer_ear_depth=param('retainer_ear_depth',6.0)
retainer_seat_z=GLASS_BACK-retainer_back_gap
ret_bottom=retainer_seat_z-retainer_thickness
host=F.inverse()*body
joint_axes=[(sx*(retainer_screw_x_front if yy==retainer_screw_y_front else retainer_screw_x),yy) for sx in [-1,1] for yy in [retainer_screw_y_front,retainer_screw_y_rear]]
for xx,yy in joint_axes:
 receiver=Pos(xx,yy,(retainer_seat_z-0.8)/2)*Box(retainer_ear_width,retainer_ear_depth,-retainer_seat_z-0.8)
 host=host+receiver
# Positive glass locator walls and roof remain a single printable piece.
host=host-(F.inverse()*pocket)-(F.inverse()*optical)
# Full negative FPC path: one 180-degree fold behind the panel.
# 0.30mm is the manufacturer's stiffened-tail thickness, used conservatively
# over the flex span. Overall free length is a disclosed 13.7mm layout target,
# not a toleranced manufacturer length; user authorized continued provisional\n# design from this estimate. This old negative channel does not certify mating.
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
print('FPC_LAYOUT',dict(bend_start=fpc_bend_start,bend_end=fpc_bend_start+math.pi*r,inner_radius=fpc_inner_radius,tail_end_y=tail_end_y,tail_z=FPC_Z-2*r))

# Local PCB clearance at the front rail; glass and screw datums are unchanged.
fascia_pcb_bottom_z=param('fascia_pcb_bottom_z',21.8)
fascia_pcb_clearance=param('fascia_pcb_clearance',0.5)
fascia_pcb_top_air=param('fascia_pcb_top_air',1.5)
PCB_T=0.8 # Frozen PCB release finished thickness.
SCREEN_WORLD=Location((0,21.521201483,35.310909266),(13,0,0))
# Negative probes only, derived from the released front spine and its screw notch.
# Three straight pockets avoid widening the retained screw-axis material.
zmid=fascia_pcb_bottom_z+PCB_T/2+(fascia_pcb_top_air-fascia_pcb_clearance)/2
height=PCB_T+fascia_pcb_clearance+fascia_pcb_top_air
c=fascia_pcb_clearance
voids=[
 Pos(-10.15,-1.9,zmid)*Box(14.3+2*c,12.0+2*c,height),
 Pos(-11.5,-7.4,zmid)*Box(17.0+2*c,2.2+2*c,height),
 Pos(-11.5,1.5,zmid)*Box(17.0+2*c,5.0+2*c,height),
 Pos(4.5,2.0,zmid)*Box(11.0+2*c,5.0+2*c,height),
 Pos(0.5,-1.3,fascia_pcb_bottom_z+PCB_T+1.1/2)*Box(6.013+2*fascia_pcb_top_air,5.0+2*fascia_pcb_top_air,1.1+2*fascia_pcb_top_air)
]
# Released C_BUF1 body bboxX5.8..6.6,Y-2.0..-0.4,Z22.595..23.395.
# Exact supplier package size0.8x1.6x0.8; local pocket follows its new position.
fascia_pcb_small_component_air=param('fascia_pcb_small_component_air',1.6)
voids.append(Pos(6.2,-1.2,fascia_pcb_bottom_z+PCB_T+0.8/2)*Box(0.8+2*fascia_pcb_small_component_air,1.6+2*fascia_pcb_small_component_air,0.8+2*fascia_pcb_small_component_air))
# Released U_BUF1 body moved into front-right screen rail; rigid PCB datum.
# Exact release8816a764 bounds X7.493685..13.50629,Y-10.5..-5.5,Z22.594999..23.695082.
# Allowance is independently adjustable; screen/retainer screw axes stay fixed.
retainer_pcb_buffer_air=param('retainer_pcb_buffer_air',1.6)
voids.append(Pos(10.4999875,-8.0,23.1450405)*Box(6.012605+2*retainer_pcb_buffer_air,5.0+2*retainer_pcb_buffer_air,1.100083+2*retainer_pcb_buffer_air))
# Current SHOU HAN C5373447 drawer, not the former hinged FH12A.
# Actual closed bounds plus supplier PDF1 reference1.5mm forward stroke.
fascia_fpc_latch_air=param('fascia_fpc_latch_air',0.5)
voids.append(Pos(0,4.0699924,23.599999)*Box(10.6+2*fascia_fpc_latch_air,6.8+2*fascia_fpc_latch_air,2.010000+2*fascia_fpc_latch_air))
# Negative service channel to the glass exit; not a manufactured cable model.
# Frozen exitYZ(-0.5630558,27.9236986), selected horizontal mouth Y2.1699924.
fascia_active_tail_channel_width=param('fascia_active_tail_channel_width',7.5)
fascia_active_tail_channel_depth=param('fascia_active_tail_channel_depth',7.0)
fascia_active_tail_channel_height=param('fascia_active_tail_channel_height',7.5)
voids.append(Pos(0,0,25.75)*Box(fascia_active_tail_channel_width,fascia_active_tail_channel_depth,fascia_active_tail_channel_height))
for void_world in voids:
 void_local=void_world.moved(SCREEN_WORLD.inverse())
 host=host-void_local


# The through-sheet coupon represents only the joint stack, never a physical part.
# The independently modeled flat retainer subtracts these exact same kit seats.
retainer_cuts=[]
retainer_hardware=[]
joint_lengths=[]
connections={}
for i,(xx,yy) in enumerate(joint_axes):
 sheet=Pos(xx,yy,ret_bottom+retainer_thickness/2)*Box(retainer_ear_width,retainer_ear_depth,retainer_thickness)
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,ret_bottom),(180,0,0)),sheet,retainer_thickness,retainer_engagement,host,'lcd-flat-retainer')
 if len(joint.bosses.solids())>0:
  host=host+joint.bosses
 host=host-joint.engage_cuts
 retainer_cuts.append(seat)
 retainer_hardware.append(hardware)
 joint_lengths.append(joint.screw_length_mm)
 connections['lcd_stop_'+str(i+1)]='printed-screw-joint-v1 M2 receiver; free ISO7046 head/seat after kit rejection, printing allowance'
 print('FLAT_RETAINER_JOINT',xx,yy,joint.screw_length_mm,joint.boss_length_mm)
# Four receiving holes share the same kit and axes as the upper shell.
mount_cuts=Compound(children=[s.moved(SCREEN_WORLD.inverse()) for s in housing.screen_mount_engage_cuts])
host=host-mount_cuts
cover_probes=Compound(children=[s.moved(SCREEN_WORLD.inverse()) for s in housing.screen_mount_cover_probes])
missing=cover_probes-host
v=0.0 if missing is None else (sum(s.volume for s in missing) if isinstance(missing,ShapeList) else missing.volume)
assert v<0.00001,('screen mount closing skin',v)

assert len(connections)==4
assert len(host.solids())==1 and host.is_valid
# No screw receiver may rise through the visible front surface.
assert host.bounding_box().max.Z<0.001,('receiver breaks face',host.bounding_box())
host.color=srgb('#e87736')
publish('fascia',F*host,'Integral screen frame',material='pla',role='part')
# Supplemental exact checks for the moved hardware. The ordinary assembly report
# caps candidate pairs on these imported assemblies; check their individual solids
# here against the final source-owned interfaces without changing published geometry.
COMPACT_PI_ASSET="design/handheld_computer/source/assets/1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe.step"
COMPACT_PCB_ASSET="design/handheld_computer/source/assets/fc6d293414ed15fcebd1226aa4a9bee691ebe59ee7340ee3075cb63742b08fa8.step"
compact_pi=asset(COMPACT_PI_ASSET).moved(Location((39+housing.pi_offset_x,-30.5,7),(90,90,0)))
compact_pcb=asset(COMPACT_PCB_ASSET).moved(Location((-100,81,21.8)))
compact_pod=(F*host).moved(Location((0,fascia_center_y,27.3)))
compact_reference_bounds={}
def compact_overlap_check(label,reference,target):
 total=0.0
 hits=[]
 tb=target.bounding_box()
 rb=reference.bounding_box()
 if any(getattr(rb.max,k)<getattr(tb.min,k) or getattr(rb.min,k)>getattr(tb.max,k) for k in ("X","Y","Z")):
  print("COMPACT_EXACT",label,0.0,"separated whole bounds")
  return
 key=id(reference)
 if key not in compact_reference_bounds:
  compact_reference_bounds[key]=[(i,s,s.bounding_box()) for i,s in enumerate(reference.solids())]
 for i,solid,sb in compact_reference_bounds[key]:
  if any(getattr(sb.max,k)<getattr(tb.min,k) or getattr(sb.min,k)>getattr(tb.max,k) for k in ("X","Y","Z")):
   continue
  overlap=solid & target
  v=0.0 if overlap is None else (sum(q.volume for q in overlap if q is not None) if isinstance(overlap,ShapeList) else overlap.volume)
  if v>0.00001:
   hits.append((i,round(v,6),str(sb)))
   total+=v
 print("COMPACT_EXACT",label,round(total,8),hits)
 assert total<0.00001,(label,round(total,6),hits)
compact_overlap_check("Pi / shell",compact_pi,housing.body)
compact_overlap_check("Pi / base",compact_pi,part("base").base)
compact_overlap_check("PCB / shell",compact_pcb,housing.body)
compact_overlap_check("PCB / pod",compact_pcb,compact_pod)
for i,(screw,probe) in enumerate(zip(housing.screen_mount_screws,housing.screen_mount_access_probes)):
 compact_overlap_check('PCB / screen screw '+str(i+1),compact_pcb,screw)
 compact_overlap_check('PCB / driver access '+str(i+1),compact_pcb,probe)
 compact_overlap_check('Pi / screen screw '+str(i+1),compact_pi,screw)
