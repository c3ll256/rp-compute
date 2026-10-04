button_diameter=param('button_diameter',9.0)
power_cap_thickness=param('power_cap_thickness',3.0)
power_cap_recess=param('power_cap_recess',2.0)
power_cap_edge=param('power_cap_edge',0.7)
power_cap_neck_diameter=param('power_cap_neck_diameter',9.0)
power_cap_lip_thickness=param('power_cap_lip_thickness',0.65)
# Preserve the existing user's10mm exterior diameter; narrow only the moving neck.
# Neck fits existing9.5mm shell bore; lip starts flush at shell exterior x42.5.
neck_h=power_cap_thickness-power_cap_lip_thickness
neck=Pos(0,0,-power_cap_recess)*Cylinder(power_cap_neck_diameter/2,neck_h,align=(Align.CENTER,Align.CENTER,Align.MIN))
lip=Cylinder(button_diameter/2,power_cap_lip_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
lip=fillet(lip.edges().filter_by(GeomType.CIRCLE),min(power_cap_edge,power_cap_lip_thickness/3))
cap=neck+Pos(0,0,neck_h-power_cap_recess)*lip
assert len(cap.solids())==1
cap.color=Color(0.96,0.31,0.07)
publish('power_cap',cap,'Orange power cap with clearance neck')