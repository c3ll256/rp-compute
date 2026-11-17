layout=part('side_port_bezel')
mask_print_layer=param('mask_print_layer',0.2)
assert 0.1<=mask_print_layer<=0.2
mask=layout.mask
publish('side_port_mask',mask,'Port panel inner mask',material='pla',role='part')