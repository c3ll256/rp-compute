layout=part('shell')
side_panel_edge_bevel=param('side_panel_edge_bevel',0.3)
panel=layout.side_panel_blank
# Break only the visible outside perimeter; leave plug-pocket widths intact.
edges=[e for e in panel.edges() if all(abs(v.X-layout.outer_port_x)<1e-5 for v in e.vertices()) and (e.center().Y<layout.side_panel_center_y-layout.side_panel_width/2+0.8 or e.center().Y>layout.side_panel_center_y+layout.side_panel_width/2-0.8 or e.center().Z>layout.side_panel_bottom_z+layout.side_panel_height-0.8)]
assert edges,'port frame perimeter selection'
panel=chamfer(edges,side_panel_edge_bevel)
for seat in layout.side_panel_cuts:panel=panel-seat
assert panel.is_valid and len(panel.solids())==1
panel.color=layout.body.color
publish('side_port_panel',panel,'Recessed port frame',material='pla',role='part')
for i,hardware in enumerate(layout.side_panel_hardware):
 publish('side_port_panel_screw_'+str(i+1),hardware,'Port frame screw',material='stainless_steel',role='fastener')
