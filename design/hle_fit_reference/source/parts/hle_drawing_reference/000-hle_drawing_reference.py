# Drawing-based HLE104DV reference; no manufacturer model was available.
# Samtec hle-1xx-02-xxx-dv...series print:10.16x5.08x3.66; lead span6.58, pitch2.54.
hle_reference_margin=param('hle_reference_margin',0.0)
m=hle_reference_margin
L=10.16
W=5.08
H=3.66
PITCH=2.54
SPAN=6.58
body=Pos(0,0,(H+m)/2)*Box(L+2*m,W+2*m,H+m)
for i in range(4):
 for y in (-PITCH/2,PITCH/2):
  x=(i-1.5)*PITCH
  # Reference void, not internal contact design.
  body-=Pos(x,y,H-3.43/2+0.01)*Box(0.9,0.9,3.45)
  body=body.fuse(Pos(x,y/abs(y)*(W/2+(SPAN-W)/4),0.1)*Box(0.635,(SPAN-W)/2+0.02,0.2))
body.color=Color(0.18,0.18,0.18)
publish('hle_nominal_reference',body,'HLE drawing reference; contact details omitted')