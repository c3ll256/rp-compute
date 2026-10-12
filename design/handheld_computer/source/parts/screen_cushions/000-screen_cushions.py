# Custom die-cut, non-adhesive compliant supports; drawing p5 forbids glue
# on the polarizer. Material compatibility and pressure need physical testing.
GLASS_W=62.8
GLASS_H=42.82
GLASS_Y=-1.77
front_cushion_thickness=param('front_cushion_thickness',0.2)
front_cushion_inset=param('front_cushion_inset',0.0)
front_cushion_window_w=param('front_cushion_window_w',59.4)
front_cushion_window_h=param('front_cushion_window_h',35.88)
front_cushion_tail_gap=param('front_cushion_tail_gap',12.0)
front_cushion_z=param('front_cushion_z',-1.4)
front=Pos(0,0,front_cushion_z)*extrude(Pos(0,GLASS_Y)*Rectangle(GLASS_W-2*front_cushion_inset,GLASS_H-2*front_cushion_inset)-Rectangle(front_cushion_window_w,front_cushion_window_h),amount=front_cushion_thickness)
front-=Pos(0,GLASS_Y-GLASS_H/2,front_cushion_z)*Box(front_cushion_tail_gap,4,4*front_cushion_thickness)
rear_cushion_thickness=param('rear_cushion_thickness',1.0)
rear_cushion_inset=param('rear_cushion_inset',0.0)
rear_cushion_window_w=param('rear_cushion_window_w',60.0)
rear_cushion_window_h=param('rear_cushion_window_h',38.0)
rear_cushion_tail_gap=param('rear_cushion_tail_gap',16.0)
rear_cushion_z=param('rear_cushion_z',-4.04)
rear=Pos(0,GLASS_Y,rear_cushion_z)*extrude(Rectangle(GLASS_W-2*rear_cushion_inset,GLASS_H-2*rear_cushion_inset)-Rectangle(rear_cushion_window_w,rear_cushion_window_h),amount=rear_cushion_thickness)
rear-=Pos(0,GLASS_Y-GLASS_H/2,rear_cushion_z)*Box(rear_cushion_tail_gap,6,4*rear_cushion_thickness)
front.color=Color(0.12,0.12,0.12)
rear.color=Color(0.24,0.24,0.25)
assert len(front.solids())==1 and len(rear.solids())==1
publish('front_cushion',front,'Front light seal',role='part')
publish('rear_cushion',rear,'Rear compliant support',role='part')