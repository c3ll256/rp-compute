"""Read-only exact filled-zone proof; source coordinates, no backend writes."""
import re,json,math,hashlib
from pathlib import Path
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
p=Path('.work/pcb/pi_baseboard_lite/kicad/pi_baseboard_lite.kicad_pcb');s=p.read_text();stack=[];root=None
for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s):
 if t=='(':
  a=[]
  if stack:stack[-1].append(a)
  else:root=a
  stack.append(a)
 elif t==')':stack.pop()
 else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
def children(a,n):return [x for x in a if isinstance(x,list) and x and x[0]==n]
def child(a,n,default=None):return next(iter(children(a,n)),default)
zs={};obstacles=[];gndvias=[]
for z in children(root,'zone'):
 if child(z,'net',['net',''])[-1]!='GND':continue
 for f in children(z,'filled_polygon'):
  layer=child(f,'layer')[1];pts=child(f,'pts');poly=Polygon([(float(t[1]),float(t[2])) for t in children(pts,'xy')]).buffer(0)
  if not poly.is_empty:zs.setdefault(layer,[]).append(poly)
for fp in children(root,'footprint'):
 at=child(fp,'at');fx,fy=map(float,at[1:3]);fa=float(at[3]) if len(at)>3 else 0;rad=math.radians(fa)
 for pad in children(fp,'pad'):
  at=child(pad,'at');px,py=map(float,at[1:3]);pa=float(at[3]) if len(at)>3 else 0
  size=child(pad,'size');w,h=map(float,size[1:3]);pr=math.radians(pa-fa);corners=[]
  for x,y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:
   lx=px+x*math.cos(pr)+y*math.sin(pr);ly=py-x*math.sin(pr)+y*math.cos(pr)
   corners.append((fx+lx*math.cos(rad)+ly*math.sin(rad),fy-lx*math.sin(rad)+ly*math.cos(rad)))
  net=child(pad,'net',['net',''])[-1];obstacles.append(Polygon(corners).buffer(.31 if net=='GND' else .46))
for tr in children(root,'segment'):
 if child(tr,'net',['net',''])[-1]=='GND':continue
 a=child(tr,'start');b=child(tr,'end');w=float(child(tr,'width')[1]);obstacles.append(LineString([(float(a[1]),float(a[2])),(float(b[1]),float(b[2]))]).buffer(w/2+.46))
for via in children(root,'via'):
 at=child(via,'at');q=Point(float(at[1]),float(at[2]));net=child(via,'net',['net',''])[-1];r=float(child(via,'size')[1])/2
 obstacles.append(q.buffer(r+(.31 if net=='GND' else .46)))
 if net=='GND':gndvias.append(q)
inner=max(zs['In1.Cu'],key=lambda p:p.area);top=zs['F.Cu'];largest=max(top,key=lambda p:p.area);obs=unary_union(obstacles);result=[]
for poly in top:
 if poly==largest or any(poly.contains(v) for v in gndvias):continue
 safe=poly.buffer(-.31).intersection(inner.buffer(-.31)).difference(obs)
 
 if safe.is_empty:
  print('NO safe through-via site; placement/routing repair needed',poly.area,poly.bounds);continue
 q=safe.representative_point();x,y=q.x,q.y
 result.append({'net':'GND','diameterMm':.6,'drillMm':.3,'native_xy_mm':[x,y],'source_xy_mm':[round(x-100,6),round(100-y,6)],'lobe_area_mm2':poly.area,'lobe_native_bbox_mm':poly.bounds,'top_boundary_clearance_mm':q.distance(poly.boundary),'inner_boundary_clearance_mm':q.distance(inner.boundary),'obstacle_residual_margin_mm':q.distance(obs),'method':'Actual F.Cu unbridged non-largest GND polygon and largest In1.Cu GND plane eroded .31mm; excluded all pads, foreign tracks across stack, and existing vias conservatively.'})
r={'inspected_kicad_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'sites':result};Path('design/pi_baseboard_lite/additional-front-ground-via-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
