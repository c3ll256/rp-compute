# Drawing-based fit reference, not manufacturer STEP or contact simulation.
# Samtec esq_th.pdf style12: housing11.05, tail2.29, pitch2.54; series print length20*2.54+0.51, width5.08.
esq_reference_margin=param('esq_reference_margin',0.0)
PITCH=2.54
L=20*PITCH+0.51
W=5.08
H=11.05
TAIL=2.29
PIN=0.635
CAVITY=1.0 # Reference void only; internal contact geometry unresolved.
DEPTH=6.35
m=esq_reference_margin
body=Pos(0,0,(H+m)/2)*Box(L+2*m,W+2*m,H+m)
pins=[]
for i in range(20):
 for y in (-PITCH/2,PITCH/2):
  x=(i-9.5)*PITCH
  body=body-Pos(x,y,H-DEPTH/2+0.01)*Box(CAVITY,CAVITY,DEPTH+0.02)
  pins.append(Pos(x,y,-TAIL/2)*Box(PIN,PIN,TAIL))
reference=Compound(children=[body]+pins)
reference.color=Color(0.18,0.18,0.18)
publish('esq_nominal_reference',reference,'ESQ drawing reference; contact details omitted')