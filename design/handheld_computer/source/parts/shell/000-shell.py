# cell: shell
# cell: shell
# cell: shell
# cell: shell
# cell: shell
# cell: shell
# cell: shell
# cell: shell
# Roof-down printing; bottom cover is closure only.
case_width=param('case_width',85.0)
pi_offset_x=param('pi_offset_x',-5.0)
pi_stack_lift=param('pi_stack_lift',1.3)
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
shell_passage_front=param('shell_passage_front',-3.5)
shell_passage_rear=param('shell_passage_rear',48.5)
shell_passage_depth=shell_passage_rear-shell_passage_front
shell_passage_y=(shell_passage_rear+shell_passage_front)/2
shell_passage_radius=param('shell_passage_radius',4.5)
shell_rj45_x=param('shell_rj45_x',-6.75)+pi_offset_x
shell_rj45_z=param('shell_rj45_z',14.0)+pi_stack_lift
shell_rj45_width=param('shell_rj45_width',17.0)
shell_rj45_height=param('shell_rj45_height',15.0)
shell_usb_mid_x=param('shell_usb_mid_x',12.0)+pi_offset_x
shell_usb_mid_z=param('shell_usb_mid_z',15.0)+pi_stack_lift
shell_usb_mid_width=param('shell_usb_mid_width',15.0)
shell_usb_mid_height=param('shell_usb_mid_height',17.0)
shell_usb_right_x=param('shell_usb_right_x',30.0)+pi_offset_x
shell_usb_right_z=param('shell_usb_right_z',14.5)+pi_stack_lift
shell_usb_right_width=param('shell_usb_right_width',16.0)
shell_usb_right_height=param('shell_usb_right_height',18.0)
shell_hdmi1_y=param('shell_hdmi1_y',-4.5)
shell_hdmi2_y=param('shell_hdmi2_y',9.0)
shell_hdmi_z=param('shell_hdmi_z',8.6)+pi_stack_lift
shell_hdmi_width=param('shell_hdmi_width',7.4)
shell_hdmi_height=param('shell_hdmi_height',4.2)
shell_jack_y=param('shell_jack_y',23.5)
PI_AUDIO_CENTER_Z_UNLIFTED=10.0 # Placed STEP circular face centre11.3 at lift1.3.
shell_jack_z=PI_AUDIO_CENTER_Z_UNLIFTED+pi_stack_lift
shell_jack_diameter=param('shell_jack_diameter',7.6)
shell_port_radius=param('shell_port_radius',0.5)
shell_pi_usb_c_y=param('shell_pi_usb_c_y',-19.3)
PI_USBC_CENTER_Z_UNLIFTED=8.58 # Placed STEP opening centre9.88 at lift1.3.
shell_pi_usb_c_z=PI_USBC_CENTER_Z_UNLIFTED+pi_stack_lift
shell_pi_usb_c_width=param('shell_pi_usb_c_width',10.2)
shell_pi_usb_c_height=param('shell_pi_usb_c_height',5.2)
shell_pi_groove_clearance=param('shell_pi_groove_clearance',0.3)
shell_lcd_mount_x=param('shell_lcd_mount_x',20.0)
shell_lcd_mount_y_front=param('shell_lcd_mount_y_front',-28.0)
shell_lcd_mount_y_rear=param('shell_lcd_mount_y_rear',25.5)
shell_lcd_well_width=param('shell_lcd_well_width',7.0)
shell_lcd_well_depth=param('shell_lcd_well_depth',7.0)
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
# Shared exterior profile: shallow lower facet plus45deg bottom-cover bevel.
shell_lower_visual_inset=param('shell_lower_visual_inset',0.3)
shell_lower_visual_height=param('shell_lower_visual_height',6.0)
base_visual_bevel=param('base_visual_bevel',1.2)
shell_front_edge_bevel=param('shell_front_edge_bevel',1.6)
shell_bevel_fade_start_y=param('shell_bevel_fade_start_y',-18.0)
shell_bevel_fade_end_y=param('shell_bevel_fade_end_y',-10.0)
shell_lower_inner_shift=max(0.0,shell_lower_visual_inset-(shell_wall-shell_edge_radius-2.0))
assert shell_wall-shell_lower_visual_inset+shell_lower_inner_shift-shell_edge_radius>=2.0-1e-6
assert (2*shell_wall-shell_front_edge_bevel)/(2**0.5)>=2.0
assert base_visual_bevel<base_thickness
assert shell_lower_visual_height>0 and shell_bevel_fade_start_y<shell_bevel_fade_end_y
def visual_section(z,inset):
 return Pos(0,0,z)*RectangleRounded(case_width-2*inset,case_depth-2*inset,case_corner-inset)
lower_visual_envelope=loft([
 visual_section(-1,shell_lower_visual_inset+base_visual_bevel),
 visual_section(0,shell_lower_visual_inset+base_visual_bevel),
 visual_section(base_visual_bevel,shell_lower_visual_inset),
 visual_section(shell_lower_z,shell_lower_visual_inset),
 visual_section(shell_lower_z+shell_lower_visual_height,0),
 visual_section(case_top_center+1,0)],ruled=True)
upper_visual_blank=extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center)
upper_visual_beveled=chamfer(upper_visual_blank.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1],shell_front_edge_bevel)
upper_edge_waste=upper_visual_blank-upper_visual_beveled
# Tangent cubic runout: the bevel depth eases continuously to zero beside
# the pod's front corner, avoiding the former triangular planar termination.
fade_span=shell_bevel_fade_end_y-shell_bevel_fade_start_y
fade_low=case_top_center-shell_front_edge_bevel
fade_ceiling=case_top_center+2*shell_front_edge_bevel
fade_profile=Face(Wire([
 Edge.make_line((-case_depth,fade_low,0),(shell_bevel_fade_start_y,fade_low,0)),
 Edge.make_bezier((shell_bevel_fade_start_y,fade_low,0),(shell_bevel_fade_start_y+fade_span/3,fade_low,0),(shell_bevel_fade_end_y-fade_span/3,case_top_center,0),(shell_bevel_fade_end_y,case_top_center,0)),
 Edge.make_line((shell_bevel_fade_end_y,case_top_center,0),(shell_bevel_fade_end_y,fade_ceiling,0)),
 Edge.make_line((shell_bevel_fade_end_y,fade_ceiling,0),(-case_depth,fade_ceiling,0)),
 Edge.make_line((-case_depth,fade_ceiling,0),(-case_depth,fade_low,0))
]))
# Extrude along the45-degree bevel direction, so the bevel width and depth
# shrink together. A normal extrusion leaves an unwanted flat outer shelf.
fade_right=Pos(case_width/2,0,0)*extrude(Plane.YZ*fade_profile,amount=2*shell_front_edge_bevel,both=True,dir=(-1,0,1))
fade_left=Pos(-case_width/2,0,0)*extrude(Plane.YZ*fade_profile,amount=2*shell_front_edge_bevel,both=True,dir=(1,0,1))
fade_front=Pos(0,(-case_depth+shell_bevel_fade_start_y)/2,case_top_center)*Box(2*case_width,case_depth+shell_bevel_fade_start_y,4*shell_front_edge_bevel)
upper_edge_waste=upper_edge_waste & (fade_front+fade_right+fade_left)
outer=Pos(0,0,shell_lower_z)*extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center-shell_lower_z)
outer=fillet(outer.edges().filter_by(Plane.XY).group_by(Axis.Z)[0],shell_edge_radius)
# Move the lower inner wall with the inset exterior, retaining2mm nominal wall.
def lower_inner_section(z,shift):
 return Pos(0,0,z)*RectangleRounded(case_width-2*(shell_wall+shift),case_depth-2*(shell_wall+shift),case_corner-shell_wall-shift)
inner=loft([lower_inner_section(0,shell_lower_inner_shift),lower_inner_section(shell_lower_z,shell_lower_inner_shift),lower_inner_section(shell_lower_z+shell_lower_visual_height,0),lower_inner_section(roof_under,0)],ruled=True)
lower_inner_void=inner
body=outer-inner
assert len(body.solids())==1, ('shell body',len(body.solids()))
PCB_FINISHED_T=0.8 # Ordered pi_baseboard_lite; original M2 clearance holes 2.2mm.
PCB_LEFT_EDGE=-23.5
mount_top=pcb_mount_bottom_z+PCB_FINISHED_T
beam_tip=pcb_mount_x-pcb_mount_beam_width/2
for sx in [-1,1]:
 outer_root=inner_side+shell_wall/2
 body+=Pos(sx*(beam_tip+outer_root)/2,pcb_mount_y,mount_top+max(pcb_mount_beam_thickness+0.2,roof_under-mount_top+0.2)/2)*Box(outer_root-beam_tip,pcb_mount_beam_width,max(pcb_mount_beam_thickness+0.2,roof_under-mount_top+0.2))
base_mount_axes=[(base_mount_left_front_x,base_mount_left_front_y),(base_mount_front_x,base_mount_front_y),(base_mount_left_rear_x,base_mount_left_rear_y),(base_mount_right_mid_x,base_mount_right_mid_y)]
column_envelope=extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center)
for xx,yy in base_mount_axes:
 sx=1 if xx>0 else -1
 tip=abs(xx)-shell_base_pad_width/2
 root=case_width/2-shell_wall/2
 column=Pos(sx*(tip+root)/2,yy,(base_thickness+roof_under+0.2)/2)*Box(root-tip,shell_base_pad_width,roof_under+0.2-base_thickness)
 body+=column & column_envelope
body-=Pos(0,shell_passage_y,roof_under)*extrude(RectangleRounded(shell_passage_width,shell_passage_depth,shell_passage_radius),amount=2*shell_wall)
aperture=Pos(0,front_module_y,roof_under-0.5)*extrude(RectangleRounded(front_module_aperture_width,front_module_aperture_depth,1.5),amount=shell_wall+1.0)
for sx in [-1,1]:
 aperture-=Pos(sx*(beam_tip+front_module_aperture_width/2+1)/2,pcb_mount_y,case_top_center)*Box(front_module_aperture_width/2+1-beam_tip,pcb_mount_beam_width,10)
body-=aperture
rear_ports=[(shell_rj45_x,shell_rj45_z,shell_rj45_width,shell_rj45_height),(shell_usb_mid_x,shell_usb_mid_z,shell_usb_mid_width,shell_usb_mid_height),(shell_usb_right_x,shell_usb_right_z,shell_usb_right_width,shell_usb_right_height)]
rear_window_left=min(x-w/2 for x,z,w,h in rear_ports)
rear_window_right=max(x+w/2 for x,z,w,h in rear_ports)
rear_window_top=max(z+h/2 for x,z,w,h in rear_ports)
rear_window_sill=min(z-h/2 for x,z,w,h in rear_ports)
rear_window_center=(rear_window_left+rear_window_right)/2
rear_window_width=rear_window_right-rear_window_left
port_bottom=shell_lower_z-1.0
body-=Pos(rear_window_center,case_depth/2,(rear_window_top+port_bottom)/2)*extrude(Plane.XZ*RectangleRounded(rear_window_width,rear_window_top-port_bottom,shell_port_radius),amount=4*shell_wall,both=True)
assert case_top_center-rear_window_top>=2.0
print('SHARED_REAR_WINDOW',dict(left=rear_window_left,right=rear_window_right,top=rear_window_top,sill=rear_window_sill,header_height=case_top_center-rear_window_top))
rear_divider_width=param('rear_divider_width',2.4)
rear_divider_depth=param('rear_divider_depth',4.0)
rear_divider_root_depth=param('rear_divider_root_depth',8.0)
rear_divider_tip_engagement=param('rear_divider_tip_engagement',1.2)
rear_divider_shoulder_z=param('rear_divider_shoulder_z',7.5)+pi_stack_lift
rear_divider_x=[]
for left,right in zip(sorted(rear_ports),sorted(rear_ports)[1:]):
 gap_left=left[0]+left[2]/2
 gap_right=right[0]-right[2]/2
 assert gap_right-gap_left>=rear_divider_width
 rear_divider_x.append((gap_left+gap_right)/2)
rear_divider_tip_z=rear_window_sill-rear_divider_tip_engagement
rear_divider_rear_y=case_depth/2
rear_divider_tip_inner_y=rear_divider_rear_y-shell_wall
rear_divider_deep_y=rear_divider_rear_y-rear_divider_depth
rear_divider_step=rear_divider_depth-shell_wall
assert rear_divider_step>=0 and rear_divider_shoulder_z>7.1
rear_divider_stems=[]
rear_divider_gussets=[]
for xx in rear_divider_x:
 profile=Plane.YZ*Polygon((rear_divider_tip_inner_y,rear_divider_tip_z),(rear_divider_rear_y,rear_divider_tip_z),(rear_divider_rear_y,case_top_center),(rear_divider_deep_y,case_top_center),(rear_divider_deep_y,rear_divider_shoulder_z+rear_divider_step),(rear_divider_tip_inner_y,rear_divider_shoulder_z),align=None)
 stem=Pos(xx,0,0)*extrude(profile,amount=rear_divider_width/2,both=True)
 gusset=Pos(xx,0,0)*extrude(Plane.YZ*Polygon((rear_divider_rear_y-rear_divider_root_depth,case_top_center),(rear_divider_rear_y,case_top_center),(rear_divider_rear_y,case_top_center-rear_divider_root_depth),align=None),amount=rear_divider_width/2,both=True)
 rear_divider_stems.append(stem)
 rear_divider_gussets.append(gusset)
 body=body+stem+gusset
print('ROOF_BACKED_REAR_DIVIDERS',dict(x=rear_divider_x,width=rear_divider_width,depth=rear_divider_depth,root_depth=rear_divider_root_depth,tip_z=rear_divider_tip_z))
# Recessed port wells: wide mouth for the moulded cable shoulder, backed
# by a closed1.2mm web with only the true connector aperture cut through it.
from portcut import port_cut,PortSpec
shell_usbc_shoulder_width=param('shell_usbc_shoulder_width',13.0)
shell_hdmi_shoulder_width=param('shell_hdmi_shoulder_width',12.0)
shell_plug_shoulder_height=param('shell_plug_shoulder_height',7.0)
shell_audio_shoulder_diameter=param('shell_audio_shoulder_diameter',11.0)
shell_usbc_entry_y_flare=param('shell_usbc_entry_y_flare',0.5)
shell_plug_entry_z_flare=param('shell_plug_entry_z_flare',0.3)
shell_plug_entry_radius=param('shell_plug_entry_radius',1.0)
side_port_web=param('side_port_web',1.2)
side_port_socket_face_air=param('side_port_socket_face_air',0.3)
side_port_hdmi_front_overhang=param('side_port_hdmi_front_overhang',1.2)
side_port_usb_extra_clearance=param('side_port_usb_extra_clearance',0.1)
assert side_port_web>=1.2 and 0.2<=side_port_socket_face_air<=0.5
outer_port_x=case_width/2
# USB-C and AV fronts measured on the bound Pi STEP. HDMI locations/3mm
# height from official RP-008343-DS p1; its detailed STEP bodies are absent.
# HDMI front overhang1.2mm is a provisional default, not a measured value.
pi_board_edge_x=39.0+pi_offset_x
usbc_socket_front_x=40.2+pi_offset_x
audio_socket_front_x=41.5+pi_offset_x
hdmi_socket_front_x=pi_board_edge_x+side_port_hdmi_front_overhang
hdmi_clear_w=max(shell_hdmi_width,shell_hdmi_shoulder_width)
hdmi_clear_h=max(shell_hdmi_height,shell_plug_shoulder_height)
usbc_clear_w=max(shell_pi_usb_c_width,shell_usbc_shoulder_width)
usbc_clear_h=max(shell_pi_usb_c_height,shell_plug_shoulder_height)
audio_clear_d=max(shell_jack_diameter,shell_audio_shoulder_diameter)
side_panel_thickness=param('side_panel_thickness',2.0)
side_panel_width=param('side_panel_width',72.0)
side_panel_height=param('side_panel_height',17.7)
side_panel_center_y=param('side_panel_center_y',0.5)
side_panel_bottom_z=param('side_panel_bottom_z',3.8)
side_panel_corner=param('side_panel_corner',2.0)
side_panel_fit=param('side_panel_fit',0.25)
side_panel_back_x=outer_port_x-side_panel_thickness
side_panel_center_z=side_panel_bottom_z+side_panel_height/2
side_panel_form=Pos(side_panel_back_x,side_panel_center_y,side_panel_center_z)*extrude(Plane.YZ*RectangleRounded(side_panel_width,side_panel_height,side_panel_corner),amount=side_panel_thickness)
side_panel_blanks=[side_panel_form]
plug_reserves=[]
side_port_floor_guards=[]
side_port_layout=[]
side_port_pockets=[]
side_port_bores=[]
def recessed_side_port(label,yy,zz,width,height,socket_x,kind,body_width,body_height,flare=0.0,circular=False):
 floor=socket_x+side_port_socket_face_air
 back=floor-side_port_web
 assert floor<outer_port_x-0.8 and back>=pi_board_edge_x+0.3-1e-6
 if circular:
  outside=Circle((width+2*side_port_web)/2)
  inner=Circle(width/2)
  mouth_cut=Pos(floor,yy,zz)*extrude(Plane.YZ*inner,amount=outer_port_x+2-floor)
 else:
  outside=RectangleRounded(width+2*side_port_web,height+2*side_port_web,shell_plug_entry_radius+side_port_web)
  sections=[
   Pos(floor,yy,zz)*(Plane.YZ*RectangleRounded(width,height,shell_plug_entry_radius)),
   Pos(outer_port_x,yy,zz)*(Plane.YZ*RectangleRounded(width+2*flare,height+2*shell_plug_entry_z_flare,shell_plug_entry_radius)),
   Pos(outer_port_x+2,yy,zz)*(Plane.YZ*RectangleRounded(width+2*flare,height+2*shell_plug_entry_z_flare,shell_plug_entry_radius))]
  mouth_cut=loft(sections,ruled=True)
 blank=Pos(back,yy,zz)*extrude(Plane.YZ*outside,amount=outer_port_x-back)
 aperture=port_cut(kind,at=(floor,yy,zz),facing='+X',depth=side_port_web+0.2,clearance=side_port_usb_extra_clearance if label=='USB-C' else 0.0)
 floor_guard=Pos(back,yy,zz)*extrude(Plane.YZ*outside,amount=side_port_web)-aperture
 side_port_floor_guards.append((label,floor_guard))
 side_port_pockets.append(mouth_cut)
 side_port_bores.append(aperture)
 side_port_layout.append(dict(label=label,center_yz=[yy,zz],socket_front_x=socket_x,floor_x=floor,back_x=back,recess_mm=outer_port_x-floor,web_mm=side_port_web))
 # Moulded shoulder begins at the recessed floor; the metal nose reaches
 #0.3mm farther to the receptacle. No physical cable model is claimed.
 probe_start=floor+0.01
 probe_end=outer_port_x+12
 if circular:
  probe=Pos((probe_start+probe_end)/2,yy,zz)*Rot(0,90,0)*Cylinder(body_width/2,probe_end-probe_start)
 else:
  probe=Pos((probe_start+probe_end)/2,yy,zz)*Box(probe_end-probe_start,body_width,body_height)
 plug_reserves.append((label,probe))
 return blank
for i,y in enumerate([shell_hdmi1_y,shell_hdmi2_y]):
 blank=recessed_side_port('micro-HDMI'+str(i+1),y,shell_hdmi_z,hdmi_clear_w,hdmi_clear_h,hdmi_socket_front_x,PortSpec('rounded',shell_hdmi_width,shell_hdmi_height,shell_port_radius),11.0,6.0)
 side_panel_blanks.append(blank)
side_panel_blanks.append(recessed_side_port('USB-C',shell_pi_usb_c_y,shell_pi_usb_c_z,usbc_clear_w,usbc_clear_h,usbc_socket_front_x,'usb_c',12.35,6.5,shell_usbc_entry_y_flare))
side_panel_blanks.append(recessed_side_port('3.5mm audio',shell_jack_y,shell_jack_z,audio_clear_d,audio_clear_d,audio_socket_front_x,'audio_3_5mm',10.0,10.0,circular=True))

side_panel_blank=side_panel_blanks[0].fuse(*side_panel_blanks[1:])
for pocket in side_port_pockets:side_panel_blank=side_panel_blank-pocket
for aperture in side_port_bores:side_panel_blank=side_panel_blank-aperture
side_panel_blank=side_panel_blank & lower_visual_envelope
# A shallow outside seat holds a separate, sideways-removable port frame.
# The service opening below it stays open to the bottom, so the Pi can still
# withdraw vertically after removing this frame and the bottom cover.
side_panel_seat=Pos(side_panel_back_x,side_panel_center_y,side_panel_center_z)*extrude(Plane.YZ*RectangleRounded(side_panel_width+2*side_panel_fit,side_panel_height+2*side_panel_fit,side_panel_corner+side_panel_fit),amount=side_panel_thickness+2)
side_service_y_min=-27.6
side_service_y_max=30.8
side_service_top=18.4
side_service_bottom=-10.0
side_service_window=Pos(pi_board_edge_x-0.1,(side_service_y_min+side_service_y_max)/2,(side_service_top+side_service_bottom)/2)*extrude(Plane.YZ*RectangleRounded(side_service_y_max-side_service_y_min,side_service_top-side_service_bottom,1.2),amount=outer_port_x+2-pi_board_edge_x+0.1)
body=body-side_panel_seat-side_service_window
for label,guard in side_port_floor_guards:
 missing=guard-side_panel_blank
 v=0.0 if not missing else missing.volume
 assert v<1e-5,(label,'port frame surround breached',v)
hdmi_web=abs(shell_hdmi2_y-shell_hdmi1_y)-hdmi_clear_w
usb_hdmi_web=(shell_hdmi1_y-shell_pi_usb_c_y)-(hdmi_clear_w+usbc_clear_w+2*shell_usbc_entry_y_flare)/2
assert hdmi_web>=1.5-1e-6 and usb_hdmi_web>=1.5-1e-6
assert shell_jack_z-audio_clear_d/2-shell_lower_z>=1.2
print('SIDE_PORT_WELLS',side_port_layout)
print('SIDE_PORT_RESERVES',dict(usb_c_bore=[shell_usbc_shoulder_width,shell_plug_shoulder_height],hdmi_bore=[shell_hdmi_shoulder_width,shell_plug_shoulder_height],audio_bore=shell_audio_shoulder_diameter,hdmi_web=hdmi_web,usb_hdmi_web=usb_hdmi_web))
PI_REAR_CORNER_RELIEF=(35.5+pi_offset_x,39.5+pi_offset_x,51.3,55.3,7.6+pi_stack_lift)
rx0,rx1,ry0,ry1,rz1=PI_REAR_CORNER_RELIEF
body-=Pos((rx0+rx1)/2,(ry0+ry1)/2,(port_bottom+rz1)/2)*Box(rx1-rx0,ry1-ry0,rz1-port_bottom)
SCREEN_CENTER_Y=21.521201483
SCREEN_CENTER_Z=34.510909266
SCREEN_FRAME=Pos(0,SCREEN_CENTER_Y,SCREEN_CENTER_Z)*Rot(13,0,0)
# The upright front skirt uses the main aperture, without the former front screw wells.
for xx in [-shell_lcd_mount_x,shell_lcd_mount_x]:
 body-=SCREEN_FRAME*Pos(xx,shell_lcd_mount_y_rear,-8)*Box(shell_lcd_well_width,shell_lcd_well_depth,20)
PCB_FRONT_BODY_BOUNDS=[[-13.650013,-26.5,21.794999,-12.350013,-24.5,23.094999],[13.349987,-26.5,21.794999,14.649987,-24.5,23.094999],[5.349987,-26.5,21.794999,6.649987,-24.5,23.094999],[5.6,10.25,21.794999,6.4,11.85,22.594999],[-5.650013,-26.5,21.794999,-4.350013,-24.5,23.094999],[9.19,-30.405,21.794999,10.81,-29.595,22.244999],[-13.4,10.25,21.794999,-12.6,11.85,22.594999],[-0.81,-18.405,21.794999,0.81,-17.595,22.244999],[-10.506315,10.5,21.794999,-4.49371,15.5,22.895082],[-12.81,16.095,21.794999,-11.19,16.905,22.244999],[-9.81,-30.405,21.794999,-8.19,-29.595,22.244999],[8.493698,-27.949987,21.794999,11.506302,-25.049987,23.045082],[-2.8,10.1,21.794999,-1.2,10.9,22.594999],[8.55,-18.4,21.794999,11.45,-15.6,23.344999],[9.19,-13.405,21.794999,10.81,-12.595,22.244999],[11.19,16.095,21.794999,12.81,16.905,22.244999],[-10.506302,-27.949987,21.794999,-7.493698,-25.049987,23.045082],[-0.81,16.095,21.794999,0.81,16.905,22.244999],[-4.81,16.095,21.794999,-3.19,16.905,22.244999],[-6.81,-20.405,21.794999,-5.19,-19.595,22.244999],[-8.81,16.095,21.794999,-7.19,16.905,22.244999],[-10.45,-18.4,21.794999,-7.55,-15.6,23.344999],[-9.81,-13.405,21.794999,-8.19,-12.595,22.244999],[12.19,-20.405,21.794999,13.81,-19.595,22.244999],[8.493685,10.5,21.794999,14.50629,15.5,22.895082],[1,9.850013,21.794999,3,11.150013,23.094999],[5.349987,-19,21.794999,6.649987,-17,23.094999],[-13.650013,-19,21.794999,-12.350013,-17,23.094999]]
for bx0,by0,bz0,bx1,by1,bz1 in PCB_FRONT_BODY_BOUNDS:
 body-=Pos((bx0+bx1)/2,(by0+by1)/2,(bz0+bz1)/2+pcb_mount_bottom_z-21.0)*Box(bx1-bx0+2*shell_pcb_top_air,by1-by0+2*shell_pcb_top_air,bz1-bz0+2*shell_pcb_top_air)
assert max(b[5] for b in PCB_FRONT_BODY_BOUNDS)+shell_pcb_top_air+pcb_mount_bottom_z-21.0<=case_top_center-2.0+1e-6
for sx in [-1,1]:
 bearing=Pos(sx*pcb_mount_x,pcb_mount_y,mount_top+0.1)*(Cylinder(2.75,0.2)-Cylinder(1.1,0.2))
 absent=bearing-body
 assert absent.volume<1e-5,('PCB bearing ring interrupted',sx,absent.volume)
gpio_tail_roof_air=param('gpio_tail_roof_air',0.5)
GPIO_TAIL_LENGTH=3.5
gpio_tail_ceiling=pcb_mount_bottom_z+GPIO_TAIL_LENGTH+gpio_tail_roof_air
assert case_top_center-gpio_tail_ceiling>=2.0-1e-6, 'GPIO roof skin below2mm'
body-=Pos(-18.5,2,(mount_top+gpio_tail_ceiling)/2)*Box(6,52,gpio_tail_ceiling-mount_top)
shell_vent_center_y=param('shell_vent_center_y',-41.0)
shell_cooling_slot_width=param('shell_cooling_slot_width',2.4)
shell_cooling_slot_bridge=param('shell_cooling_slot_bridge',2.0)
shell_cooling_slot_count=param('shell_cooling_slot_count',4)
shell_cooling_exhaust_z=param('shell_cooling_exhaust_z',13.25)
shell_cooling_exhaust_height=param('shell_cooling_exhaust_height',4.5)
for i in range(int(shell_cooling_slot_count)):
 offset=(i-(int(shell_cooling_slot_count)-1)/2)*(shell_cooling_slot_width+shell_cooling_slot_bridge)
 body-=Pos(-case_width/2,shell_vent_center_y+offset,shell_cooling_exhaust_z)*extrude(Plane.YZ*SlotOverall(shell_cooling_exhaust_height,shell_cooling_slot_width,rotation=90),amount=4*shell_wall,both=True)
assert len(body.solids())==1, ('after cuts',[round(s.volume,1) for s in body.solids()])
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
from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole, SocketHeadCapScrew
countersink_print_radial_allowance=param('countersink_print_radial_allowance',0.2)
countersink_settle_depth=countersink_print_radial_allowance
def printed_seat(standard,depth):
 cutter_screw=CounterSunkScrew(standard.thread_size,length=standard.length,fastener_type=standard.fastener_type)
 cutter_screw.screw_data=dict(cutter_screw.screw_data)
 cutter_screw.screw_data['dk']+=2*countersink_print_radial_allowance
 cutter_screw.screw_data['k']+=countersink_print_radial_allowance
 assert depth>=cutter_screw.screw_data['k']
 return ClearanceHole(cutter_screw,depth=depth,counter_sunk=True,mode=Mode.PRIVATE)
def flush_joint(frame,sheet,thickness,engagement,host,label,size='M2.5'):
 joint=make_screw_joint_v1(size=size,at=frame,through=[(sheet,thickness)],seat='countersink',engage_depth=engagement,into=host,head='countersunk',head_recess=countersink_settle_depth,material='PLA',label=label)
 seat=joint.through_cuts[0]
 hardware=joint.hardware
 print('FLUSH_JOINT',label,size,joint.screw_length_mm,joint.head_above_surface_mm,joint.seat_opening_diameter_mm)
 return joint,seat,hardware
m2_flush_joint=flush_joint
front_module_receiver_width=param('front_module_receiver_width',7.2)
for xx in [-front_module_screw_x,front_module_screw_x]:
 for yy in [front_module_y-front_module_screw_y_offset,front_module_y+front_module_screw_y_offset]:
  body+=Pos(xx,yy,case_top_center-shell_wall/2)*Box(front_module_receiver_width,front_module_receiver_width,shell_wall)
front_module_seats=[]
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
pcb_mount_screws=[]
for sx in [-1,1]:
 xx=sx*pcb_mount_x
 through_probe=Pos(xx,pcb_mount_y,pcb_mount_bottom_z+PCB_FINISHED_T/2)*Box(pcb_mount_beam_width,pcb_mount_beam_width,PCB_FINISHED_T)
 frame=Location((xx,pcb_mount_y,pcb_mount_bottom_z),(180,0,0))
 try:
  joint=make_screw_joint_v1(size='M2',at=frame,through=[(through_probe,PCB_FINISHED_T)],seat='surface',engage_depth=pcb_mount_engagement,into=body,head='socket_cap',material='PLA',boss='none',termination='blind',label='upper-shell-pcb-direct')
 except ScrewJointNotApplicableV1 as exc:
  print('PCB_DIRECT_FREE_STANDARD_LENGTH',str(exc))
  PCB_RECEIVER_GAUGE_T=2.0
  gauge_frame=frame*Pos(0,0,PCB_RECEIVER_GAUGE_T-PCB_FINISHED_T)
  gauge=Pos(xx,pcb_mount_y,mount_top-PCB_RECEIVER_GAUGE_T/2)*Box(pcb_mount_beam_width,pcb_mount_beam_width,PCB_RECEIVER_GAUGE_T)
  joint=make_screw_joint_v1(size='M2',at=gauge_frame,through=[(gauge,PCB_RECEIVER_GAUGE_T)],seat='surface',engage_depth=pcb_mount_engagement,into=body,head='socket_cap',material='PLA',boss='none',termination='blind',label='pcb-receiver-gauge-only')
  PCB_DIRECT_SCREW_LENGTH=3.0
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
 assert length==3.0, ('Ordered PCB screw must remain M2x3',length)
 body=body-joint.engage_cuts
 pcb_mount_screws.append(hardware)
 tip_z=pcb_mount_bottom_z+length
 assert tip_z<=case_top_center-1.2, ('pcb screw tip',tip_z)
 print('PCB_DIRECT_MOUNT',xx,pcb_mount_y,dict(length=length,engagement=joint.engage_depth_mm,tip_z=tip_z,spacers=0))
assert case_top_center-(mount_top+pcb_mount_beam_thickness+pcb_mount_cover_clearance)>=1.2-1e-6
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
screen_mount_front_axis_x=param('screen_mount_front_axis_x',34.4)
screen_mount_front_y=param('screen_mount_front_y',9.2)
screen_mount_rear_x=param('screen_mount_rear_x',27.0)
screen_mount_rear_y=param('screen_mount_rear_y',51.0)
screen_mount_front_pad_width=param('screen_mount_front_pad_width',6.4)
screen_mount_rear_pad_width=param('screen_mount_rear_pad_width',6.4)
screen_mount_rear_pad_depth=param('screen_mount_rear_pad_depth',8.0)
screen_mount_front_rib_height=param('screen_mount_front_rib_height',20.0)
screen_mount_rear_rib_height=param('screen_mount_rear_rib_height',20.0)
screen_mount_front_engagement=param('screen_mount_front_engagement',1.2)
screen_mount_rear_engagement=param('screen_mount_rear_engagement',3.0)
screen_mount_driver_shaft_diameter=param('screen_mount_driver_shaft_diameter',2.4)
screen_mount_rear_driver_diameter=param('screen_mount_rear_driver_diameter',3.4)
SCREEN_POD_BASE_Z=27.3
# Offset the left rear pod joint from the bottom-cover column and carrier lug.
screen_mount_left_rear_x=param('screen_mount_left_rear_x',-26.5)
screen_mount_left_rear_y=param('screen_mount_left_rear_y',47.0)
screen_mount_left_rear_access_diameter=param('screen_mount_left_rear_access_diameter',7.0)
screen_mount_axes=[(sx*screen_mount_front_axis_x,screen_mount_front_y) for sx in [-1,1]]+[(screen_mount_left_rear_x,screen_mount_left_rear_y),(screen_mount_rear_x,screen_mount_rear_y)]
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
 lug=Pos(xx,yy,case_top_center-shell_wall/2)*Box(ww,dd,shell_wall)
 body=body+lug
 access_diameter=screen_mount_driver_shaft_diameter if front else (screen_mount_left_rear_access_diameter if i==2 else screen_mount_rear_driver_diameter)
 access=Pos(xx,yy,roof_under/2)*Cylinder(access_diameter/2,roof_under)
 body=body-access
 screen_mount_access_probes.append(access)
 receiver=Pos(xx,yy,(case_top_center+SCREEN_POD_BASE_Z+hh)/2)*Box(ww,dd,SCREEN_POD_BASE_Z+hh-case_top_center)
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,roof_under),(180,0,0)),body,shell_wall,engagement,receiver,'screen-pod-'+str(i+1),size='M2.5' if front else 'M3')
 assert len(joint.bosses.solids())==0, 'Receiver wall tab supplies the blind-hole depth'
 body=body-seat
 assert joint.screw_length_mm==(4.0 if front else 6.0)
 screen_mount_receiver_blanks.append(receiver)
 screen_mount_engage_cuts.append(joint.engage_cuts)
 end=joint.engage_cuts.bounding_box().max.Z
 screen_mount_cover_probes.append(Pos(xx,yy,end+0.6)*Cylinder(1.2,1.2))
 screen_mount_screws.append(hardware)
 screen_mount_lengths.append(joint.screw_length_mm)
 screen_mount_connections['pod_to_shell_'+str(i+1)]='printed-screw-joint-v1 receiver and matched countersunk hardware with0.2mm head recess'
assert len(screen_mount_connections)==4
assert case_width/2-(screen_mount_front_axis_x+screen_mount_driver_shaft_diameter/2)>=1.5-1e-6
pi_carrier_ear_bottom=param('pi_carrier_ear_bottom',3.0)
pi_carrier_ear_thickness=param('pi_carrier_ear_thickness',2.4)
pi_carrier_ear_width=param('pi_carrier_ear_width',6.4)
pi_carrier_neck_length=param('pi_carrier_neck_length',8.6)
pi_carrier_mount_clearance=param('pi_carrier_mount_clearance',0.3)
pi_carrier_engagement=param('pi_carrier_engagement',3.6)
pi_carrier_left_mount_x=param('pi_carrier_left_mount_x',-29.0)
pi_carrier_left_front_y=param('pi_carrier_left_front_y',-22.0)
pi_carrier_left_rear_y=param('pi_carrier_left_rear_y',40.0)
pi_carrier_front_mount_x=param('pi_carrier_front_mount_x',24.0)
pi_carrier_front_mount_y=param('pi_carrier_front_mount_y',-50.0)
pi_carrier_axes=[(pi_carrier_left_mount_x,pi_carrier_left_front_y),(pi_carrier_left_mount_x,pi_carrier_left_rear_y),(pi_carrier_front_mount_x,pi_carrier_front_mount_y)]
pi_carrier_ear_top=pi_carrier_ear_bottom+pi_carrier_ear_thickness
pi_carrier_tabs=[]
pi_carrier_tab_seats=[]
pi_carrier_hardware=[]
for i,(xx,yy) in enumerate(pi_carrier_axes):
 left=i<2
 wx=pi_carrier_neck_length if left else pi_carrier_ear_width
 wy=pi_carrier_ear_width if left else pi_carrier_neck_length
 cx=xx+(pi_carrier_neck_length-pi_carrier_ear_width)/2 if left else xx
 cy=yy if left else yy+(pi_carrier_neck_length-pi_carrier_ear_width)/2
 tab=Pos(cx,cy,pi_carrier_ear_bottom+pi_carrier_ear_thickness/2)*Box(wx,wy,pi_carrier_ear_thickness)
 pi_carrier_tabs.append(tab)
 body-=Pos(cx,cy,pi_carrier_ear_top/2)*Box(wx+2*pi_carrier_mount_clearance,wy+2*pi_carrier_mount_clearance,pi_carrier_ear_top)
 root=(-case_width/2+shell_wall/2) if left else (-case_depth/2+shell_wall/2)
 inner=(xx+pi_carrier_ear_width/2) if left else (yy+pi_carrier_ear_width/2)
 ztip=case_top_center-(inner-root)
 assert ztip>pi_carrier_ear_top+pi_carrier_engagement+1.0
 pts=[(root,pi_carrier_ear_top),(inner,pi_carrier_ear_top),(inner,ztip),(root,case_top_center)]
 rib=(Pos(0,yy,0)*extrude(Plane.XZ*Polygon(*pts,align=None),amount=pi_carrier_ear_width/2,both=True)) if left else (Pos(xx,0,0)*extrude(Plane.YZ*Polygon(*pts,align=None),amount=pi_carrier_ear_width/2,both=True))
 body+=rib
 joint,seat,hardware=m2_flush_joint(Location((xx,yy,pi_carrier_ear_bottom),(180,0,0)),tab,pi_carrier_ear_thickness,pi_carrier_engagement,body,'Pi-independent-carrier-'+str(i+1),size='M2.5')
 assert len(joint.bosses.solids())==0
 body-=joint.engage_cuts
 pi_carrier_tab_seats.append(seat)
 pi_carrier_hardware.append(hardware)
 print('PI_CARRIER_SHELL_JOINT',i+1,dict(axis=(xx,yy),length=joint.screw_length_mm,engagement=joint.engage_depth_mm))
corner_support_start_y=param('corner_support_start_y',34.0)
corner_support_end_y=param('corner_support_end_y',53.0)
corner_support_inner_x=param('corner_support_inner_x',33.0)
corner_stop_height=shell_lower_z+shell_edge_radius-base_thickness+0.3
corner_wall=Pos(0,0,base_thickness)*extrude(RectangleRounded(case_width,case_depth,case_corner)-RectangleRounded(case_width-2*shell_wall,case_depth-2*shell_wall,case_corner-shell_wall),amount=corner_stop_height)
corner_stop=corner_wall & Pos((corner_support_inner_x+case_width/2)/2,(corner_support_start_y+corner_support_end_y)/2,base_thickness+corner_stop_height/2)*Box(case_width/2-corner_support_inner_x,corner_support_end_y-corner_support_start_y,corner_stop_height)
rx0,rx1,ry0,ry1,rz1=PI_REAR_CORNER_RELIEF
corner_stop-=Pos((rx0+rx1)/2,(ry0+ry1)/2,base_thickness+corner_stop_height/2)*Box(rx1-rx0,ry1-ry0,corner_stop_height+0.2)
body+=corner_stop
# Two side-facing flush kit joints release the frame along+X for service.
# Short through-receivers stay outside the heatsink; no blind-hole floor
# projects into the bought part. A2mm receiver retains1.2mm engagement after the kit lead-in.
side_panel_screw_y_front=param('side_panel_screw_y_front',-31.5)
side_panel_screw_y_rear=param('side_panel_screw_y_rear',32.5)
side_panel_screw_z=param('side_panel_screw_z',17.5)
side_panel_receiver_width=param('side_panel_receiver_width',6.4)
side_panel_receiver_top=param('side_panel_receiver_top',23.5)
side_panel_engagement=param('side_panel_light_engagement',1.2)
side_panel_front_engagement=param('side_panel_front_engagement',2.0)
side_panel_receiver_depth=side_panel_thickness
side_panel_cuts=[]
side_panel_hardware=[]
side_panel_screw_lengths=[]
side_panel_connections={}
for j,yy in enumerate([side_panel_screw_y_front,side_panel_screw_y_rear]):
 receiver_bottom=side_panel_screw_z-side_panel_receiver_width/2
 pad=Pos(side_panel_back_x-side_panel_receiver_depth/2,yy,(receiver_bottom+side_panel_receiver_top)/2)*Box(side_panel_receiver_depth,side_panel_receiver_width,side_panel_receiver_top-receiver_bottom)
 # Clear the cup return near the rear pad without cutting its closed web.
 pad=pad-side_panel_blank
 body=body+pad
 frame=Location((outer_port_x,yy,side_panel_screw_z),(0,90,0))
 joint=make_screw_joint_v1(size='M2.5',at=frame,through=[(side_panel_blank,side_panel_thickness)],seat='countersink',engage_depth=side_panel_front_engagement if j==0 else side_panel_engagement,into=body if j==0 else pad,head='countersunk',head_recess=0.2 if j==0 else 0.0,termination='blind' if j==0 else 'through',boss='none',lengths=(4.0,),material='PLA',print_axis='horizontal',label='side-port-frame-'+str(j+1))
 assert len(joint.bosses.solids())==0
 body=body-joint.engage_cuts
 side_panel_cuts.append(joint.through_cuts[0])
 side_panel_hardware.append(joint.hardware)
 side_panel_screw_lengths.append(joint.screw_length_mm)
 side_panel_connections[str(j)]='printed-screw-joint-v1 M2.5x4 through-receiver,1.2mm engagement'
 print('SIDE_PANEL_JOINT',j,dict(length=joint.screw_length_mm,engagement=joint.engage_depth_mm,protrusion=joint.screw_protrusion_mm))
 assert joint.screw_length_mm==4.0 and joint.screw_protrusion_mm<=0.15
assert len(side_panel_connections)==2
# Keep the same profile across every outer boss and the matching closure.
body=body & lower_visual_envelope
body=body-upper_edge_waste
print('VISUAL_EDGE_PROFILE',dict(lower_inset=shell_lower_visual_inset,lower_height=shell_lower_visual_height,bottom_bevel=base_visual_bevel,front_top_bevel=shell_front_edge_bevel,min_nominal_lower_wall=shell_wall-shell_lower_visual_inset+shell_lower_inner_shift-shell_edge_radius))
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
 publish('pcb_mount_screw_'+str(i+1),screw,'Ordered PCB M2 mount screw',material='stainless_steel',role='fastener')
for i,screw in enumerate(base_mount_screws):publish('base_mount_screw_'+str(i+1),screw,'Bottom cover screw',material='stainless_steel',role='fastener')
for i,screw in enumerate(screen_mount_screws):
 publish('screen_mount_screw_'+str(i+1),screw,'Screen mount '+('M2.5' if i<2 else 'M3')+' x '+str(screen_mount_lengths[i]),material='stainless_steel',role='fastener')