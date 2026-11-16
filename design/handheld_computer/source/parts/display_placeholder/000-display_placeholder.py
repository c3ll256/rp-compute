# cell: display_placeholder
# User-requested visual placeholder, not a manufacturer STEP or qualified display.
# Outline from Sharp p26; thickness1.8mm is the user's measured sample.
p=part('fascia')
display_placeholder_width=param('display_placeholder_width',62.8)
display_placeholder_height=param('display_placeholder_height',42.82)
display_placeholder_thickness=p.screen_measured_thickness
display_placeholder_center_y=param('display_placeholder_center_y',-1.77)
display_placeholder_front_z=p.GLASS_FRONT
display_placeholder=Pos(0,display_placeholder_center_y,display_placeholder_front_z-display_placeholder_thickness/2)*Box(display_placeholder_width,display_placeholder_height,display_placeholder_thickness)
display_placeholder.color=srgb('#aab4ad')
assert len(display_placeholder.solids())==1 and display_placeholder.is_valid
print('DISPLAY_PLACEHOLDER_LOCAL',dict(width=display_placeholder_width,height=display_placeholder_height,thickness=display_placeholder_thickness,front_z=display_placeholder_front_z,rear_z=display_placeholder_front_z-display_placeholder_thickness))
publish('display_placeholder',display_placeholder,'LCD placeholder',material='glass',role='reference')
