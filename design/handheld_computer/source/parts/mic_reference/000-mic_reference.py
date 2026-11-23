s=part('shell')
outer=param('duct_outer_d',4.5)
bore=param('duct_bore_d',1.6)
front_t=param('front_sealing_flange_t',1.1)
flange_clearance=param('flange_side_clearance',0.2)
board_y=param('mic_axis_world_y',-37.0)
board_z=param('pcb_underside_z',21.0)
x=s.mic_x
bx=x+param('outlet_offset_x',-1.5)
y0=s.inner_front
z0=s.audio_z
def channel(d):
    r=d/2
    straight=loft([Pos(x,y0,z0)*(Plane.XZ*Circle(r)),Pos(bx,board_y,z0)*(Plane.XZ*Circle(r))])
    up=Pos(bx,board_y,(z0+board_z)/2)*Cylinder(r,board_z-z0)
    return straight + Pos(bx,board_y,z0)*Sphere(r) + up
flange=Pos(x,y0+front_t/2,z0)*Box(s.mic_carrier_w-2*flange_clearance,front_t,s.mic_carrier_h-2*flange_clearance)
boot=(channel(outer)+flange)-channel(bore)
boot.color=Color(0.25,0.26,0.25)
publish('mic_reference',boot,'Sealed microphone elbow, front wall to PCB underside')
fit('mic_reference','pi_baseboard_lite',kind='nominal_contact',budget_mm=0.15,reason='The soft lip of the acoustic seal compresses against underside copper around the board sound hole.')