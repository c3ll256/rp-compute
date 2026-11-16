# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
# cell: fascia
import math
housing=part('shell')
# Equal line-to-optical-window band on the screen plane; outer face is independent. The pod base stays on the shell seam;
# the screen pose is derived from the specified front rise and tilt.
fascia_width=housing.case_width
fascia_thickness=param('fascia_thickness',3.0)
fascia_border_inner_gap=param('fascia_border_inner_gap',3.0)
fascia_optical_clearance=param('fascia_optical_clearance',0.3)
fascia_optical_radius=param('fascia_optical_radius',0.35)
fascia_border_line_width=param('fascia_border_line_width',0.5)
fascia_window_width=58.8+2*fascia_optical_clearance+2*(fascia_border_inner_gap+fascia_border_line_width)
fascia_window_height=35.28+2*fascia_optical_clearance+2*(fascia_border_inner_gap+fascia_border_line_width)
fascia_window_radius=fascia_optical_radius+fascia_border_inner_gap+fascia_border_line_width
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
fascia_border=(fascia_width-fascia_window_width)/2
# The visible face offsets the existing line by exactly the side margin.
# The front skirt drops vertically from the visible face; glass and FPC stay put.
fascia_face_depth=fascia_window_height+2*fascia_border
fascia_face_corner_radius=fascia_window_radius+fascia_border
fascia_depth=fascia_face_depth
fascia_radius=fascia_face_corner_radius
assert fascia_border>=fascia_edge_radius+0.5
assert (fascia_depth-fascia_window_height)/2>=fascia_edge_radius+0.5
assert abs(fascia_window_x)<1e-6 and abs(fascia_window_y)<1e-6
fascia_glass_clearance=param('fascia_glass_clearance',0.3)
fascia_front_lip=param('fascia_front_lip',1.5)

# Outline from Sharp p26; thickness from the user's physical sample.
GLASS_W,GLASS_H,GLASS_Y=62.8,42.82,-1.77
screen_measured_thickness=param('screen_measured_thickness',1.8)
screen_foam_sheet_thickness=param('screen_foam_sheet_thickness',0.2)
screen_foam_compression_ratio=param('screen_foam_compression_ratio',0.10)
assert 0<=screen_foam_compression_ratio<=0.20
foam_installed_thickness=screen_foam_sheet_thickness*(1-screen_foam_compression_ratio)
GLASS_FRONT=-fascia_front_lip-foam_installed_thickness
GLASS_BACK=GLASS_FRONT-screen_measured_thickness
screen_clamp_gap=screen_measured_thickness+2*foam_installed_thickness

# Keep the printed shell and PCB fixed, preserve the user's front height,
# and derive the raised display pose and a compatible native-tail route.
# The shell retains its original service-well datum.
GLASS_EDGE=-23.18
FPC_Z=GLASS_FRONT-0.83
# Preserve the user's1.67mm nominal front rise. A1mm forward shift provides
# native-tail reach without changing the printed shell or its mounting axes.
fascia_front_nominal_rise=param('fascia_front_nominal_rise',1.67)
fascia_screen_forward=param('fascia_screen_forward',1.0)
REFERENCE_FRONT_WORLD_Y=-4.04626901696457
a=math.radians(fascia_slope)
fascia_center_y=REFERENCE_FRONT_WORLD_Y-fascia_screen_forward+fascia_depth*math.cos(a)/2
fascia_screen_center_z=housing.case_top_center+fascia_front_nominal_rise-housing.SCREEN_POD_BASE_Z+fascia_depth*math.sin(a)/2
FPC_ANCHOR_Y=fascia_center_y+GLASS_EDGE*math.cos(a)-FPC_Z*math.sin(a)
FPC_ANCHOR_Z=housing.SCREEN_POD_BASE_Z+fascia_screen_center_z+GLASS_EDGE*math.sin(a)+FPC_Z*math.cos(a)
zc=fascia_screen_center_z
F=Pos(0,0,zc)*Rot(fascia_slope,0,0)
d=fascia_depth*math.cos(a)
front_y=-d/2
rear_y=housing.case_depth/2-fascia_center_y
fascia_front_height=zc-fascia_depth*math.sin(a)/2
h=zc+fascia_depth*math.sin(a)/2
rear_lean=(rear_y-d/2)/h
fascia_rear_lean_deg=math.degrees(math.atan(rear_lean))
assert fascia_front_height>0 and 0<=fascia_rear_lean_deg<=45
# Rear corners still match the case. The front straight edge is vertical,
# with only the existing small top radius.
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
print('EQUAL_WINDOW_LINE_BAND',dict(face_width=fascia_width,face_depth=fascia_depth,gaps=[fascia_border_inner_gap]*4,line_outer=[fascia_window_width,fascia_window_height],line_radius=fascia_window_radius,front_rise_with_seam=fascia_front_height+0.3,rear_lean_deg=fascia_rear_lean_deg))
# Integral optical lip replaces the independent bezel and its thin rear flange.

print('MEASURED_SCREEN_STACK',dict(glass=screen_measured_thickness,foam_sheet=screen_foam_sheet_thickness,foam_layers=2,compression_ratio=screen_foam_compression_ratio,closed_gap=screen_clamp_gap))
optical=F*Pos(0,0,-12)*extrude(RectangleRounded(58.8+2*fascia_optical_clearance,35.28+2*fascia_optical_clearance,fascia_optical_radius),amount=24)
pocket=F*Pos(0,GLASS_Y,-12)*extrude(Rectangle(GLASS_W+2*fascia_glass_clearance,GLASS_H+2*fascia_glass_clearance),amount=12-fascia_front_lip)
body=body-optical-pocket
# Shallow line is a true constant offset of the optical opening, including corners.

fascia_border_line_depth=param('fascia_border_line_depth',0.3)
fascia_min_roof_skin=param('fascia_min_roof_skin',1.2)
border_line=RectangleRounded(fascia_window_width,fascia_window_height,fascia_window_radius)-RectangleRounded(fascia_window_width-2*fascia_border_line_width,fascia_window_height-2*fascia_border_line_width,fascia_window_radius-fascia_border_line_width)
body=body-F*Pos(0,0,-fascia_border_line_depth)*extrude(border_line,amount=2*fascia_border_line_depth)
# The relief roof follows the screen plane; its skin also accounts for the groove.
fpc_relief_roof=max(fascia_fpc_roof,fascia_border_line_depth+fascia_min_roof_skin)
body-=F*Pos(0,fascia_fpc_y,-fpc_relief_roof-fascia_fpc_depth/2)*Box(fascia_fpc_width,fascia_fpc_length,fascia_fpc_depth)
from screwjoint import make_screw_joint_v1, ScrewJointNotApplicableV1
from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole
# M2.5 countersunk joints use the shell's shared kit tooling and matched seat/hardware.
m2_flush_joint=housing.flush_joint

# Shared mechanical interface. All four stops share the glass-support plane.
retainer_thickness=param('retainer_thickness',2.0)
retainer_back_gap=foam_installed_thickness
retainer_engagement=param('fascia_stop_engagement',2.0)
retainer_screw_x=param('retainer_screw_x',20.0)
retainer_front_capture_x=param('retainer_front_capture_x',28.5)
retainer_screw_y_front=param('retainer_screw_y_front',-26.25)
retainer_screw_y_rear=param('retainer_screw_y_rear',24.5)
retainer_ear_width=param('retainer_ear_width',6.4)
retainer_ear_depth=param('retainer_ear_depth',6.0)
retainer_front_tip_y=param('retainer_front_tip_y',-26.4)
retainer_front_capture_overlap=param('retainer_front_capture_overlap',1.5)
retainer_front_capture_floor=param('retainer_front_capture_floor',1.2)
retainer_front_slot_air=param('retainer_front_slot_air',0.3)
retainer_front_capture_side_wall=param('retainer_front_capture_side_wall',1.5)
retainer_front_capture_width=retainer_ear_width+2*(retainer_front_slot_air+retainer_front_capture_side_wall)
# Retain the original four hard-stop ears and full2mm screw engagement.
# Only the pressure rail rises toward the thinner measured pad stack.
retainer_seat_z=param('retainer_stop_plane_z',-5.04)
retainer_contact_z=GLASS_BACK-retainer_back_gap
retainer_pressure_rise=retainer_contact_z-retainer_seat_z
assert retainer_pressure_rise>=0
ret_bottom=retainer_seat_z-retainer_thickness
host=F.inverse()*body
joint_axes=[(sx*(retainer_front_capture_x if yy==retainer_screw_y_front else retainer_screw_x),yy) for sx in [-1,1] for yy in [retainer_screw_y_front,retainer_screw_y_rear]]
# Keep the below-seam receiver feet, but trim the upper ends to the new
# exterior slope so no rectangular stop breaks through the narrower face.
receiver_envelope=F.inverse()*(outer+Pos(0,0,-12)*extrude(pod_foot(0),amount=12))
# Front rigid capture slots replace the two front screw receivers.
# Their floor bears directly on the retainer underside: the glass gap is unchanged.
# The upper0.3mm assembly clearance is above the retainer, not below its bearing.
front_capture_floors=[]
aperture_air=retainer_front_slot_air
aperture_inner=Pos(0,housing.shell_passage_y,0)*extrude(RectangleRounded(housing.shell_passage_width-2*aperture_air,housing.shell_passage_depth-2*aperture_air,housing.shell_passage_radius-aperture_air),amount=100,both=True)
underfoot_clip=aperture_inner.moved((POD_WORLD*F).inverse())
above_foot=F.inverse()*(Pos(0,0,100)*Box(200,200,200))
receiver_envelope=receiver_envelope & (underfoot_clip+above_foot)
for xx,yy in joint_axes:
 receiver_bottom=retainer_seat_z+(retainer_front_slot_air if yy<0 else 0)
 receiver=Pos(xx,yy,(receiver_bottom-0.8)/2)*Box(retainer_front_capture_width if yy<0 else retainer_ear_width,retainer_ear_depth,-receiver_bottom-0.8)
 receiver=receiver & receiver_envelope
 host=host+receiver
 if yy<0:
  capture_rear=retainer_front_tip_y+retainer_front_capture_overlap
  capture_front=retainer_front_tip_y-retainer_front_capture_overlap
  floor=Pos(xx,(capture_front+capture_rear)/2,ret_bottom-retainer_front_capture_floor/2)*Box(retainer_front_capture_width,capture_rear-capture_front,retainer_front_capture_floor)
  floor=floor & receiver_envelope
  front_capture_floors.append(floor)
  host=host+floor
  for side in [-1,1]:
   column_x=xx+side*(retainer_ear_width/2+retainer_front_slot_air+retainer_front_capture_side_wall/2)
   column_bottom=ret_bottom-retainer_front_capture_floor
   column_top=receiver_bottom+0.05
   column=Pos(column_x,(capture_front+capture_rear)/2,(column_top+column_bottom)/2)*Box(retainer_front_capture_side_wall,capture_rear-capture_front,column_top-column_bottom)
   host=host+(column & receiver_envelope)
# Positive glass locator walls and roof remain a single printable piece.
host=host-(F.inverse()*pocket)-(F.inverse()*optical)
# Negative reserve for the active top-contact socket; no purchased cable solid.
# Native total length remains the user's delegated13.7+/-0.5mm estimate.
# All bends stay between0.8 and6mm from the glass; stiffness and seating
# still need actual mating. The initial straight accommodates the steeper exit.
fpc_free_length=param('fpc_free_length',13.7)
fpc_path_clearance=param('fpc_path_clearance',0.25)
fpc_initial_straight=0.85 #0.8mm manufacturer no-bend zone plus0.05mm nominal margin.
FPC_T_MAX=0.33
FPC_R2=0.45+FPC_T_MAX/2
FPC_SOCKET_STOP_Y=5.77
FPC_SOCKET_SLOT_Z=23.045
FPC_T=0.30
SCREEN_WORLD=Location((0,fascia_center_y,housing.SCREEN_POD_BASE_Z+fascia_screen_center_z),(fascia_slope,0,0))
reserve_t=FPC_T_MAX+2*fpc_path_clearance
reserve_w=11.0
route_theta=math.pi+a
route_beta=1.5*math.pi-route_theta
route_coeff=route_beta-math.cos(a)+1-math.sin(a)
route_const=fpc_initial_straight+FPC_ANCHOR_Z-fpc_initial_straight*math.sin(a)-FPC_R2-FPC_SOCKET_SLOT_Z+math.pi/2*FPC_R2+FPC_SOCKET_STOP_Y-FPC_ANCHOR_Y+fpc_initial_straight*math.cos(a)-FPC_R2
assert 0.8<=fpc_initial_straight<6.0

def fpc_arc_band(y,z,r,theta0,theta1,width,thickness):
 center=(y-r*math.sin(theta0),z+r*math.cos(theta0))
 phi0=theta0-math.pi/2
 phi1=theta1-math.pi/2
 def pt(rr,phi):return (center[0]+rr*math.cos(phi),center[1]+rr*math.sin(phi),0)
 ro=r+thickness/2
 ri=r-thickness/2
 edges=[Edge.make_three_point_arc(pt(ro,phi0),pt(ro,(phi0+phi1)/2),pt(ro,phi1)),Edge.make_line(pt(ro,phi1),pt(ri,phi1)),Edge.make_three_point_arc(pt(ri,phi1),pt(ri,(phi0+phi1)/2),pt(ri,phi0)),Edge.make_line(pt(ri,phi0),pt(ro,phi0))]
 band=Pos(-width/2,0,0)*extrude(Plane.YZ*Face(Wire(edges)),amount=width)
 return band,(center[0]+r*math.sin(theta1),center[1]-r*math.cos(theta1))

def fpc_route_case(length,width,thickness):
 r1=(length-route_const)/route_coeff
 v=FPC_ANCHOR_Z-fpc_initial_straight*math.sin(a)-r1*math.cos(a)-FPC_R2-FPC_SOCKET_SLOT_Z
 bend_end=fpc_initial_straight+route_beta*r1+v+math.pi/2*FPC_R2
 assert r1-FPC_T_MAX/2>=0.45 and v>=0 and bend_end<=6.0,(length,r1,v,bend_end)
 first_end=(FPC_ANCHOR_Y+fpc_initial_straight*math.cos(route_theta),FPC_ANCHOR_Z+fpc_initial_straight*math.sin(route_theta))
 first=Pos(0,(FPC_ANCHOR_Y+first_end[0])/2,(FPC_ANCHOR_Z+first_end[1])/2)*Rot(math.degrees(route_theta),0,0)*Box(width,fpc_initial_straight,thickness)
 arc1,p1=fpc_arc_band(first_end[0],first_end[1],r1,route_theta,1.5*math.pi,width,thickness)
 vertical=Pos(0,p1[0],p1[1]-v/2)*Box(width,thickness,v)
 arc2,p2=fpc_arc_band(p1[0],p1[1]-v,FPC_R2,1.5*math.pi,2*math.pi,width,thickness)
 last=Pos(0,(p2[0]+FPC_SOCKET_STOP_Y)/2,FPC_SOCKET_SLOT_Z)*Box(width,FPC_SOCKET_STOP_Y-p2[0],thickness)
 report=dict(length_mm=length,r1_mm=r1,vertical_mm=v,bend_end_mm=bend_end,free_straight_mm=length-bend_end,last_bend_y=p2[0])
 return (first,arc1+vertical+arc2,last),report
native_route_reserves_world=[]
native_route_cases=[]
start_cuts=[];arc_cuts=[];return_cuts=[]
for length in [fpc_free_length-0.5,fpc_free_length,fpc_free_length+0.5]:
 shapes,report=fpc_route_case(length,reserve_w,reserve_t)
 native_route_reserves_world.append(shapes)
 native_route_cases.append(report)
 start_cuts.append(shapes[0].moved(SCREEN_WORLD.inverse()))
 arc_cuts.append(shapes[1].moved(SCREEN_WORLD.inverse()))
 return_cuts.append(shapes[2].moved(SCREEN_WORLD.inverse()))
 print('NATIVE_TAIL_ANALYTIC',report)
route_start=Compound(children=start_cuts)
route_arc=Compound(children=arc_cuts)
route_return=Compound(children=return_cuts)
for keepout in [route_start,route_arc,route_return]:host=host-keepout
print('RAISED_SCREEN_POSE',dict(slope=fascia_slope,center_y=fascia_center_y,center_z=housing.SCREEN_POD_BASE_Z+fascia_screen_center_z,exit_y=FPC_ANCHOR_Y,exit_z=FPC_ANCHOR_Z))

# Local PCB clearance at the front rail; glass and screw datums are unchanged.
fascia_pcb_bottom_z=housing.pcb_mount_bottom_z
fascia_pcb_clearance=param('fascia_pcb_clearance',0.5)
fascia_pcb_top_air=param('fascia_pcb_top_air',1.5)
PCB_T=0.8
SCREEN_WORLD=Location((0,fascia_center_y,housing.SCREEN_POD_BASE_Z+fascia_screen_center_z),(fascia_slope,0,0))
assert abs(fascia_center_y+GLASS_EDGE*math.cos(a)-FPC_Z*math.sin(a)-FPC_ANCHOR_Y)<1e-6
assert abs(housing.SCREEN_POD_BASE_Z+fascia_screen_center_z+GLASS_EDGE*math.sin(a)+FPC_Z*math.cos(a)-FPC_ANCHOR_Z)<1e-6
# Negative probes only, derived from the released front spine and its screw notch.
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
fascia_pcb_small_component_air=param('fascia_pcb_small_component_air',1.6)
voids.append(Pos(6.2,-1.2,fascia_pcb_bottom_z+PCB_T+0.8/2)*Box(0.8+2*fascia_pcb_small_component_air,1.6+2*fascia_pcb_small_component_air,0.8+2*fascia_pcb_small_component_air))
retainer_pcb_buffer_air=param('retainer_pcb_buffer_air',1.6)
voids.append(Pos(10.4999875,-8.0,23.1450405+fascia_pcb_bottom_z-21.8)*Box(6.012605+2*retainer_pcb_buffer_air,5.0+2*retainer_pcb_buffer_air,1.100083+2*retainer_pcb_buffer_air))
fascia_fpc_latch_air=param('fascia_fpc_latch_air',0.5)
voids.append(Pos(0,4.0699924,23.599999+fascia_pcb_bottom_z-21.8)*Box(10.6+2*fascia_fpc_latch_air,6.8+2*fascia_fpc_latch_air,2.010000+2*fascia_fpc_latch_air))
fascia_active_tail_channel_width=param('fascia_active_tail_channel_width',7.5)
fascia_active_tail_channel_depth=param('fascia_active_tail_channel_depth',7.0)
fascia_active_tail_channel_height=param('fascia_active_tail_channel_height',7.5)
TAIL_EXIT_Z=SCREEN_WORLD.position.Z-23.18*math.sin(a)+FPC_Z*math.cos(a)
voids.append(Pos(0,0,TAIL_EXIT_Z-2.1736986)*Box(fascia_active_tail_channel_width,fascia_active_tail_channel_depth,fascia_active_tail_channel_height))
service_roof_depth=max(fascia_front_lip,fascia_border_line_depth+fascia_min_roof_skin)
service_cut_limit=Pos(0,0,-(4*h+service_roof_depth)/2)*Box(4*fascia_width,4*fascia_depth,4*h-service_roof_depth)
voids=[(void_world.moved(SCREEN_WORLD.inverse()) & service_cut_limit).moved(SCREEN_WORLD) for void_world in voids]
for void_world in voids:
 void_local=void_world.moved(SCREEN_WORLD.inverse())
 host=host-void_local

# The through-sheet coupon represents only the joint stack, never a physical part.
# The independently modeled flat retainer subtracts these exact same kit seats.
retainer_cuts=[]
retainer_hardware=[]
retainer_head_service_depth=param('retainer_head_service_depth',6.0)
retainer_service_floor_z=param('retainer_service_floor_z',-32.0)
retainer_service_skin=param('retainer_service_skin',1.25)
joint_lengths=[]
connections={}
retainer_screw_axes=[axis for axis in joint_axes if axis[1]>0]
for i,(xx,yy) in enumerate(retainer_screw_axes):
 sheet=Pos(xx,yy,ret_bottom+retainer_thickness/2)*Box(retainer_ear_width,retainer_ear_depth,retainer_thickness)
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,ret_bottom),(180,0,0)),sheet,retainer_thickness,retainer_engagement,host,'lcd-flat-retainer')
 if len(joint.bosses.solids())>0:
  host=host+joint.bosses
 # Extend the kit's own seat-mouth profile for removal of the rear screw.
 # This is access clearance below the stop, not a hand-modeled receiving hole.
 zbottom=seat.bounding_box().min.Z
 mouths=[face for face in seat.faces() if abs(face.center().Z-zbottom)<1e-5 and face.normal_at().Z<-.99]
 mouth=max(mouths,key=lambda face:face.area)
 head_service=extrude(mouth,amount=retainer_head_service_depth,dir=(0,0,-1))
 # Rear access cavity widens with depth, leaving the outer rear skin closed.
 # Its upper end stops exactly at the hard stop, retaining thread engagement.
 service_top=retainer_seat_z
 service_bottom=retainer_service_floor_z
 rear_top=yy+2.8
 rear_bottom=rear_top+0.12*(service_top-service_bottom)
 front=yy-retainer_ear_depth/2-0.3
 width=retainer_ear_width+0.6
 def rear_access_section(z,rear,extra=0.0):
  return Pos(xx,(front+rear+extra)/2,z)*Rectangle(width,rear-front+extra)
 service=loft([rear_access_section(service_bottom,rear_bottom),rear_access_section(service_top,rear_top)],ruled=True)
 # A geometric envelope behind the cavity proves the thin local access skin.
 guard=loft([rear_access_section(service_bottom,rear_bottom,retainer_service_skin),rear_access_section(service_top,rear_top,retainer_service_skin)],ruled=True)
 guard=guard & (F.inverse()*(Pos(0,0,100)*Box(4*fascia_width,4*fascia_depth,200)))
 missing=guard-(F.inverse()*outer)
 vv=0.0 if not missing else missing.volume
 assert vv<1e-5,('rear access closing skin',vv)
 host=host-joint.engage_cuts-seat-head_service-service
 retainer_cuts.append(seat)
 retainer_hardware.append(hardware)
 joint_lengths.append(joint.screw_length_mm)
 connections['lcd_stop_'+str(i+1)]='printed-screw-joint-v1 M2.5 receiver and matched ISO7046 head/seat with0.2mm head recess'
 print('FLAT_RETAINER_JOINT',xx,yy,joint.screw_length_mm,joint.boss_length_mm)
# Four receiving holes share the same kit and axes as the upper shell.
mount_cuts=Compound(children=[s.moved(SCREEN_WORLD.inverse()) for s in housing.screen_mount_engage_cuts])
host=host-mount_cuts
cover_probes=Compound(children=[s.moved(SCREEN_WORLD.inverse()) for s in housing.screen_mount_cover_probes])
missing=cover_probes-host
v=0.0 if missing is None else (sum(s.volume for s in missing) if isinstance(missing,ShapeList) else missing.volume)
assert v<0.00001,('screen mount closing skin',v)

# Exact full-area guards catch any future relief breaking through the decoration
# or thinning the glass-support lip. These are assertions, not published parts.
groove_floor_guard=Pos(0,0,-fascia_border_line_depth-fascia_min_roof_skin)*extrude(border_line,amount=fascia_min_roof_skin)
glass_lip_guard=Pos(0,GLASS_Y,-fascia_front_lip)*extrude(Rectangle(GLASS_W+2*fascia_glass_clearance,GLASS_H+2*fascia_glass_clearance),amount=fascia_front_lip)
glass_lip_guard=glass_lip_guard-(F.inverse()*optical)
# The specified shallow engraving removes only the upper0.3mm; the separate
# full-area groove guard proves1.2mm of material remains beneath every point.
glass_lip_guard-=Pos(0,0,-fascia_border_line_depth)*extrude(border_line,amount=2*fascia_border_line_depth)
for label,guard in [('complete decoration floor',groove_floor_guard),('complete optical lip',glass_lip_guard)]:
 missing_skin=guard-host
 missing_skin_volume=0.0 if not missing_skin else missing_skin.volume
 print('SCREEN_SKIN_GUARD',label,dict(required_mm=fascia_min_roof_skin,missing_mm3=missing_skin_volume))
 assert missing_skin_volume<0.00001,(label,missing_skin_volume)
for label,probe in [('fold arc',route_arc),('fold start',route_start),('fold return',route_return)]:
 collision=host & probe
 collision_volume=0.0 if not collision else collision.volume
 assert collision_volume<0.00001,('protected skin blocks FPC reserve',label,collision_volume)

connections['front_left_capture']='free: rigid sliding pocket, no flex snap, 1.5mm nominal bearing'
connections['front_right_capture']='free: rigid sliding pocket, no flex snap, 1.5mm nominal bearing'
assert len(connections)==4
assert len(host.solids())==1 and host.is_valid
assert host.bounding_box().max.Z<0.001,('receiver breaks face',host.bounding_box())

# Rear branding uses the supplied SVG's mM path, without its app-icon tile,
# gradients, blur or shadow. Normalised XY outline retains circular arc segments.
# Source: product/references/uploads/20261116T193239198Z-1-icon.svg
rear_brand_text=param('rear_brand_text','Makit Compute')
rear_brand_font_size=param('rear_brand_font_size',6.0)
rear_brand_logo_width=param('rear_brand_logo_width',12.0)
rear_brand_gap=param('rear_brand_gap',3.0)
rear_brand_center_z=param('rear_brand_center_z',13.0)
rear_brand_relief=param('rear_brand_relief',0.45)
rear_brand_finish_t=param('rear_brand_finish_t',0.02)
assert 0.4<=rear_brand_relief<=0.8 and 0<rear_brand_finish_t<=0.05
rear_brand_logo_commands=[[[0.143062029401219,0.2689135891000359,0],[0.24883470778056646,0.2689135891000359,0]],[[0.24883470778056646,0.2689135891000359,0],[0.2611625923963443,0.2664245229883055,0],[0.2716027249910362,0.25941197561850127,0]],[[0.2716027249910362,0.25941197561850127,0],[0.4904983865184655,0.04069558981713874,0]],[[0.4904983865184655,0.04069558981713874,0],[0.49754530987419004,0.03017267913475118,0],[0.5,0.017748296880602327,0]],[[0.5,0.017748296880602327,0],[0.5,-0.23664395840803157,0]],[[0.5,-0.23664395840803157,0],[0.49054844399669745,-0.2594620330967333,0],[0.4677303693079957,-0.2689135891000359,0]],[[0.4677303693079957,-0.2689135891000359,0],[0.3592685550376479,-0.2689135891000359,0]],[[0.3592685550376479,-0.2689135891000359,0],[0.34694067042187,-0.2664245229883054,0],[0.3365005378271783,-0.2594119756185014,0]],[[0.3365005378271783,-0.2594119756185014,0],[0.1301541771244174,-0.05306561491574045,0]],[[0.1301541771244174,-0.05306561491574045,0],[0.1182993130089981,-0.0506390450036757,0],[0.11168877733954816,-0.06077447113660807,0]],[[0.11168877733954816,-0.06077447113660807,0],[0.11168877733954816,-0.23664395840803157,0]],[[0.11168877733954816,-0.23664395840803157,0],[0.10223722133624562,-0.2594620330967333,0],[0.07941914664754385,-0.2689135891000359,0]],[[0.07941914664754385,-0.2689135891000359,0],[-0.028863391896737225,-0.2689135891000359,0]],[[-0.028863391896737225,-0.2689135891000359,0],[-0.04128777415088618,-0.2664588989742259,0],[-0.051810684833273536,-0.2594119756185014,0]],[[-0.051810684833273536,-0.2594119756185014,0],[-0.25815704553603447,-0.05306561491574045,0]],[[-0.25815704553603447,-0.05306561491574045,0],[-0.2698651562633208,-0.05083550890560959,0],[-0.27644316959483684,-0.06077447113660807,0]],[[-0.27644316959483684,-0.06077447113660807,0],[-0.27644316959483684,-0.23664395840803157,0]],[[-0.27644316959483684,-0.23664395840803157,0],[-0.2858947255981394,-0.2594620330967333,0],[-0.30871280028684117,-0.2689135891000359,0]],[[-0.30871280028684117,-0.2689135891000359,0],[-0.4677303693079957,-0.2689135891000359,0]],[[-0.4677303693079957,-0.2689135891000359,0],[-0.49054844399669745,-0.2594620330967333,0],[-0.5,-0.23664395840803157,0]],[[-0.5,-0.23664395840803157,0],[-0.5,-0.025098601649336683,0]],[[-0.5,-0.025098601649336683,0],[-0.49054844399669756,-0.002280526960634915,0],[-0.4677303693079957,0.0071710290426676235,0]],[[-0.4677303693079957,0.0071710290426676235,0],[-0.302438149874507,0.0071710290426676235,0]],[[-0.302438149874507,0.0071710290426676235,0],[-0.2846907584499611,0.01452223926745843,0],[-0.2773395482251703,0.03226963069200431,0]],[[-0.2773395482251703,0.03226963069200431,0],[-0.2773395482251703,0.23664395840803157,0]],[[-0.2773395482251703,0.23664395840803157,0],[-0.26788799222186777,0.2594620330967333,0],[-0.245069917533166,0.2689135891000359,0]],[[-0.245069917533166,0.2689135891000359,0],[-0.13929723915381856,0.2689135891000359,0]],[[-0.13929723915381856,0.2689135891000359,0],[-0.12696935453804079,0.2664245229883055,0],[-0.11652922194334887,0.25941197561850127,0]],[[-0.11652922194334887,0.25941197561850127,0],[0.09250627465041238,0.050376479024740094,0]],[[0.09250627465041238,0.050376479024740094,0],[0.10421438537769873,0.048146373014609334,0],[0.1107923987092147,0.05808533524560771,0]],[[0.1107923987092147,0.05808533524560771,0],[0.1107923987092147,0.23664395840803157,0]],[[0.1107923987092147,0.23664395840803157,0],[0.12024395471251724,0.2594620330967333,0],[0.143062029401219,0.2689135891000359,0]]]
brand_edges=[]
for command in rear_brand_logo_commands:
 pts=[Vector(p)*rear_brand_logo_width for p in command]
 brand_edges.append(Edge.make_line(*pts) if len(pts)==2 else Edge.make_three_point_arc(*pts))
brand_logo=Face(Wire(brand_edges))
brand_letters=Text(rear_brand_text,rear_brand_font_size,font='Arial',font_style=FontStyle.BOLD)
brand_text_bounds=brand_letters.bounding_box()
brand_text_w=brand_text_bounds.size.X
brand_letters=Pos(-(brand_text_bounds.min.X+brand_text_bounds.max.X)/2,-(brand_text_bounds.min.Y+brand_text_bounds.max.Y)/2)*brand_letters
brand_width=rear_brand_logo_width+rear_brand_gap+brand_text_w
assert brand_width<fascia_width-14
brand_art=Pos(-brand_width/2+rear_brand_logo_width/2,0)*brand_logo+Pos(brand_width/2-brand_text_w/2,0)*brand_letters
brand_plane=Plane(origin=(0,rear_y-rear_lean*rear_brand_center_z,rear_brand_center_z),x_dir=(-1,0,0),z_dir=(0,1,rear_lean))
brand_pod=brand_plane*Pos(0,0,-0.05)*extrude(brand_art,amount=rear_brand_relief+0.05,dir=(0,0,1))
brand_inside=brand_plane*Pos(0,0,-0.05)*extrude(brand_art,amount=0.05,dir=(0,0,1))
brand_missing=brand_inside-(F*host)
brand_missing_v=0.0 if not brand_missing else brand_missing.volume
assert brand_missing_v<1e-5,('branding foot must fully meet rear wall',brand_missing_v)
host=host+brand_pod.moved(F.inverse())
assert len(host.solids())==1 and host.is_valid
# Paint is a reference only. Relief is integral to the original orange frame.
rear_brand_finish=brand_plane*Pos(0,0,rear_brand_relief)*extrude(brand_art,amount=rear_brand_finish_t,dir=(0,0,1))
rear_brand_finish.color=srgb('#e9e6df')
publish('rear_brand_finish',rear_brand_finish,'Rear brand paint',role='reference')
print('REAR_BRANDING',dict(text=rear_brand_text,width_mm=brand_width,logo_width_mm=rear_brand_logo_width,font_size_mm=rear_brand_font_size,relief_mm=rear_brand_relief,plane_center_z_world=rear_brand_center_z+housing.SCREEN_POD_BASE_Z))

host.color=srgb('#e87736')
publish('fascia',F*host,'Integral screen frame',material='pla',role='part')
# Cosmetic finish only: a nominal20um dry paint layer above the unchanged
# integral lip. This reference is not a third printed piece or a glued bezel.
screen_face_finish_thickness=param('screen_face_finish_thickness',0.02)
assert 0<screen_face_finish_thickness<=0.05
screen_face_finish_outer=RectangleRounded(fascia_window_width-2*fascia_border_line_width,fascia_window_height-2*fascia_border_line_width,fascia_window_radius-fascia_border_line_width)
screen_face_finish_opening=RectangleRounded(58.8+2*fascia_optical_clearance,35.28+2*fascia_optical_clearance,fascia_optical_radius)
screen_face_finish=extrude(screen_face_finish_outer-screen_face_finish_opening,amount=screen_face_finish_thickness)
# Continue the same finish down the optical wall; leave all foam seats bare.
# The20um coat leaves0.28mm per side beyond the58.8x35.28mm active area.
screen_finish_clear_w=58.8+2*(fascia_optical_clearance-screen_face_finish_thickness)
screen_finish_clear_h=35.28+2*(fascia_optical_clearance-screen_face_finish_thickness)
assert fascia_optical_clearance-screen_face_finish_thickness>=0.2
screen_finish_inner=RectangleRounded(screen_finish_clear_w,screen_finish_clear_h,fascia_optical_radius-screen_face_finish_thickness)
screen_finish_wall=Pos(0,0,-fascia_front_lip)*extrude(screen_face_finish_opening-screen_finish_inner,amount=fascia_front_lip+screen_face_finish_thickness)
screen_face_finish=screen_face_finish+screen_finish_wall
screen_face_finish.color=srgb('#26282b')
assert len(screen_face_finish.solids())==1 and screen_face_finish.is_valid
publish('screen_face_finish',F*screen_face_finish,'Matte screen finish',role='reference')
COMPACT_PI_ASSET="design/handheld_computer/source/assets/1906d615405ba20aaaf5b4bdcd41f19fe49b8e82a87ab1387e0f1d1abfe6bbbe.step"
compact_pi=asset(COMPACT_PI_ASSET).moved(Location((39+housing.pi_offset_x,-30.5,7+getattr(housing,'pi_stack_lift',0.0)),(90,90,0)))
compact_pod=(F*host).moved(Location((0,fascia_center_y,housing.SCREEN_POD_BASE_Z)))
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
for i,(screw,probe) in enumerate(zip(housing.screen_mount_screws,housing.screen_mount_access_probes)):
 compact_overlap_check('Pi / screen screw '+str(i+1),compact_pi,screw)