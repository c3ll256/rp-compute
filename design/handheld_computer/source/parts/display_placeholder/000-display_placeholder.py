# User-requested visual placeholder, not a manufacturer STEP or qualified display.
# Sharp LCY-1210401A LS027B7DH01 PDF p26: nominal body excludes tail/protrusions.
display_placeholder_width=param('display_placeholder_width',62.8)
display_placeholder_height=param('display_placeholder_height',42.82)
display_placeholder_thickness=param('display_placeholder_thickness',1.64)
display_placeholder_center_y=param('display_placeholder_center_y',-1.77)
display_placeholder_front_z=param('display_placeholder_front_z',-1.4)
display_placeholder=Pos(0,display_placeholder_center_y,display_placeholder_front_z-display_placeholder_thickness/2)*Box(display_placeholder_width,display_placeholder_height,display_placeholder_thickness)
display_placeholder.color=srgb('#aab4ad')
assert len(display_placeholder.solids())==1 and display_placeholder.is_valid
print('DISPLAY_PLACEHOLDER_LOCAL',dict(width=display_placeholder_width,height=display_placeholder_height,thickness=display_placeholder_thickness,front_z=display_placeholder_front_z,rear_z=display_placeholder_front_z-display_placeholder_thickness))
publish('display_placeholder',display_placeholder,'LCD placeholder',material='glass',role='reference')