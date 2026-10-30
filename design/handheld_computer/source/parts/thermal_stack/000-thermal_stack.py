layout=part('shell')
# Geekworm P165-B explicit photo/dimension reference, NOT manufacturer STEP.
# Verified outer size55x65x11mm and four M2.5 threads (Geekworm SKU100237).
# Fin spacing, underside lands and port reliefs below are photo-derived defaults;
# they carry no stock-machining or guaranteed physical contact certification.
P165_W=55.0
P165_D=65.0
P165_H=11.0
P165_HOLE_X=tuple(x+layout.pi_offset_x for x in (-13.5,35.5))
P165_HOLE_Y=(-27.,31.)
passive_heatsink_allowance=param('passive_heatsink_allowance',0.0)
passive_heatsink_x=param('passive_heatsink_x',11.0)+layout.pi_offset_x
passive_heatsink_y=param('passive_heatsink_y',2.0)
passive_heatsink_bottom_z=param('passive_heatsink_bottom_z',7.1)
passive_heatsink_base_bottom_z=param('passive_heatsink_base_bottom_z',11.5)
passive_heatsink_base_thickness=param('passive_heatsink_base_thickness',1.2)
passive_heatsink_fin_thickness=param('passive_heatsink_fin_thickness',1.1)
passive_heatsink_fin_count=param('passive_heatsink_fin_count',21)
passive_heatsink_corner_width=param('passive_heatsink_corner_width',6.0)
passive_heatsink_gpio_relief_width=param('passive_heatsink_gpio_relief_width',7.2)
passive_heatsink_gpio_relief_depth=param('passive_heatsink_gpio_relief_depth',51.0)
passive_heatsink_dsi_relief_width=param('passive_heatsink_dsi_relief_width',23.4)
passive_heatsink_dsi_relief_depth=param('passive_heatsink_dsi_relief_depth',7.2)
passive_heatsink_av_relief_width=param('passive_heatsink_av_relief_width',12.5)
passive_heatsink_av_relief_depth=param('passive_heatsink_av_relief_depth',13.0)
passive_heatsink_av_relief_top_z=param('passive_heatsink_av_relief_top_z',14.5)
passive_heatsink_dsi_relief_x=param('passive_heatsink_dsi_relief_x',11.0)+layout.pi_offset_x
passive_heatsink_av_relief_y=param('passive_heatsink_av_relief_y',23.5)
passive_heatsink_csi_relief_width=param('passive_heatsink_csi_relief_width',23.0)
passive_heatsink_csi_relief_depth=param('passive_heatsink_csi_relief_depth',6.4)
passive_heatsink_csi_relief_y=param('passive_heatsink_csi_relief_y',16.1)
passive_heatsink_poe_relief_width=param('passive_heatsink_poe_relief_width',6.2)
passive_heatsink_poe_relief_depth=param('passive_heatsink_poe_relief_depth',6.1)
passive_heatsink_poe_relief_x=param('passive_heatsink_poe_relief_x',-7.36)+layout.pi_offset_x
passive_heatsink_poe_relief_y=param('passive_heatsink_poe_relief_y',31.0)
# Existing contact datums retained;0.25mm TIM is a review assumption only.
cpu_heatsink_x=param('cpu_heatsink_x',6.3725)+layout.pi_offset_x
cpu_heatsink_y=param('cpu_heatsink_y',-1.2681)
cpu_heatsink_bottom_z=param('cpu_heatsink_bottom_z',9.55)
ram_heatsink_x=param('ram_heatsink_x',6.58255)+layout.pi_offset_x
ram_heatsink_y=param('ram_heatsink_y',14.3315)
ram_heatsink_bottom_z=param('ram_heatsink_bottom_z',8.05)
cpu_thermal_tape_width=param('cpu_thermal_tape_width',13.5)
cpu_thermal_tape_depth=param('cpu_thermal_tape_depth',13.5)
cpu_thermal_tape_thickness=param('cpu_thermal_tape_thickness',0.25)
ram_thermal_tape_width=param('ram_thermal_tape_width',9.5)
ram_thermal_tape_depth=param('ram_thermal_tape_depth',9.5)
ram_thermal_tape_thickness=param('ram_thermal_tape_thickness',0.25)
w=P165_W+2*passive_heatsink_allowance
d=P165_D+2*passive_heatsink_allowance
x,y,z=passive_heatsink_x,passive_heatsink_y,passive_heatsink_bottom_z
base_z=passive_heatsink_base_bottom_z
base_t=passive_heatsink_base_thickness
top=z+P165_H
sink=Pos(x,y,base_z+base_t/2)*Box(w,d,base_t)
for i in range(int(passive_heatsink_fin_count)):
 xx=x-w/2+passive_heatsink_fin_thickness/2+i*(w-passive_heatsink_fin_thickness)/(int(passive_heatsink_fin_count)-1)
 sink+=Pos(xx,y,(base_z+base_t+top-1)/2)*Box(passive_heatsink_fin_thickness,d,top-1-base_z-base_t)
for xx in P165_HOLE_X:
 for yy in P165_HOLE_Y:
  sink+=Pos(xx,yy,(z+top)/2)*Box(passive_heatsink_corner_width,passive_heatsink_corner_width,P165_H)
# Visible manufacturer GPIO and front display-connector reliefs.
sink-=Pos(x-w/2+passive_heatsink_gpio_relief_width/2,y,top/2)*Box(passive_heatsink_gpio_relief_width,passive_heatsink_gpio_relief_depth,2*top)
sink-=Pos(passive_heatsink_dsi_relief_x,y-d/2+passive_heatsink_dsi_relief_depth/2,top/2)*Box(passive_heatsink_dsi_relief_width,passive_heatsink_dsi_relief_depth,2*top)
# Photo side view shows underside port clearance above the Pi AV jack.
sink-=Pos(x+w/2-passive_heatsink_av_relief_width/2,passive_heatsink_av_relief_y,(z+passive_heatsink_av_relief_top_z)/2)*Box(passive_heatsink_av_relief_width,passive_heatsink_av_relief_depth,passive_heatsink_av_relief_top_z-z)
# Visible CSI slot and small rear PoE relief in Geekworm packing top photo.
# Widths/depths inferred to clear nominal Pi reference by >=0.3mm. These are
# unknown stock detail dimensions, NOT instructions to machine the bought part.
sink-=Pos(x+w/2-passive_heatsink_csi_relief_width/2,passive_heatsink_csi_relief_y,top/2)*Box(passive_heatsink_csi_relief_width,passive_heatsink_csi_relief_depth,2*top)
sink-=Pos(passive_heatsink_poe_relief_x,passive_heatsink_poe_relief_y,top/2)*Box(passive_heatsink_poe_relief_width,passive_heatsink_poe_relief_depth,2*top)
# Nominal interface lands sized inside actual CPU/RAM package boundaries.
for xx,yy,zz,ww,dd in [(cpu_heatsink_x,cpu_heatsink_y,cpu_heatsink_bottom_z,cpu_thermal_tape_width,cpu_thermal_tape_depth),(ram_heatsink_x,ram_heatsink_y,ram_heatsink_bottom_z,ram_thermal_tape_width,ram_thermal_tape_depth)]:
 sink+=Pos(xx,yy,(zz+base_z)/2)*Box(ww,dd,base_z-zz)
# Nominal female major-diameter clearance envelope. The real metal female threads engage the screw.
P165_THREAD_MAJOR_D=2.5 # M2.5 female major-diameter clearance envelope; no modeled thread helix.
for xx in P165_HOLE_X:
 for yy in P165_HOLE_Y:sink-=Pos(xx,yy,(z+top)/2)*Cylinder(P165_THREAD_MAJOR_D/2,2*P165_H)
assert len(sink.solids())==1
sink.color=Color(0.12,0.13,0.14)
publish('passive_heatsink',sink,'P165-B photo-derived reference',material='aluminum',role='reference')
cpu_tape=Pos(cpu_heatsink_x,cpu_heatsink_y,cpu_heatsink_bottom_z-cpu_thermal_tape_thickness/2)*Box(cpu_thermal_tape_width,cpu_thermal_tape_depth,cpu_thermal_tape_thickness)
ram_tape=Pos(ram_heatsink_x,ram_heatsink_y,ram_heatsink_bottom_z-ram_thermal_tape_thickness/2)*Box(ram_thermal_tape_width,ram_thermal_tape_depth,ram_thermal_tape_thickness)
for oid,s in [('cpu_thermal_tape',cpu_tape),('ram_thermal_tape',ram_tape)]:
 s.color=Color(0.8,0.8,0.8);publish(oid,s,'Included kit TIM nominal gap reference',material='rubber',role='reference')