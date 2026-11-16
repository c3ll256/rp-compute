# cell: lcd_retainer
# cell: lcd_retainer
# cell: lcd_retainer
# cell: lcd_retainer
# cell: lcd_retainer
p=part('fascia')
retainer_width=param('retainer_width',66.0)
retainer_depth=param('retainer_depth',44.0)
retainer_y=param('retainer_y',-1.77)
retainer_rail_width=param('retainer_rail_width',3.0)
retainer_tail_gap=param('retainer_tail_gap',16.0)
# Original2mm base and mounting ears; the pressure rail is raised below.
ring=Pos(0,retainer_y,p.ret_bottom)*extrude(Rectangle(retainer_width,retainer_depth)-Rectangle(retainer_width-2*retainer_rail_width,retainer_depth-2*retainer_rail_width),amount=p.retainer_thickness)
ring-=Pos(0,retainer_y-retainer_depth/2,p.retainer_seat_z)*Box(retainer_tail_gap,2*retainer_rail_width+2,4*p.retainer_thickness)
for xx,yy in p.joint_axes:
 edge_y=retainer_y+(-retainer_depth/2 if yy<0 else retainer_depth/2)
 if yy<0:
  rear_y=edge_y+retainer_rail_width
  tab=Pos(xx,(p.retainer_front_tip_y+rear_y)/2,p.ret_bottom+p.retainer_thickness/2)*Box(p.retainer_ear_width,rear_y-p.retainer_front_tip_y,p.retainer_thickness)
 else:
  tab=Pos(xx,(edge_y+yy)/2,p.ret_bottom+p.retainer_thickness/2)*Box(p.retainer_ear_width,abs(edge_y-yy)+p.retainer_ear_depth,p.retainer_thickness)
 ring=ring+tab
# All assembly reliefs are through-slots in a flat plate. Sweeping the
# interference patch faces along Z gives its exact XY shadow without leaving
# the thin skins created by subtracting a tilted keepout directly.
retainer_shell_clearance=param('retainer_shell_clearance',0.3)
mount_reliefs=[]
for i,(xx,yy) in enumerate(p.housing.screen_mount_axes):
 ww=p.housing.screen_mount_front_pad_width if i<2 else p.housing.screen_mount_rear_pad_width
 dd=p.housing.screen_mount_front_pad_width if i<2 else p.housing.screen_mount_rear_pad_depth
 service_forward=2.5 if i<2 else (6.0 if i==2 else 0.0)
 cut=Pos(xx,yy-service_forward/2,p.housing.case_top_center)*Box(ww+2*retainer_shell_clearance,dd+2*retainer_shell_clearance+service_forward,2*p.housing.case_top_center)
 mount_reliefs.append(cut.moved(p.SCREEN_WORLD.inverse()))
# Flat base bridge runs ahead of the left rear pod mount so the captive
# front tongues can slide out without cutting the retainer into two pieces.
retainer_service_bridge_width=param('retainer_service_bridge_width',3.3)
bridge_front=retainer_y+retainer_depth/2-retainer_rail_width-retainer_service_bridge_width
bridge_rear=retainer_y+retainer_depth/2-retainer_rail_width+0.3
bridge_left=-retainer_width/2
bridge_right=-p.retainer_screw_x+p.retainer_ear_width/2
bridge=Pos((bridge_left+bridge_right)/2,(bridge_front+bridge_rear)/2,p.ret_bottom+p.retainer_thickness/2)*Box(bridge_right-bridge_left,bridge_rear-bridge_front,p.retainer_thickness)
ring=ring+bridge
plate_blank=ring
assembly_keepouts=[p.route_arc,p.route_start,p.route_return]+[v.moved(p.SCREEN_WORLD.inverse()) for v in p.voids]+[p.host]+mount_reliefs
through_clearances=[]
for keepout in assembly_keepouts:
 overlap=plate_blank & keepout
 if not overlap or not overlap.solids():continue
 patch=Compound(children=list(overlap.solids()))
 for face in patch.faces():
  if abs(face.normal_at().Z)<1e-7:continue
  prism=extrude(face,amount=2*p.retainer_thickness,dir=(0,0,1),both=True)
  if prism.volume>1e-8:through_clearances.append(prism)
ring=plate_blank-through_clearances
# Before the designed countersinks, every remaining side surface is vertical
# and the complete plate is exactly the driving thickness.
for face in ring.faces():
 nz=abs(face.normal_at().Z)
 assert nz<1e-6 or abs(nz-1)<1e-6,('partial-depth plate relief',nz)
top_area=sum(face.area for face in ring.faces() if abs(face.normal_at().Z)>1-1e-6 and abs(face.center().Z-p.retainer_seat_z)<1e-5)
assert abs(ring.volume-top_area*p.retainer_thickness)<1e-4,('nonconstant plate thickness',ring.volume,top_area)
print('RETAINER_FULL_THICKNESS',dict(thickness_mm=p.retainer_thickness,clearance_prisms=len(through_clearances),plate_volume_mm3=ring.volume))
# Raise only the glass-facing perimeter. Relieve this land independently so
# its overlap with an original screw stop cannot sever the base-to-ear bridge.
if p.retainer_pressure_rise>0:
 pressure_land=Pos(0,retainer_y,p.retainer_seat_z)*extrude(Rectangle(retainer_width,retainer_depth)-Rectangle(retainer_width-2*retainer_rail_width,retainer_depth-2*retainer_rail_width),amount=p.retainer_pressure_rise)
 pressure_land-=Pos(0,retainer_y-retainer_depth/2,p.retainer_contact_z)*Box(retainer_tail_gap,2*retainer_rail_width+2,4*(p.retainer_thickness+p.retainer_pressure_rise))
 # Clearance ahead of the rear receivers permits the12deg unhooking rotation.
 rear_tilt_reliefs=[Pos(xx,yy,(p.retainer_seat_z+1)/2)*Box(p.retainer_ear_width+0.6,p.retainer_ear_depth+0.6,1-p.retainer_seat_z) for xx,yy in p.joint_axes if yy>0]
 pressure_land=pressure_land-assembly_keepouts-through_clearances-rear_tilt_reliefs
 ring=ring.fuse(*list(pressure_land.solids()))
print('SCREEN_PRESSURE_RAIL',dict(base_mm=p.retainer_thickness,rise_mm=p.retainer_pressure_rise,closed_gap=p.screen_clamp_gap))
# Matched original screw seats, stops and hardware are retained.
for seat in p.retainer_cuts: ring=ring-seat

assert len(ring.solids())==1 and ring.is_valid,('flat retainer',len(ring.solids()))
assert abs(ring.bounding_box().size.Z-(p.retainer_thickness+p.retainer_pressure_rise))<0.001
ring.color=srgb('#363b40')
publish('retainer',ring,'Raised screen retainer',material='pla',role='part')
for i,(sc,axis) in enumerate(zip(p.retainer_hardware,p.retainer_screw_axes)):
 if axis[1]<0:continue
 screw_index=1 if axis[0]<0 else 2
 publish('retainer_screw_'+str(screw_index),sc,'M2.5 x '+str(p.joint_lengths[i])+' screw',material='stainless_steel',role='fastener')
print('TWO_PIECE_SCREEN',dict(printed_parts=['fascia','retainer'],retainer_thickness=p.retainer_thickness,screw_lengths=p.joint_lengths))