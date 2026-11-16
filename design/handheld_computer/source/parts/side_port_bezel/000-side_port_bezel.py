# cell: side_port_bezel
layout=part('shell')
side_panel_edge_bevel=param('side_panel_edge_bevel',0.3)
# Use the same original mounting envelope and port tooling, but keep the
# external face flat for printing. Only the lower exterior facet is filled;
# no material is added behind the original mating plane or into the shell.
panel=layout.side_panel_blanks[0].fuse(*layout.side_panel_blanks[1:])
for pocket in layout.side_port_pockets:panel=panel-pocket
for bore in layout.side_port_bores:panel=panel-bore
# Break only the visible outside perimeter; leave plug-pocket widths intact.
edges=[e for e in panel.edges() if all(abs(v.X-layout.outer_port_x)<1e-5 for v in e.vertices()) and (e.center().Y<layout.side_panel_center_y-layout.side_panel_width/2+0.8 or e.center().Y>layout.side_panel_center_y+layout.side_panel_width/2-0.8 or e.center().Z>layout.side_panel_bottom_z+layout.side_panel_height-0.8 or e.center().Z<layout.side_panel_bottom_z+0.8)]
assert edges,'port frame perimeter selection'
panel=chamfer(edges,side_panel_edge_bevel)
for seat in layout.side_panel_cuts:panel=panel-seat
assert panel.is_valid and len(panel.solids())==1
panel.color=layout.body.color
publish('side_port_panel',panel,'Recessed port frame',material='pla',role='part')
for i,hardware in enumerate(layout.side_panel_hardware):
 publish('side_port_panel_screw_'+str(i+1),hardware,'Port frame screw',material='stainless_steel',role='fastener')