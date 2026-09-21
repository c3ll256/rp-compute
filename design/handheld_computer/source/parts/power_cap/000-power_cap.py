button_diameter=param('button_diameter',9.0)
power_cap_thickness=param('power_cap_thickness',3.0)
power_cap_recess=param('power_cap_recess',2.0)
power_cap_edge=param('power_cap_edge',0.7)
cap=Cylinder(button_diameter/2,power_cap_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
cap=fillet(cap.edges().filter_by(GeomType.CIRCLE),power_cap_edge)
cap=Pos(0,0,-power_cap_recess)*cap
cap.color=Color(0.96,0.31,0.07)
publish('power_cap',cap,'Orange power cap')