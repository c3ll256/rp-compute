# cell: shell
# cell: shell
# cell: shell
# Print orientation: roof face down on the bed (Z=case_top_center is the bed plane).
# Every interior feature grows from the roof or a wall, or slopes >=45 deg, so the
# shell prints without support material. Assembly is vertical: the shell drops
# straight down over the Pi that is already screwed to the bottom cover.
case_width=param('case_width',85.0)
pi_offset_x=param('pi_offset_x',-5.0)
fan_offset_x=param('fan_offset_x',3.0)
fan_offset_y=param('fan_offset_y',-3.0)
case_depth=param('case_depth',115.0)
case_corner=param('case_corner',9.0)
case_top_center=param('case_top_center',27.0)
shell_wall=param('shell_wall',2.4)
shell_lower_z=param('shell_lower_z',2.7)
shell_edge_radius=param('shell_edge_radius',1.0)
front_module_width=param('front_module_width',70.0)
front_module_depth=param('front_module_depth',37.0)
front_module_y=param('front_module_y',-34.0)
front_module_aperture_width=param('front_module_aperture_width',54.0)
front_module_aperture_depth=param('front_module_aperture_depth',26.0)
front_module_screw_x=param('front_module_screw_x',31.0)
front_module_screw_y_offset=param('front_module_screw_y_offset',15.0)
front_module_screw_engagement=param('front_module_screw_engagement',2.0)
front_module_blank_thickness=param('front_module_blank_thickness',1.4)
shell_passage_width=param('shell_passage_width',71.0)
shell_passage_depth=param('shell_passage_depth',54.0)
shell_passage_y=param('shell_passage_y',21.5)
shell_passage_radius=param('shell_passage_radius',4.5)
# Opening centres follow the placed step.parts Pi4B reference.
shell_rj45_x=param('shell_rj45_x',-6.75)+pi_offset_x
shell_rj45_z=param('shell_rj45_z',14.0)
shell_rj45_width=param('shell_rj45_width',17.0)
shell_rj45_height=param('shell_rj45_height',15.0)
shell_usb_mid_x=param('shell_usb_mid_x',12.0)+pi_offset_x
shell_usb_mid_z=param('shell_usb_mid_z',15.0)
shell_usb_mid_width=param('shell_usb_mid_width',15.0)
shell_usb_mid_height=param('shell_usb_mid_height',17.0)
shell_usb_right_x=param('shell_usb_right_x',30.0)+pi_offset_x
shell_usb_right_z=param('shell_usb_right_z',14.5)
shell_usb_right_width=param('shell_usb_right_width',16.0)
shell_usb_right_height=param('shell_usb_right_height',18.0)
shell_hdmi1_y=param('shell_hdmi1_y',-4.5)
shell_hdmi2_y=param('shell_hdmi2_y',9.0)
shell_hdmi_z=param('shell_hdmi_z',8.6)
shell_hdmi_width=param('shell_hdmi_width',7.4)
shell_hdmi_height=param('shell_hdmi_height',4.2)
shell_jack_y=param('shell_jack_y',23.5)
shell_jack_z=param('shell_jack_z',9.6)
shell_jack_diameter=param('shell_jack_diameter',7.6)
shell_port_radius=param('shell_port_radius',0.5)
shell_pi_usb_c_y=param('shell_pi_usb_c_y',-19.3)
shell_pi_usb_c_z=param('shell_pi_usb_c_z',8.18)
shell_pi_usb_c_width=param('shell_pi_usb_c_width',10.2)
shell_pi_usb_c_height=param('shell_pi_usb_c_height',5.2)
shell_pi_groove_clearance=param('shell_pi_groove_clearance',0.3)
shell_lcd_mount_x=param('shell_lcd_mount_x',20.0)
shell_lcd_mount_x_front=param('shell_lcd_mount_x_front',27.0)
shell_lcd_mount_y_front=param('shell_lcd_mount_y_front',-28.0)
shell_lcd_mount_y_rear=param('shell_lcd_mount_y_rear',25.5)
shell_lcd_well_width=param('shell_lcd_well_width',6.4)
shell_lcd_well_depth=param('shell_lcd_well_depth',7.0)
shell_lcd_front_well_depth=param('shell_lcd_front_well_depth',6.6)
pcb_mount_bottom_z=param('pcb_mount_bottom_z',21.8)
pcb_mount_x=param('pcb_mount_x',16.0)
pcb_mount_y=param('pcb_mount_y',-32.0)
pcb_mount_beam_width=param('pcb_mount_beam_width',6.0)
pcb_mount_beam_thickness=param('pcb_mount_beam_thickness',2.0)
pcb_mount_engagement=param('pcb_mount_engagement',2.0)
pcb_mount_cover_clearance=param('pcb_mount_cover_clearance',0.5)
pcb_rear_guide_y=param('pcb_rear_guide_y',24.0)
pcb_rear_guide_width=param('pcb_rear_guide_width',8.0)
pcb_rear_guide_thickness=param('pcb_rear_guide_thickness',1.5)
pcb_rear_guide_clearance=param('pcb_rear_guide_clearance',0.3)
shell_pcb_top_air=param('shell_pcb_top_air',1.6)
base_mount_front_x=param('base_mount_front_x',32.0)
base_mount_front_y=param('base_mount_front_y',-48.0)
base_mount_left_front_x=param('base_mount_left_front_x',-32.0)
base_mount_left_front_y=param('base_mount_left_front_y',-15.0)
base_mount_left_rear_x=param('base_mount_left_rear_x',-32.0)
base_mount_left_rear_y=param('base_mount_left_rear_y',51.5)
base_mount_right_mid_x=param('base_mount_right_mid_x',32.0)
base_mount_right_mid_y=param('base_mount_right_mid_y',-35.0)
base_thickness=param('base_thickness',2.4)
shell_base_pad_width=param('shell_base_pad_width',8.0)
base_screw_engagement=param('base_screw_engagement',3.6)

inner_side=case_width/2-shell_wall
roof_under=case_top_center-shell_wall

# Body. Bed edge is a 45 deg chamfer (no support); the open lower edge keeps its round.
outer=Pos(0,0,shell_lower_z)*extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center-shell_lower_z)
outer=fillet(outer.edges().filter_by(Plane.XY).group_by(Axis.Z)[0],shell_edge_radius)
# Square roof perimeter meets the matching screen pod walls without a ledge.
# Roof-down printing starts at this plane; no overhang is introduced.
inner=extrude(RectangleRounded(case_width-2*shell_wall,case_depth-2*shell_wall,case_corner-shell_wall),amount=roof_under)
body=outer-inner
assert len(body.solids())==1, ('shell body',len(body.solids()))

# Raised PCB beams: they touch the roof underside, so they print as roof ribs.
PCB_FINISHED_T=0.8 # Frozen pi_baseboard_lite release; drilled holes 2.2mm.
PCB_LEFT_EDGE=-24.5 # Released board outline.
mount_top=pcb_mount_bottom_z+PCB_FINISHED_T
beam_tip=pcb_mount_x-pcb_mount_beam_width/2
for sx in [-1,1]:
 outer_root=inner_side+shell_wall/2
 body+=Pos(sx*(beam_tip+outer_root)/2,pcb_mount_y,mount_top+pcb_mount_beam_thickness/2+0.1)*Box(outer_root-beam_tip,pcb_mount_beam_width,pcb_mount_beam_thickness+0.2)

# Bottom-cover screw columns: full height from the roof to the cover, rooted in the
# side wall. They replace the old floating pads that needed support.
base_mount_axes=[(base_mount_left_front_x,base_mount_left_front_y),(base_mount_front_x,base_mount_front_y),(base_mount_left_rear_x,base_mount_left_rear_y),(base_mount_right_mid_x,base_mount_right_mid_y)]
column_envelope=extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center)
for xx,yy in base_mount_axes:
 sx=1 if xx>0 else -1
 tip=abs(xx)-shell_base_pad_width/2
 root=case_width/2-shell_wall/2
 column=Pos(sx*(tip+root)/2,yy,(base_thickness+roof_under+0.2)/2)*Box(root-tip,shell_base_pad_width,roof_under+0.2-base_thickness)
 body+=column & column_envelope

# Fan cassette receivers: two roof-hung bosses outside the module aperture.
shell_fan_center_x=param('shell_fan_center_x',-29.0)+fan_offset_x
shell_fan_center_y=param('shell_fan_center_y',-38.0)+fan_offset_y
shell_fan_cavity_width=param('shell_fan_cavity_width',17.2)
shell_fan_cavity_height=param('shell_fan_cavity_height',5.0)
shell_fan_rail_thickness=param('shell_fan_rail_thickness',1.2)
shell_fan_boss_diameter=param('shell_fan_boss_diameter',6.0)
fan_cassette_floor_z=param('fan_cassette_floor_z',9.8)
fan_cassette_floor_thickness=param('fan_cassette_floor_thickness',1.2)
fan_cassette_roof_thickness=param('fan_cassette_roof_thickness',1.4)
fan_cassette_inlet_width=param('fan_cassette_inlet_width',13.6)
fan_cassette_ear_x=shell_fan_center_x-param('fan_cassette_ear_inset',2.5)
fan_cassette_ear_offset=(shell_fan_cavity_width+2*shell_fan_rail_thickness)/2+param('fan_cassette_ear_clearance',0.4)
fan_cassette_ear_width=param('fan_cassette_ear_width',6.0)
fan_cassette_engagement=param('fan_cassette_engagement',4.4)
fx,fy=shell_fan_center_x,shell_fan_center_y
c_floor_top=fan_cassette_floor_z+fan_cassette_floor_thickness
c_roof_bot=c_floor_top+shell_fan_cavity_height
c_top=c_roof_bot+fan_cassette_roof_thickness
for s in [-1,1]:
 body+=Pos(fan_cassette_ear_x,fy+s*fan_cassette_ear_offset,(c_top+roof_under+0.2)/2)*Cylinder(shell_fan_boss_diameter/2,roof_under+0.2-c_top)
assert len(body.solids())==1, ('after adds',[round(s.volume,1) for s in body.solids()])

# Cuts.
body-=Pos(0,shell_passage_y,roof_under)*extrude(RectangleRounded(shell_passage_width,shell_passage_depth,shell_passage_radius),amount=2*shell_wall)
# Module aperture keeps the roof over both PCB beams, so the beams never span the opening.
aperture=Pos(0,front_module_y,roof_under-0.5)*extrude(RectangleRounded(front_module_aperture_width,front_module_aperture_depth,1.5),amount=shell_wall+1.0)
for sx in [-1,1]:
 aperture-=Pos(sx*(beam_tip+front_module_aperture_width/2+1)/2,pcb_mount_y,case_top_center)*Box(front_module_aperture_width/2+1-beam_tip,pcb_mount_beam_width,10)
body-=aperture
# Rear USB/RJ45 windows run out through the lower edge: the shell slides down over the
# connectors, and tongues on the bottom cover fill the slot below each window.
port_bottom=shell_lower_z-1.0
for x,z,w,h in [(shell_rj45_x,shell_rj45_z,shell_rj45_width,shell_rj45_height),(shell_usb_mid_x,shell_usb_mid_z,shell_usb_mid_width,shell_usb_mid_height),(shell_usb_right_x,shell_usb_right_z,shell_usb_right_width,shell_usb_right_height)]:
 top=z+h/2
 body-=Pos(x,case_depth/2,(top+port_bottom)/2)*extrude(Plane.XZ*RectangleRounded(w,top-port_bottom,shell_port_radius),amount=4*shell_wall,both=True)
# Side ports clear the moulded plug shoulder as well as the metal nose.
# Negative design reserves only: these are not purchased plug models.
# The user's actual cables are not specified. Nominal supported shoulder bodies:
# USB-C12x6mm, micro-HDMI11x6mm, audio diameter10mm, straight axial approach.
# All main bores cross the complete2.4mm wall; no small aperture remains at the
# bottom of a deep pocket to stop the overmould before it reaches the receptacle.
shell_usbc_shoulder_width=param('shell_usbc_shoulder_width',13.0)
shell_hdmi_shoulder_width=param('shell_hdmi_shoulder_width',12.0)
shell_plug_shoulder_height=param('shell_plug_shoulder_height',7.0)
shell_audio_shoulder_diameter=param('shell_audio_shoulder_diameter',11.0)
shell_usbc_entry_y_flare=param('shell_usbc_entry_y_flare',0.5)
shell_plug_entry_z_flare=param('shell_plug_entry_z_flare',0.3)
shell_plug_entry_radius=param('shell_plug_entry_radius',1.0)
shell_plug_inner_reach=param('shell_plug_inner_reach',0.5)
inner_port_x=inner_side-shell_plug_inner_reach
outer_port_x=case_width/2
# Existing nose-opening parameters remain lower bounds for adjustable bores.
hdmi_clear_w=max(shell_hdmi_width,shell_hdmi_shoulder_width)
hdmi_clear_h=max(shell_hdmi_height,shell_plug_shoulder_height)
usbc_clear_w=max(shell_pi_usb_c_width,shell_usbc_shoulder_width)
usbc_clear_h=max(shell_pi_usb_c_height,shell_plug_shoulder_height)
audio_clear_d=max(shell_jack_diameter,shell_audio_shoulder_diameter)
plug_reserves=[]
def side_shoulder_cut(yy,zz,width,height,label,body_width,entry_y_flare=0.0):
 # YZ profile normal is+X. The last section continues into outside air.
 # HDMI side edges stay parallel: its13.5mm pitch retains a1.5mm separator.
 outer_width=width+2*entry_y_flare
 outer_height=height+2*shell_plug_entry_z_flare
 sections=[
  Pos(inner_port_x,yy,zz)*(Plane.YZ*RectangleRounded(width,height,shell_plug_entry_radius)),
  Pos(outer_port_x,yy,zz)*(Plane.YZ*RectangleRounded(outer_width,outer_height,shell_plug_entry_radius)),
  Pos(outer_port_x+2,yy,zz)*(Plane.YZ*RectangleRounded(outer_width,outer_height,shell_plug_entry_radius))
 ]
 cut=loft(sections,ruled=True)
 # Sharp reserve is deliberately more conservative at the plug-body corners.
 # It extends from0.2mm beyond the imported Pi board edge through the wall and
 #12mm into outside air. This tests the enclosure approach, not electrical mating.
 reserve_x=34.0+0.2 # Actual placed Pi PCB edge from imported STEP.
 reserve_end=outer_port_x+12
 probe=Pos((reserve_x+reserve_end)/2,yy,zz)*Box(reserve_end-reserve_x,body_width,6.0)
 plug_reserves.append((label,probe))
 return cut
for i,y in enumerate([shell_hdmi1_y,shell_hdmi2_y]):
 body-=side_shoulder_cut(y,shell_hdmi_z,hdmi_clear_w,hdmi_clear_h,'micro-HDMI'+str(i+1),11.0)
body-=side_shoulder_cut(shell_pi_usb_c_y,shell_pi_usb_c_z,usbc_clear_w,usbc_clear_h,'USB-C',12.0,shell_usbc_entry_y_flare)
# Full-depth circular audio barrel bore. No lower-edge flare: keep at least
#1.4mm of material above the open shell edge rather than thinning it to1.1mm.
body-=Pos(inner_port_x,shell_jack_y,shell_jack_z)*extrude(Plane.YZ*Circle(audio_clear_d/2),amount=outer_port_x+2-inner_port_x)
assert shell_jack_z-audio_clear_d/2-shell_lower_z>=1.2
audio_x=36.5 # Frontmost audio-jack bound measured on the placed Pi STEP.
audio_end=outer_port_x+12
audio_probe=Pos((audio_x+audio_end)/2,shell_jack_y,shell_jack_z)*Rot(0,90,0)*Cylinder(5.0,audio_end-audio_x)
plug_reserves.append(('3.5mm audio',audio_probe))
hdmi_web=abs(shell_hdmi2_y-shell_hdmi1_y)-hdmi_clear_w
usb_hdmi_web=(shell_hdmi1_y-shell_pi_usb_c_y)-(hdmi_clear_w+usbc_clear_w+2*shell_usbc_entry_y_flare)/2
assert hdmi_web>=1.5-1e-6 and usb_hdmi_web>=1.5-1e-6
assert min(shell_hdmi_z-hdmi_clear_h/2,shell_pi_usb_c_z-usbc_clear_h/2)-shell_plug_entry_z_flare-shell_lower_z>=1.2
print('SIDE_PORT_RESERVES',dict(usb_c_bore=[shell_usbc_shoulder_width,shell_plug_shoulder_height],hdmi_bore=[shell_hdmi_shoulder_width,shell_plug_shoulder_height],audio_bore=shell_audio_shoulder_diameter,hdmi_web=hdmi_web,usb_hdmi_web=usb_hdmi_web,inner_x=inner_port_x))
# Blind inner grooves let the 3.5mm jack and USB-C bodies, which reach into the right
# wall, slide up from the lower edge. Extents measured on the imported Pi STEP.
PI_JACK_IN_WALL=(20.5,26.5,41.5)   # y0, y1, outermost X
PI_USBC_IN_WALL=(-23.77,-14.83,40.2)
g=shell_pi_groove_clearance
for (y0,y1,xm),ztop in [(PI_JACK_IN_WALL,shell_jack_z),(PI_USBC_IN_WALL,shell_pi_usb_c_z)]:
 xa=inner_side-0.5
 xb=xm+g+pi_offset_x
 if xb>xa:
  body-=Pos((xa+xb)/2,(y0+y1)/2,(port_bottom+ztop)/2)*Box(xb-xa,y1-y0+2*g,ztop-port_bottom)
# Pi rear board corner sits inside the rounded wall; its relief is open to the lower edge.
PI_REAR_CORNER_RELIEF=(35.5+pi_offset_x,39.5+pi_offset_x,51.3,55.3,7.6)
rx0,rx1,ry0,ry1,rz1=PI_REAR_CORNER_RELIEF
body-=Pos((rx0+rx1)/2,(ry0+ry1)/2,(port_bottom+rz1)/2)*Box(rx1-rx0,ry1-ry0,rz1-port_bottom)
# Concealed wells under the screen pod clear the rear-frame mounting ears.
SCREEN_FRAME=Pos(0,21.521201483,35.310909266)*Rot(13,0,0)
for yy in [shell_lcd_mount_y_front,shell_lcd_mount_y_rear]:
 mx=shell_lcd_mount_x_front if yy==shell_lcd_mount_y_front else shell_lcd_mount_x
 for xx in [-mx,mx]:
  body-=SCREEN_FRAME*Pos(xx,yy,-8)*Box(shell_lcd_well_width,shell_lcd_front_well_depth if yy==shell_lcd_mount_y_front else shell_lcd_well_depth,20)
# Exact physical top-body bounds from PCB release 8816a764, source XY+(0,-19).
PCB_FRONT_BODY_BOUNDS=[
    (-8.650013,-51.000000,22.594999, -7.350013,-49.000000,23.894999),
    (-8.850013,-23.800000,22.594999, -7.550013,-21.800000,23.894999),
    (-17.150013,-51.000000,22.594999, -15.850013,-49.000000,23.894999),
    (4.600000,-10.750000,22.594999, 5.400000,-9.150000,23.394999),
    (4.800000,-50.649987,22.594999, 6.800000,-49.349987,23.894999),
    (14.400000,-50.649987,22.594999, 16.400000,-49.349987,23.894999),
    (-14.006302,-51.449987,22.594999, -10.993698,-48.549987,23.845082),
    (-8.450000,-19.400000,22.594999, -5.550000,-16.600000,24.144999),
    (10.550000,-20.400000,22.594999, 13.450000,-17.600000,24.144999),
    (6.349987,-17.500000,22.594999, 7.649987,-15.500000,23.894999),
    (9.193698,-51.450013,22.594999, 12.206302,-48.550013,23.845082),
    (7.493685,-10.500000,22.594999, 13.506290,-5.500000,23.695082),
]
for bx0,by0,bz0,bx1,by1,bz1 in PCB_FRONT_BODY_BOUNDS:
 body-=Pos((bx0+bx1)/2,(by0+by1)/2,(bz0+bz1)/2)*Box(bx1-bx0+2*shell_pcb_top_air,by1-by0+2*shell_pcb_top_air,bz1-bz0+2*shell_pcb_top_air)
# Left-side blower exhaust slots.
shell_cooling_slot_width=param('shell_cooling_slot_width',2.4)
shell_cooling_slot_bridge=param('shell_cooling_slot_bridge',2.0)
shell_cooling_slot_count=param('shell_cooling_slot_count',4)
shell_cooling_exhaust_z=param('shell_cooling_exhaust_z',13.25)
shell_cooling_exhaust_height=param('shell_cooling_exhaust_height',4.5)
for i in range(int(shell_cooling_slot_count)):
 offset=(i-(int(shell_cooling_slot_count)-1)/2)*(shell_cooling_slot_width+shell_cooling_slot_bridge)
 body-=Pos(-case_width/2,fy+offset,shell_cooling_exhaust_z)*extrude(Plane.YZ*SlotOverall(shell_cooling_exhaust_height,shell_cooling_slot_width,rotation=90),amount=4*shell_wall,both=True)
assert len(body.solids())==1, ('after cuts',[round(s.volume,1) for s in body.solids()])

# Rear-left PCB edge guide: seat lip + side stop, closed up to the deck with a 51 deg
# face so it grows from the roof instead of hanging off the wall.
x_wall=-inner_side-shell_wall/2
x_lip=PCB_LEFT_EDGE+0.8
x_stop=PCB_LEFT_EDGE-pcb_rear_guide_clearance
z_shelf=pcb_mount_bottom_z-pcb_rear_guide_thickness
z_stop=mount_top+pcb_rear_guide_clearance
guide_pts=[(x_wall,z_shelf),(x_lip,z_shelf),(x_lip,pcb_mount_bottom_z),(x_stop,pcb_mount_bottom_z),(x_stop,z_stop),(x_stop-0.8*(case_top_center-z_stop),case_top_center),(x_wall,case_top_center)]
guide=Pos(0,pcb_rear_guide_y,0)*extrude(Plane.XZ*Polygon(*guide_pts,align=None),amount=pcb_rear_guide_width/2,both=True)
body+=guide
assert len(body.solids())==1, ('after guide',[round(s.volume,1) for s in body.solids()],str(guide.bounding_box()))

from screwjoint import make_screw_joint_v1, ScrewJointNotApplicableV1
from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole
# Library-generated manufacturing cutter: keep the 90-degree cone and enlarge
# its diameter by 0.4mm and its depth by 0.2mm. This negative is not hardware.
countersink_print_radial_allowance=param('countersink_print_radial_allowance',0.2)
countersink_settle_depth=countersink_print_radial_allowance
def printed_seat(standard,depth):
 cutter_screw=CounterSunkScrew(standard.thread_size,length=standard.length,fastener_type=standard.fastener_type)
 cutter_screw.screw_data=dict(cutter_screw.screw_data)
 cutter_screw.screw_data['dk']+=2*countersink_print_radial_allowance
 cutter_screw.screw_data['k']+=countersink_print_radial_allowance
 assert depth>=cutter_screw.screw_data['k']
 return ClearanceHole(cutter_screw,depth=depth,counter_sunk=True,mode=Mode.PRIVATE)
def flush_joint(frame,sheet,thickness,engagement,host,label,size='M2'):
 try:
  joint=make_screw_joint_v1(size=size,at=frame,through=[(sheet,thickness)],engage_depth=engagement,into=host,head='countersunk',material='PLA',label=label)
  hardware=joint.hardware
  standard=CounterSunkScrew('M3-0.5',length=joint.screw_length_mm,fastener_type='iso10642')
 except ScrewJointNotApplicableV1 as exc:
  print('FREE_HEAD_FALLBACK',size,str(exc))
  joint=make_screw_joint_v1(size=size,at=frame,through=[(sheet,thickness)],engage_depth=engagement,into=host,head='socket_cap',material='PLA',label=label)
  standard=CounterSunkScrew('M2-0.4' if size=='M2' else 'M3-0.5',length=joint.screw_length_mm,fastener_type='iso7046' if size=='M2' else 'iso10642')
  k,dk=standard.head_height,standard.head_diameter
  head=standard & Pos(0,0,-k/2)*Box(2*dk,2*dk,k)
  shaft=joint.hardware.moved(frame.inverse()) & Pos(0,0,-(k+joint.screw_length_mm)/2)*Box(dk,dk,joint.screw_length_mm-k)
  hardware=frame*(head+shaft)
 seat=frame*printed_seat(standard,thickness)
 hardware=(hardware.moved(frame.inverse())).moved(Pos(0,0,-countersink_settle_depth)).moved(frame)
 print('FLUSH_JOINT',label,size,joint.screw_length_mm,countersink_settle_depth)
 return joint,seat,hardware
m2_flush_joint=flush_joint

# Shared M3 cover seats and receiver pads. All four remain outside the PCB.
front_module_receiver_width=param('front_module_receiver_width',7.2)
for xx in [-front_module_screw_x,front_module_screw_x]:
 for yy in [front_module_y-front_module_screw_y_offset,front_module_y+front_module_screw_y_offset]:
  body+=Pos(xx,yy,case_top_center-shell_wall/2)*Box(front_module_receiver_width,front_module_receiver_width,shell_wall)
front_module_seats=[]
# Expansion cover now sits on the flat deck (no recessed seat), so the deck prints flat.
front_module=Pos(0,front_module_y,case_top_center)*extrude(RectangleRounded(front_module_width,front_module_depth,1.8),amount=front_module_blank_thickness)
front_module_screws=[]
for xx in [-front_module_screw_x,front_module_screw_x]:
 for yy in [front_module_y-front_module_screw_y_offset,front_module_y+front_module_screw_y_offset]:
  joint,seat,hardware=m2_flush_joint(Location((xx,yy,case_top_center+front_module_blank_thickness)),front_module,front_module_blank_thickness,front_module_screw_engagement,body,'front-module',size='M3')
  if len(joint.bosses.solids())>0:
   body=body+joint.bosses
  body=body-joint.engage_cuts
  assert joint.screw_length_mm==6.0
  front_module_seats.append(seat)
  front_module_screws.append(hardware)

# Raised PCB fixed to the upper-shell beams. Blind receiver: the beam is backed by the
# deck, so the screw must stop inside it instead of running out through the top.
pcb_mount_screws=[]
for sx in [-1,1]:
 xx=sx*pcb_mount_x
 # Preserve the real PCB at Z21.8; the head now bears directly on its
 # unchanged underside mounting land. No washer or printed spacer.
 through_probe=Pos(xx,pcb_mount_y,pcb_mount_bottom_z+PCB_FINISHED_T/2)*Box(pcb_mount_beam_width,pcb_mount_beam_width,PCB_FINISHED_T)
 frame=Location((xx,pcb_mount_y,pcb_mount_bottom_z),(180,0,0))
 try:
  joint=make_screw_joint_v1(size='M2',at=frame,through=[(through_probe,PCB_FINISHED_T)],engage_depth=pcb_mount_engagement,into=body,head='socket_cap',material='PLA',boss='none',termination='blind',label='upper-shell-pcb-direct')
 except ScrewJointNotApplicableV1 as exc:
  print('PCB_DIRECT_FREE_STANDARD_LENGTH',str(exc))
  # Receiver-only calibration gauge. Its lower plane is selected from the
  # library's 4mm solve, not a physical washer or retained printed spacer.
  # Its upper plane is exactly the real PCB/beam interface, so the prior
  # compensated blind receiver is reproduced without moving that interface.
  PCB_RECEIVER_GAUGE_T=2.0
  gauge_frame=frame*Pos(0,0,PCB_RECEIVER_GAUGE_T-PCB_FINISHED_T)
  gauge=Pos(xx,pcb_mount_y,mount_top-PCB_RECEIVER_GAUGE_T/2)*Box(pcb_mount_beam_width,pcb_mount_beam_width,PCB_RECEIVER_GAUGE_T)
  joint=make_screw_joint_v1(size='M2',at=gauge_frame,through=[(gauge,PCB_RECEIVER_GAUGE_T)],engage_depth=pcb_mount_engagement,into=body,head='socket_cap',material='PLA',boss='none',termination='blind',label='pcb-receiver-gauge-only')
  from bd_warehouse.fastener import SocketHeadCapScrew
  PCB_DIRECT_SCREW_LENGTH=3.0  # Explicit standard free implementation after rejection.
  actual=SocketHeadCapScrew('M2-0.4',length=PCB_DIRECT_SCREW_LENGTH,fastener_type='iso4762')
  dk,k=actual.head_diameter,actual.head_height
  head=actual & Pos(0,0,k/2)*Box(2*dk,2*dk,k)
  shaft=joint.hardware.moved(gauge_frame.inverse()) & Pos(0,0,-PCB_DIRECT_SCREW_LENGTH/2)*Box(dk,dk,PCB_DIRECT_SCREW_LENGTH)
  hardware=frame*(head+shaft)
  length=PCB_DIRECT_SCREW_LENGTH
 else:
  hardware=joint.hardware
  length=joint.screw_length_mm
 assert len(joint.bosses.solids())==0
 assert length==3.0, ('Direct PCB screw must be M2x3',length)
 body=body-joint.engage_cuts
 pcb_mount_screws.append(hardware)
 tip_z=pcb_mount_bottom_z+length
 assert tip_z<=case_top_center-1.2, ('pcb screw tip',tip_z)
 print('PCB_DIRECT_MOUNT',xx,pcb_mount_y,dict(length=length,engagement=joint.engage_depth_mm,tip_z=tip_z,spacers=0))
assert case_top_center-(mount_top+pcb_mount_beam_thickness+pcb_mount_cover_clearance)>=1.2-1e-6

# Fan cassette: separate printed U-channel that holds the blower. Printed floor-down:
# floor, two side rails, a bridged roof with the inlet and two full-height ears.
# Two M2 screws go up through the ears into the roof-hung bosses.
cx0=-inner_side+0.3
cx1=fx+shell_fan_cavity_width/2
outer_w=shell_fan_cavity_width+2*shell_fan_rail_thickness
cassette=Pos((cx0+cx1)/2,fy,(fan_cassette_floor_z+c_top)/2)*Box(cx1-cx0,outer_w,c_top-fan_cassette_floor_z)
cassette-=Pos((cx0+cx1)/2,fy,(c_floor_top+c_roof_bot)/2)*Box(cx1-cx0+4,shell_fan_cavity_width,shell_fan_cavity_height)
cassette-=Pos(fx,fy,c_top)*Box(fan_cassette_inlet_width,fan_cassette_inlet_width,4*fan_cassette_roof_thickness)
for s in [-1,1]:
 ey=fy+s*fan_cassette_ear_offset
 y_in=fy+s*(outer_w/2-0.2)
 y_out=ey+s*fan_cassette_ear_width/2
 cassette+=Pos(fan_cassette_ear_x,(y_in+y_out)/2,(fan_cassette_floor_z+c_top)/2)*Box(fan_cassette_ear_width,abs(y_out-y_in),c_top-fan_cassette_floor_z)
# Keep the cassette clear of the narrowed front-left rounded wall.
cassette_wall_gap=param('cassette_wall_gap',0.3)
cassette_inset=shell_wall+cassette_wall_gap
cassette_envelope=extrude(RectangleRounded(case_width-2*cassette_inset,case_depth-2*cassette_inset,case_corner-cassette_inset),amount=case_top_center)
cassette=cassette & cassette_envelope
cooling_screws=[]
for s in [-1,1]:
 joint,seat,hardware=m2_flush_joint(Location((fan_cassette_ear_x,fy+s*fan_cassette_ear_offset,fan_cassette_floor_z),(180,0,0)),cassette,c_top-fan_cassette_floor_z,fan_cassette_engagement,body,'fan-cassette')
 cassette-=seat
 if len(joint.bosses.solids()):body+=joint.bosses
 body-=joint.engage_cuts
 cooling_screws.append(hardware)
 print('FAN_CASSETTE_JOINT',dict(length=joint.screw_length_mm,engagement=joint.engage_depth_mm,boss=joint.boss_length_mm))
assert len(cassette.solids())==1, ('cassette',[round(s.volume,1) for s in cassette.solids()])
fan_corner_pads_width=param('fan_corner_pads_width',2.0)
fan_corner_pads_depth=param('fan_corner_pads_depth',2.0)
fan_corner_pads_thickness=param('fan_corner_pads_thickness',0.5)
FAN_CORNER_OFFSET=6.5 # Nidec nominal mounting corner, standard not editable.
FAN_FRAME=Pos(fx,fy,0)*Rot(0,0,90)
pad_shape=Compound([FAN_FRAME*Pos(sx*FAN_CORNER_OFFSET,sy*FAN_CORNER_OFFSET,c_roof_bot-fan_corner_pads_thickness/2)*Box(fan_corner_pads_width,fan_corner_pads_depth,fan_corner_pads_thickness) for sx,sy in [(-1,-1),(1,-1),(1,1)]])
cassette.color=Color(0.23,0.25,0.27)
pad_shape.color=Color(0.1,0.1,0.1)
publish('fan_cassette',cassette,'Fan cassette',material='pla',role='part')
publish('fan_corner_pads',pad_shape,'Fan corner pads',material='silicone',role='part')
for i,screw in enumerate(cooling_screws):publish('fan_cassette_screw_'+str(i+1),screw,'Fan cassette screw',material='stainless_steel',role='fastener')

# Bottom cover screws thread into the full-height columns.
base_screw_probe=extrude(RectangleRounded(case_width,case_depth,case_corner),amount=base_thickness)
base_mount_screws=[]
base_mount_seats=[]
for i,(xx,yy) in enumerate(base_mount_axes):
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,0),(180,0,0)),base_screw_probe,base_thickness,base_screw_engagement,body,'bottom-cover-'+str(i+1),size='M3')
 if len(joint.bosses.solids()):body=body+joint.bosses
 body=body-joint.engage_cuts
 assert joint.screw_length_mm==6.0
 base_mount_seats.append(seat)
 base_mount_screws.append(hardware)
 print('BOTTOM_JOINT',i+1,dict(axis=(xx,yy),length=joint.screw_length_mm,engagement=joint.engage_depth_mm,boss=joint.boss_length_mm))


# Four concealed screws fasten the screen pod to this roof from the inside.
screen_mount_front_axis_x=param('screen_mount_front_axis_x',34.4)
screen_mount_front_y=param('screen_mount_front_y',4.2)
screen_mount_rear_x=param('screen_mount_rear_x',27.0)
screen_mount_rear_y=param('screen_mount_rear_y',51.0)
screen_mount_front_pad_width=param('screen_mount_front_pad_width',5.6)
screen_mount_rear_pad_width=param('screen_mount_rear_pad_width',6.4)
screen_mount_rear_pad_depth=param('screen_mount_rear_pad_depth',8.0)
screen_mount_front_rib_height=param('screen_mount_front_rib_height',20.0)
screen_mount_rear_rib_height=param('screen_mount_rear_rib_height',20.0)
screen_mount_front_engagement=param('screen_mount_front_engagement',1.2)
screen_mount_rear_engagement=param('screen_mount_rear_engagement',3.0)
screen_mount_driver_shaft_diameter=param('screen_mount_driver_shaft_diameter',2.4)
screen_mount_rear_driver_diameter=param('screen_mount_rear_driver_diameter',3.4)
SCREEN_POD_BASE_Z=27.3 # Existing cad.open placement datum.
screen_mount_axes=[(sx*screen_mount_front_axis_x,screen_mount_front_y) for sx in [-1,1]]+[(sx*screen_mount_rear_x,screen_mount_rear_y) for sx in [-1,1]]
screen_mount_receiver_blanks=[]
screen_mount_engage_cuts=[]
screen_mount_cover_probes=[]
screen_mount_screws=[]
screen_mount_lengths=[]
screen_mount_access_probes=[]
screen_mount_connections={}
for i,(xx,yy) in enumerate(screen_mount_axes):
 front=i<2
 ww=screen_mount_front_pad_width if front else screen_mount_rear_pad_width
 dd=screen_mount_front_pad_width if front else screen_mount_rear_pad_depth
 hh=screen_mount_front_rib_height if front else screen_mount_rear_rib_height
 engagement=screen_mount_front_engagement if front else screen_mount_rear_engagement
 # Rectangular roof tabs are fused into the side and rear deck edges.
 lug=Pos(xx,yy,case_top_center-shell_wall/2)*Box(ww,dd,shell_wall)
 body=body+lug
 # Blind internal access groove. Pi stays on its removable bottom assembly.
 access=Pos(xx,yy,roof_under/2)*Cylinder((screen_mount_driver_shaft_diameter if front else screen_mount_rear_driver_diameter)/2,roof_under)
 body=body-access
 screen_mount_access_probes.append(access)
 # Shared interface tooling; the actual receiver wall tabs belong to fascia.
 receiver=Pos(xx,yy,(case_top_center+SCREEN_POD_BASE_Z+hh)/2)*Box(ww,dd,SCREEN_POD_BASE_Z+hh-case_top_center)
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,roof_under),(180,0,0)),body,shell_wall,engagement,receiver,'screen-pod-'+str(i+1),size='M2' if front else 'M3')
 assert len(joint.bosses.solids())==0, 'Receiver wall tab supplies the blind-hole depth'
 body=body-seat
 assert joint.screw_length_mm==(4.0 if front else 6.0)
 screen_mount_receiver_blanks.append(receiver)
 screen_mount_engage_cuts.append(joint.engage_cuts)
 end=joint.engage_cuts.bounding_box().max.Z
 screen_mount_cover_probes.append(Pos(xx,yy,end+0.6)*Cylinder(1.2,1.2))
 screen_mount_screws.append(hardware)
 screen_mount_lengths.append(joint.screw_length_mm)
 screen_mount_connections['pod_to_shell_'+str(i+1)]='printed-screw-joint-v1 receiver; free standard head after kit rejection when needed; compensated seat'
assert len(screen_mount_connections)==4
assert case_width/2-(screen_mount_front_axis_x+screen_mount_driver_shaft_diameter/2)>=1.5-1e-6

# Check the final shell, including screw columns and other later additions.
for label,probe in plug_reserves:
 overlap=body & probe
 vol=0.0 if overlap is None else (sum(s.volume for s in overlap if s is not None) if isinstance(overlap,ShapeList) else overlap.volume)
 print('SIDE_PLUG_APPROACH',label,vol)
 assert vol<0.00001,(label,'moulded shoulder blocked by final shell',vol)
assert len(body.solids())==1, ('final body',[round(s.volume,1) for s in body.solids()])
body.color=Color(0.88,0.86,0.79)
publish('shell',body,'Upper shell',material='pla',role='part')
for i,screw in enumerate(front_module_screws):
 publish('front_module_screw_'+str(i+1),screw,'M3 module screw',role='fastener')
for i,screw in enumerate(pcb_mount_screws):
 publish('pcb_mount_screw_'+str(i+1),screw,'PCB mount screw',material='stainless_steel',role='fastener')
for i,screw in enumerate(base_mount_screws):publish('base_mount_screw_'+str(i+1),screw,'Bottom cover screw',material='stainless_steel',role='fastener')
for i,screw in enumerate(screen_mount_screws):
 publish('screen_mount_screw_'+str(i+1),screw,'Screen mount '+('M2' if i<2 else 'M3')+' x '+str(screen_mount_lengths[i]),material='stainless_steel',role='fastener')
