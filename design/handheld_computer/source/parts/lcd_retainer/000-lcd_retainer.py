# cell: lcd_retainer

p=part('fascia')
retainer_width=param('retainer_width',66.0)
retainer_depth=param('retainer_depth',44.0)
retainer_y=param('retainer_y',-1.77)
retainer_rail_width=param('retainer_rail_width',3.0)
retainer_tail_gap=param('retainer_tail_gap',16.0)
# One constant-thickness plate; both broad faces are parallel.
ring=Pos(0,retainer_y,p.ret_bottom)*extrude(Rectangle(retainer_width,retainer_depth)-Rectangle(retainer_width-2*retainer_rail_width,retainer_depth-2*retainer_rail_width),amount=p.retainer_thickness)
ring-=Pos(0,retainer_y-retainer_depth/2,p.retainer_seat_z)*Box(retainer_tail_gap,2*retainer_rail_width+2,4*p.retainer_thickness)
for xx,yy in p.joint_axes:
 edge_y=retainer_y+(-retainer_depth/2 if yy<0 else retainer_depth/2)
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
 cut=Pos(xx,yy,p.housing.case_top_center)*Box(ww+2*retainer_shell_clearance,dd+2*retainer_shell_clearance,2*p.housing.case_top_center)
 mount_reliefs.append(cut.moved(p.SCREEN_WORLD.inverse()))
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
# Countersinks are the only intentional local taper in the finished plate.
for seat in p.retainer_cuts: ring=ring-seat

assert len(ring.solids())==1 and ring.is_valid,('flat retainer',len(ring.solids()))
assert abs(ring.bounding_box().size.Z-p.retainer_thickness)<0.001
p.compact_overlap_check('PCB / flat retainer',p.compact_pcb,ring.moved(p.SCREEN_WORLD))
ring.color=srgb('#363b40')
publish('retainer',ring,'Flat rear retainer',material='pla',role='part')
for i,sc in enumerate(p.retainer_hardware):
 publish('retainer_screw_'+str(i+1),sc,'M2 x '+str(p.joint_lengths[i])+' screw',material='stainless_steel',role='fastener')
print('TWO_PIECE_SCREEN',dict(printed_parts=['fascia','retainer'],retainer_thickness=p.retainer_thickness,screw_lengths=p.joint_lengths))