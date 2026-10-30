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
# Only actual assembly keepouts; no rear flange seat or separate FPC guard.
for keepout in [p.route_arc,p.route_start,p.route_return]:
 ring=ring-keepout
for void in p.voids:
 ring=ring-void.moved(p.SCREEN_WORLD.inverse())
ring=ring-p.host
for seat in p.retainer_cuts:
 ring=ring-seat

# Open-edge reliefs clear the upper-shell lugs and their screw heads.
retainer_shell_clearance=param('retainer_shell_clearance',0.3)
mount_reliefs=[]
for i,(xx,yy) in enumerate(p.housing.screen_mount_axes):
 ww=p.housing.screen_mount_front_pad_width if i<2 else p.housing.screen_mount_rear_pad_width
 dd=p.housing.screen_mount_front_pad_width if i<2 else p.housing.screen_mount_rear_pad_depth
 cut=Pos(xx,yy,p.housing.case_top_center)*Box(ww+2*retainer_shell_clearance,dd+2*retainer_shell_clearance,2*p.housing.case_top_center)
 mount_reliefs.append(cut.moved(p.SCREEN_WORLD.inverse()))
ring=ring-Compound(children=mount_reliefs)

assert len(ring.solids())==1 and ring.is_valid,('flat retainer',len(ring.solids()))
assert abs(ring.bounding_box().size.Z-p.retainer_thickness)<0.001
p.compact_overlap_check('PCB / flat retainer',p.compact_pcb,ring.moved(p.SCREEN_WORLD))
ring.color=srgb('#363b40')
publish('retainer',ring,'Flat rear retainer',material='pla',role='part')
for i,sc in enumerate(p.retainer_hardware):
 publish('retainer_screw_'+str(i+1),sc,'M2 x '+str(p.joint_lengths[i])+' screw',material='stainless_steel',role='fastener')
print('TWO_PIECE_SCREEN',dict(printed_parts=['fascia','retainer'],retainer_thickness=p.retainer_thickness,screw_lengths=p.joint_lengths))