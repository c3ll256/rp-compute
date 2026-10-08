
# Standalone replaceable cover, modelled with its upper face at local Z=0.
# World assembly placement is (0,-34,27), set with cad.edit place.
front_module_width=param('front_module_width',70.0)
front_module_depth=param('front_module_depth',37.0)
front_module_seat_clearance=param('front_module_seat_clearance',0.3)
front_module_seat_depth=param('front_module_seat_depth',1.4)
front_module_tongue_depth=param('front_module_tongue_depth',0.6)
front_module_aperture_width=param('front_module_aperture_width',54.0)
front_module_aperture_depth=param('front_module_aperture_depth',26.0)
front_module_screw_x=param('front_module_screw_x',31.0)
front_module_screw_y_offset=param('front_module_screw_y_offset',15.0)
front_module_blank_thickness=param('front_module_blank_thickness',1.4)
front_module_blank_corner=param('front_module_blank_corner',1.8)
front_module_blank_tongue_corner=param('front_module_blank_tongue_corner',1.2)
front_module_blank_socket_cover_x=param('front_module_blank_socket_cover_x',0.0)
front_module_blank_socket_cover_y=param('front_module_blank_socket_cover_y',-34.0)
front_module_blank_socket_air=param('front_module_blank_socket_air',0.1)
front_module_blank_socket_roof=param('front_module_blank_socket_roof',0.6)
front_module_gpio_pin_pocket_roof=param('front_module_gpio_pin_pocket_roof',1.2)
shell_pcb_top_air=param('shell_pcb_top_air',1.6)
front_module_pcb_min_roof=param('front_module_pcb_min_roof',1.2)
# Frozen released assembly envelopes below are reference geometry, not design sliders.
REFERENCE_PLACEMENT=(0,-34,27) # Existing dock / fixed deck datum.
HLE_BOUNDS=(-5.075,-36.54,22.594999,5.075,-31.46,26.254999)
PCB_BEAM_CLEARANCE_BOUNDS=[
 (-41.8,-35.5,21.8,-12.5,-28.5,25.1),
 (12.5,-35.5,21.8,41.8,-28.5,25.1),
] # Existing upper-shell support envelope plus its established 0.5mm clearance.
GPIO_PIN_POCKET_X=-13.5 # Released dock pin ends, world-frame bounds.
GPIO_PIN_POCKET_Y=-19.4
GPIO_PIN_POCKET_WIDTH=6.2
GPIO_PIN_POCKET_DEPTH=10.0
PCB_BOTTOM_Z=21.8
PCB_FRONT_BODY_BOUNDS=[
    (-8.650013,-51.000000,22.594999, -7.350013,-49.000000,23.894999), # 0:assembly_1_1
    (-8.850013,-23.800000,22.594999, -7.550013,-21.800000,23.894999), # 4:assembly_1_1
    (-17.150013,-51.000000,22.594999, -15.850013,-49.000000,23.894999), # 8:assembly_1_1
    (4.600000,-10.750000,22.594999, 5.400000,-9.150000,23.394999), # 9:assembly_1_10
    (4.800000,-50.649987,22.594999, 6.800000,-49.349987,23.894999), # 10:assembly_1_1
    (14.400000,-50.649987,22.594999, 16.400000,-49.349987,23.894999), # 11:assembly_1_1
    (-14.006302,-51.449987,22.594999, -10.993698,-48.549987,23.845082), # 13:assembly_1_14
    (-8.450000,-19.400000,22.594999, -5.550000,-16.600000,24.144999), # 15:SOT-23-6
    (10.550000,-20.400000,22.594999, 13.450000,-17.600000,24.144999), # 17:SOT-23-6
    (6.349987,-17.500000,22.594999, 7.649987,-15.500000,23.894999), # 21:assembly_1_1
    (9.193698,-51.450013,22.594999, 12.206302,-48.550013,23.845082), # 24:assembly_1_14
    (7.493685,-10.500000,22.594999, 13.506290,-5.500000,23.695082), # 26:assembly_1_6 moved U_BUF1
]

def local_clearance(b,air=0.0):
 x0,y0,z0,x1,y1,z1=b
 return Pos((x0+x1)/2-REFERENCE_PLACEMENT[0],(y0+y1)/2-REFERENCE_PLACEMENT[1],(z0+z1)/2-REFERENCE_PLACEMENT[2])*Box(x1-x0+2*air,y1-y0+2*air,z1-z0+2*air)

cover=Pos(0,0,-front_module_blank_thickness)*extrude(RectangleRounded(front_module_width,front_module_depth,front_module_blank_corner),amount=front_module_blank_thickness)
cover+=Pos(0,0,-front_module_seat_depth-front_module_tongue_depth)*extrude(RectangleRounded(front_module_aperture_width-2*front_module_seat_clearance,front_module_aperture_depth-2*front_module_seat_clearance,front_module_blank_tongue_corner),amount=front_module_tongue_depth)
for b in PCB_FRONT_BODY_BOUNDS:
 assert REFERENCE_PLACEMENT[2]-(b[5]+shell_pcb_top_air)>=front_module_pcb_min_roof
 cover-=local_clearance(b,shell_pcb_top_air)
for b in PCB_BEAM_CLEARANCE_BOUNDS:
 cover-=local_clearance(b)
pin_top=REFERENCE_PLACEMENT[2]-front_module_gpio_pin_pocket_roof
cover-=local_clearance((GPIO_PIN_POCKET_X-GPIO_PIN_POCKET_WIDTH/2,GPIO_PIN_POCKET_Y-GPIO_PIN_POCKET_DEPTH/2,PCB_BOTTOM_Z,GPIO_PIN_POCKET_X+GPIO_PIN_POCKET_WIDTH/2,GPIO_PIN_POCKET_Y+GPIO_PIN_POCKET_DEPTH/2,pin_top))

x0,y0,z0,x1,y1,z1=HLE_BOUNDS
socket_top=z1+front_module_blank_socket_air
socket_roof=REFERENCE_PLACEMENT[2]-socket_top
assert socket_roof>=front_module_blank_socket_roof
socket_pocket=local_clearance((x0-front_module_blank_socket_air,y0-front_module_blank_socket_air,z0,x1+front_module_blank_socket_air,y1+front_module_blank_socket_air,socket_top))
socket_pocket=Pos(front_module_blank_socket_cover_x,front_module_blank_socket_cover_y-REFERENCE_PLACEMENT[1],0)*socket_pocket
cover-=socket_pocket
print('FLAT_COVER_UNDERSIDE_POCKET',dict(socket_air=front_module_blank_socket_air,central_roof=socket_roof))

# Receiver and compensated shaft remain the printed-screw-joint-v1 joint in shell.
# M2 countersunk ISO10642 is rejected there; explicit ISO7046 free head/seat
# fallback is shared by this standalone cover. Do not alter the released screws.
from bd_warehouse.fastener import CounterSunkScrew, ClearanceHole
COVER_SCREW_LENGTH=4.0 # Selected ISO7046 M2x4, fixed purchased standard.
screw=CounterSunkScrew('M2-0.4',length=COVER_SCREW_LENGTH,fastener_type='iso7046')
assert front_module_blank_thickness>=screw.head_height
for xx in [-front_module_screw_x,front_module_screw_x]:
 for yy in [-front_module_screw_y_offset,front_module_screw_y_offset]:
  cover-=Location((xx,yy,0))*ClearanceHole(screw,depth=front_module_blank_thickness,counter_sunk=True,mode=Mode.PRIVATE)
assert len(cover.solids())==1
assert abs(cover.bounding_box().max.Z)<1e-6
cover.color=Color(0.23,0.25,0.27)
publish('front_module_blank',cover,'Independent expansion cover',material='pla')
