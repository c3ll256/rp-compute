s=part('shell')
speaker=part('speaker_reference')
wall=param('speaker_cup_wall',1.3)
lip=param('speaker_bond_width',0.9)
volume_cc=param('speaker_cavity_cc',1.0)
lead_d=param('speaker_lead_hole',1.6)
iw=s.speaker_face_w-2*lip
ih=s.speaker_face_h-2*lip
depth=1000*volume_cc/(iw*ih)
front=s.inner_front+speaker.gasket+speaker.depth
outer=Pos(s.speaker_x,front+(depth+wall)/2,s.audio_z)*Box(iw+2*wall,depth+wall,ih+2*wall)
void=Pos(s.speaker_x,front+depth/2-0.1,s.audio_z)*Box(iw,depth+0.2,ih)
cup=outer-void
cup-=Pos(s.speaker_x,front+depth+wall/2,s.audio_z)*Cylinder(lead_d/2,wall+1,rotation=(90,0,0))
cup.color=Color(0.32,0.32,0.30)
publish('speaker_chamber',cup,'Speaker rear chamber, seal lead entry after wiring',material='pla',role='part')