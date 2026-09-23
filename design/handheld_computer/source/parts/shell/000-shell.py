case_width=param('case_width',85.0)
case_depth=param('case_depth',115.0)
case_corner=param('case_corner',9.0)
case_top_center=param('case_top_center',27.0)
shell_wall=param('shell_wall',2.4)
shell_lower_z=param('shell_lower_z',2.7)
shell_edge_radius=param('shell_edge_radius',1.0)
button_y=param('button_y',-37.0)
button_diameter=param('button_diameter',9.0)
shell_button_z=param('shell_button_z',12.0)
panel_gap=param('panel_gap',0.25)
charge_width=param('charge_width',10.5)
charge_height=param('charge_height',4.4)
charge_z=param('charge_z',12.0)
shell_charge_y=param('shell_charge_y',-37.0)
front_module_width=param('front_module_width',70.0)
front_module_depth=param('front_module_depth',37.0)
front_module_y=param('front_module_y',-34.0)
front_module_seat_clearance=param('front_module_seat_clearance',0.3)
front_module_seat_depth=param('front_module_seat_depth',1.4)
front_module_aperture_width=param('front_module_aperture_width',54.0)
front_module_aperture_depth=param('front_module_aperture_depth',26.0)
front_module_tongue_depth=param('front_module_tongue_depth',0.6)
front_module_screw_x=param('front_module_screw_x',31.0)
front_module_screw_y_offset=param('front_module_screw_y_offset',15.0)
front_module_screw_engagement=param('front_module_screw_engagement',2.0)
shell_passage_width=param('shell_passage_width',42.0)
shell_passage_depth=param('shell_passage_depth',24.0)
shell_passage_y=param('shell_passage_y',18.0)
# Independent opening decisions; centers follow the placed step.parts Pi4B reference.
shell_rj45_x=param('shell_rj45_x',-6.75)
shell_rj45_z=param('shell_rj45_z',14.0)
shell_rj45_width=param('shell_rj45_width',17.0)
shell_rj45_height=param('shell_rj45_height',15.0)
shell_usb_mid_x=param('shell_usb_mid_x',12.0)
shell_usb_mid_z=param('shell_usb_mid_z',15.0)
shell_usb_mid_width=param('shell_usb_mid_width',15.0)
shell_usb_mid_height=param('shell_usb_mid_height',17.0)
shell_usb_right_x=param('shell_usb_right_x',30.0)
shell_usb_right_z=param('shell_usb_right_z',15.0)
shell_usb_right_width=param('shell_usb_right_width',16.0)
shell_usb_right_height=param('shell_usb_right_height',18.0)
shell_hdmi1_y=param('shell_hdmi1_y',-4.5)
shell_hdmi2_y=param('shell_hdmi2_y',9.0)
shell_hdmi_z=param('shell_hdmi_z',8.6)
shell_hdmi_width=param('shell_hdmi_width',8.5)
shell_hdmi_height=param('shell_hdmi_height',5.2)
shell_jack_y=param('shell_jack_y',23.5)
shell_jack_z=param('shell_jack_z',10.0)
shell_jack_diameter=param('shell_jack_diameter',8.5)
shell_port_radius=param('shell_port_radius',0.5)
shell_pi_usb_c_y=param('shell_pi_usb_c_y',-19.3)
shell_pi_usb_c_z=param('shell_pi_usb_c_z',9.0)
shell_pi_usb_c_width=param('shell_pi_usb_c_width',12.0)
shell_pi_usb_c_height=param('shell_pi_usb_c_height',8.0)
shell_pi_usb_c_outer_wall=param('shell_pi_usb_c_outer_wall',1.5)
outer=Pos(0,0,shell_lower_z)*extrude(RectangleRounded(case_width,case_depth,case_corner),amount=case_top_center-shell_lower_z)
outer=fillet(outer.edges().filter_by(Plane.XY),shell_edge_radius)
inner=extrude(RectangleRounded(case_width-2*shell_wall,case_depth-2*shell_wall,case_corner-shell_wall),amount=case_top_center-shell_wall)
body=outer-inner
body-=Pos(0,shell_passage_y,case_top_center-shell_wall)*extrude(RectangleRounded(shell_passage_width,shell_passage_depth,2),amount=2*shell_wall)
# Reusable front-deck cassette: shallow locating seat over a true service aperture.
body-=Pos(0,front_module_y,case_top_center-front_module_seat_depth)*extrude(RectangleRounded(front_module_width+front_module_seat_clearance,front_module_depth+front_module_seat_clearance,2.0),amount=front_module_seat_depth+0.5)
body-=Pos(0,front_module_y,case_top_center-shell_wall-0.5)*extrude(RectangleRounded(front_module_aperture_width,front_module_aperture_depth,1.5),amount=shell_wall+1.0)
body-=Pos(case_width/2,button_y,shell_button_z)*Rot(0,90,0)*Cylinder(button_diameter/2+panel_gap,4*shell_wall)
# Charge input on LEFT SIDE, front is now continuous material.
body-=Pos(-case_width/2,shell_charge_y,charge_z)*extrude(Plane.YZ*RectangleRounded(charge_width,charge_height,charge_height/2-0.01),amount=4*shell_wall,both=True)
for x,z,w,h in [(shell_rj45_x,shell_rj45_z,shell_rj45_width,shell_rj45_height),(shell_usb_mid_x,shell_usb_mid_z,shell_usb_mid_width,shell_usb_mid_height),(shell_usb_right_x,shell_usb_right_z,shell_usb_right_width,shell_usb_right_height)]:
 body-=Pos(x,case_depth/2,z)*extrude(Plane.XZ*RectangleRounded(w,h,shell_port_radius),amount=4*shell_wall,both=True)
for y in [shell_hdmi1_y,shell_hdmi2_y]:
 body-=Pos(case_width/2,y,shell_hdmi_z)*extrude(Plane.YZ*RectangleRounded(shell_hdmi_width,shell_hdmi_height,shell_port_radius),amount=4*shell_wall,both=True)
body-=Pos(case_width/2,shell_jack_y,shell_jack_z)*Rot(0,90,0)*Cylinder(shell_jack_diameter/2,8*shell_wall)
# Internal blind clearance leaves an unbroken outer wall over Pi's own USB-C.
# This blocks access geometrically; it is NOT the future working electrical interlock.
blind=Pos(case_width/2-shell_pi_usb_c_outer_wall,shell_pi_usb_c_y,shell_pi_usb_c_z)*extrude(Plane.YZ*RectangleRounded(shell_pi_usb_c_width,shell_pi_usb_c_height,shell_port_radius),amount=-4*shell_wall)
body-=blind
# Concealed wells under the screen pod clear the rear-frame mounting ears.
# Outer shell, front groove and all external port openings remain untouched.
shell_lcd_mount_x=param('shell_lcd_mount_x',20.0)
shell_lcd_mount_y_front=param('shell_lcd_mount_y_front',-28.0)
shell_lcd_mount_y_rear=param('shell_lcd_mount_y_rear',25.5)
shell_lcd_well_width=param('shell_lcd_well_width',6.4)
shell_lcd_well_depth=param('shell_lcd_well_depth',7.0)
SCREEN_FRAME=Pos(0,21.521201483,35.310909266)*Rot(13,0,0)
for xx in [-shell_lcd_mount_x,shell_lcd_mount_x]:
 for yy in [shell_lcd_mount_y_front,shell_lcd_mount_y_rear]:
  body-=SCREEN_FRAME*Pos(xx,yy,-8)*Box(shell_lcd_well_width,shell_lcd_well_depth,20)
# Pi 4B STEP rear board corner needs an internal blind relief after the USB aperture is tightened.
# Fixed reference geometry from imported Pi asset; preserve 2.2 mm outer rear wall.
PI_REAR_CORNER_RELIEF_CENTER=(37.5,53.3,6.2)
PI_REAR_CORNER_RELIEF_SIZE=(4.0,4.0,2.8)
body-=Pos(*PI_REAR_CORNER_RELIEF_CENTER)*Box(*PI_REAR_CORNER_RELIEF_SIZE)
from screwjoint import make_screw_joint_v1
# A blank insert defines the shared mechanical envelope for later user-made modules.
front_module=Pos(0,front_module_y,case_top_center-front_module_seat_depth/2)*extrude(RectangleRounded(front_module_width,front_module_depth,1.8),amount=front_module_seat_depth/2,both=True)
front_module+=Pos(0,front_module_y,case_top_center-front_module_seat_depth-front_module_tongue_depth)*extrude(RectangleRounded(front_module_aperture_width-2*front_module_seat_clearance,front_module_aperture_depth-2*front_module_seat_clearance,1.2),amount=front_module_tongue_depth)
front_module_screws=[]
for xx in [-front_module_screw_x,front_module_screw_x]:
 for yy in [front_module_y-front_module_screw_y_offset,front_module_y+front_module_screw_y_offset]:
  joint=make_screw_joint_v1(size='M2',at=Location((xx,yy,case_top_center)),through=[(front_module,front_module_seat_depth)],engage_depth=front_module_screw_engagement,into=body,head='socket_cap',material='PLA',label='front-module')
  front_module=front_module-joint.through_cuts[0]
  if len(joint.bosses.solids())>0:
   body=body+joint.bosses
  body=body-joint.engage_cuts
  front_module_screws.append(joint.hardware)
assert len(front_module.solids())==1
assert len(body.solids())==1
body.color=Color(0.88,0.86,0.79)
front_module.color=Color(0.23,0.25,0.27)
publish('shell',body,'Rear and side port shell')
publish('front_module_blank',front_module,'User replaceable front module blank')
for i,screw in enumerate(front_module_screws):
 publish('front_module_screw_'+str(i+1),screw,'M2 front module screw')