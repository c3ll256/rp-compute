layout=part('shell')
side_panel_edge_bevel=param('side_panel_edge_bevel',0.3)
side_panel_glue_gap=param('side_panel_glue_gap',0.05)
assert 0<=side_panel_glue_gap<=0.15
# Source-owned assembled envelope retains original mounting and kit openings.
envelope=layout.side_panel_blanks[0].fuse(*layout.side_panel_blanks[1:])
for pocket in layout.side_port_pockets:envelope=envelope-pocket
for bore in layout.side_port_bores:envelope=envelope-bore
edges=[e for e in envelope.edges() if all(abs(v.X-layout.outer_port_x)<1e-5 for v in e.vertices()) and (e.center().Y<layout.side_panel_center_y-layout.side_panel_width/2+0.8 or e.center().Y>layout.side_panel_center_y+layout.side_panel_width/2-0.8 or e.center().Z>layout.side_panel_bottom_z+layout.side_panel_height-0.8 or e.center().Z<layout.side_panel_bottom_z+0.8)]
envelope=chamfer(edges,side_panel_edge_bevel)
for seat in layout.side_panel_cuts:envelope=envelope-seat
clip_span=layout.case_depth*2
panel=envelope & (Pos(layout.side_panel_back_x,0,0)*Box(layout.side_panel_thickness,clip_span,clip_span,align=(Align.MIN,Align.CENTER,Align.CENTER)))
# The three low connector cups form one printable inner mask.
# Audio remains in the main plate with an0.8mm floor growing off its bed.
mask=layout.side_panel_blanks[1].fuse(*layout.side_panel_blanks[2:4])
for pocket in layout.side_port_pockets:mask=mask-pocket
for bore in layout.side_port_bores:mask=mask-bore
mask_back_x=min(q['back_x'] for q in layout.side_port_layout if q['label']!='3.5mm audio')
mask_front_x=layout.side_panel_back_x-side_panel_glue_gap
mask=mask & (Pos(mask_back_x,0,0)*Box(mask_front_x-mask_back_x,clip_span,clip_span,align=(Align.MIN,Align.CENTER,Align.CENTER)))
# attach_panel_v1(glue_pad) was tested on these mating faces and rejected:
# contact too narrow for a hidden feature. Explicit free flush adhesive joint.
# Preserve thin flange geometry rather than forcing oversized kit tabs.
connections={'mask_to_panel':'free: flush PLA adhesive joint after SplitJointNotApplicableV1, narrow contact'}
assert len(connections)==1
for name,shape in [('panel',panel),('mask',mask)]:
 assert shape.is_valid and len(shape.solids())==1,(name,'not one valid solid')
 for label,probe in layout.plug_reserves:
  hit=shape & probe
  assert not hit or hit.volume<1e-5,(name,label,'plug blocked')
panel.color=layout.body.color
mask.color=layout.body.color
publish('side_port_panel',panel,'Port panel outer',material='pla',role='part')
for i,hardware in enumerate(layout.side_panel_hardware):
 publish('side_port_panel_screw_'+str(i+1),hardware,'Port frame screw',material='stainless_steel',role='fastener')
