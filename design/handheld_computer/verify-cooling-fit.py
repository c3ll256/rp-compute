"""Read-only checks of exact committed CAD + frozen released PCB bodies."""
import argparse,json,hashlib,math
from pathlib import Path
from build123d import import_step,Pos,Cylinder,Box,Location,Sphere,Vector,Align,Axis
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);p.add_argument('--release',required=True);p.add_argument('--output',default='/tmp/rp-passive-fit.json');p.add_argument('--wire-only',action='store_true');a=p.parse_args()
root=Path(f'.work/cache/cad-workbench/designs/handheld_computer/builds/{a.revision}/validated/objects');o={f.stem:import_step(f) for f in root.glob('*/*.step')}
step=Path(f'manufacturing/pi_baseboard_lite/releases/{a.release}/package/assembly.step');raw=import_step(step)
parts=[(f'{i}:{c.label}',c.moved(Location((-100,81,21.8)))) for i,c in enumerate(raw.children) if c.label not in ['board_copper','board_pad','board_via']]
def bbox(s):
 b=s.bounding_box();return {'min':[round(x,6) for x in b.min],'max':[round(x,6) for x in b.max]}
def meet(a,b):
 x=a.bounding_box(optimal=False);y=b.bounding_box(optimal=False);return all(tuple(x.min)[i]<tuple(y.max)[i]+1e-6 and tuple(y.min)[i]<tuple(x.max)[i]+1e-6 for i in range(3))
def volume(a,b):
 if not meet(a,b):return 0.
 v=0
 for x in a.solids():
  for y in b.solids():
   if not meet(x,y):continue
   op=BRepAlgoAPI_Common(x.wrapped,y.wrapped);g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g);v+=g.Mass()
 return round(v,6)
r={'revision':a.revision,'pcb_release':a.release,'pcb_step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),'checked':{},'bounds':{},'limits':['P165-B is a declared65x55x11mm manufacturer-photo reference, not vendor STEP; underside, reliefs, contact heights and fin layout remain physical inspection items.','TIM0.25mm modeled for review, not supplier thickness/compression evidence.','No temperature or installed flow rate measured.']}
if a.wire_only:
 r=json.loads(Path(a.output).read_text())
 assert r['revision']==a.revision and r['pcb_release']==a.release,'Cannot reuse checks from another build'
else:
 for n in ['passive_heatsink','cooling_fan','fan_collar','fan_corner_pads']:
  s=o[n];r['bounds'][n]=bbox(s);v={k:volume(s,o[k]) for k in ['shell','base','pi4b','fascia','retainer','front_module_blank','pcb_mount_screw_1','pcb_mount_screw_2']}
  hits=[{'label':label,'volume_mm3':vv} for label,part in parts if (vv:=volume(s,part))>1e-5]
  r['checked'][n]={'volume_mm3':v,'pcb_hits':hits,'pcb_body_gap_mm':round(s.distance_to(o['pi_baseboard_lite']),6)};print(n,r['checked'][n],flush=True)
  Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
 # Nominal fan upper face15.5; allow maximum +0.5mm thickness before3mm free intake.
 # Ignore manufacturer's wire stubs when establishing inlet datum, not collisions.
 inlet=Pos(-29,-38,17.5)*Cylinder(6,3)
 r['inlet_column_mm']={'diameter':12,'bottom_z':16,'height':3}
 r['inlet_hits']={n:volume(inlet,o[n]) for n in ['shell','front_module_blank','fan_collar','pi_baseboard_lite','passive_heatsink']}
 r['inlet_pcb_hits']=[{'label':label,'volume_mm3':v} for label,part in parts if (v:=volume(inlet,part))>1e-5]
 # Conservative mating plug/release volume in front of side-entry SH socket.
 fanpart=next((s for label,s in parts if 'JST_SH_SM02B' in label),None)
 if fanpart:
  r['J_FAN_world_bbox_mm']=bbox(fanpart)
  plug=Pos(0,-49.125,20.3)*Box(3.4,5.,2.8)
  r['J_FAN_front_plug_probe_mm']=bbox(plug)
  r['J_FAN_front_access_hits']={n:volume(plug,o[n]) for n in ['shell','front_module_blank','fan_collar','cooling_fan','passive_heatsink']}
  r['J_FAN_to_fan_gap_mm']=round(fanpart.distance_to(o['cooling_fan']),6)
  r['J_FAN_front_plug_limits']='Manufacturer mating plug dimensional reference plus0.2mm fitting allowance; horizontal assembly with bottom cover removed. Probe excludes intentional insertion into socket.'
 r['heatsink_to_HAT_minimum_mm']=round(o['passive_heatsink'].distance_to(o['pi_baseboard_lite']),6)
 r['heatsink_to_upper_shell_mm']=round(o['passive_heatsink'].distance_to(o['shell']),6)
 r['metal_threads']={f'pi_mount_screw_{i}':{'shared_volume_mm3':volume(o['passive_heatsink'],o[f'pi_mount_screw_{i}']),'intended_axial_engagement_mm':2.4} for i in range(1,5)}
 # Clear rear-left intake and left-side exhaust slots; no forward hot outlet.
 r['vent_slots']=[]
 for i in range(4):
  off=(i-1.5)*4.4
  for bank,probe,area in [('intake',Pos(-41.5,36+off,19)*Box(5.0,2.36,5.96),14.4),('exhaust',Pos(-41.5,-38+off,13.25)*Box(5.0,2.36,4.46),10.8)]:
   r['vent_slots'].append({'bank':bank,'area_mm2':area,'shell_obstruction_mm3':volume(probe,o['shell']),'internal_hits':[{'target':n,'volume_mm3':v} for n,t in parts+[(n,o[n]) for n in ['pi4b','fan_collar','passive_heatsink']] if (v:=volume(probe,t))>1e-5]})
# Installed two-wire bundle, explicit reserve rather than vendor formed-wire asset.
# Leads leave the rotated fan right-rear corner and rise outside its collar.
pts=[(-20.6,-31.6,12.95),(-10.4,-31.6,12.95),(-10.4,-31.6,20.3),(-10.4,-54.1,20.3),(0,-54.1,20.3),(0,-51.625,20.3)]
radius=2.0;ends=[0.0]*len(pts);angles=[0.0]*len(pts)
for j in range(1,len(pts)-1):
 u=(Vector(pts[j])-Vector(pts[j-1])).normalized();v=(Vector(pts[j+1])-Vector(pts[j])).normalized()
 angles[j]=math.acos(max(-1,min(1,u.dot(v))));ends[j]=radius*math.tan(angles[j]/2)
for j in range(len(pts)-1):assert ends[j]+ends[j+1]<(Vector(pts[j+1])-Vector(pts[j])).length+1e-6,'Adjacent bends overlap'
rounded=[Vector(pts[0])]
for j in range(1,len(pts)-1):
 av,bv,cv=map(Vector,[pts[j-1],pts[j],pts[j+1]]);u=(bv-av).normalized();v=(cv-bv).normalized();theta=angles[j]
 if theta<1e-6:rounded.append(bv);continue
 start=bv-u*ends[j];n=(v-u*math.cos(theta)).normalized();center=start+n*radius;axis=u.cross(v).normalized();r0=start-center;count=math.ceil(theta/math.radians(7.5))
 for k in range(count+1):
  ang=theta*k/count;rounded.append(center+r0*math.cos(ang)+axis.cross(r0)*math.sin(ang))
rounded.append(Vector(pts[-1]))
wire_hits=[];target=parts+[(n,o[n]) for n in ['shell','base','pi4b','fascia','retainer','front_module_blank','fan_collar','fan_collar_screw_1','fan_collar_screw_2','passive_heatsink','pcb_mount_screw_1','pcb_mount_screw_2']]
for av,bv in zip(rounded,rounded[1:]):
 dv=bv-av
 if dv.length<1e-8:continue
 shape=Cylinder(.7,dv.length,align=(Align.CENTER,Align.CENTER,Align.MIN));axis=Vector(0,0,1).cross(dv)
 if axis.length>1e-8:shape=shape.rotate(Axis((0,0,0),axis),Vector(0,0,1).get_angle(dv))
 elif dv.Z<0:shape=shape.rotate(Axis.X,180)
 shape=shape.translate(av)
 for n,t in target:
  vv=volume(shape,t)
  if vv>1e-5:wire_hits.append({'target':n,'volume_mm3':vv,'point_mm':list(av)})
for av in rounded:
 shape=Pos(*av)*Sphere(.7)
 for n,t in target:
  vv=volume(shape,t)
  if vv>1e-5:wire_hits.append({'target':n,'volume_mm3':vv,'point_mm':list(av)})
length=sum((Vector(b)-Vector(a)).length for a,b in zip(pts,pts[1:]))-2*sum(ends)+radius*sum(angles)+3.03
r['factory_lead_route']={'points_mm':pts,'bundle_OD_allowance_mm':1.4,'bend_radius_mm':radius,'lead_length_including_ends_mm':round(length,3),'minimum_factory_lead_length_mm':70,'length_passed':length<=70,'intersections':wire_hits,'limits':'Actual bent vendor AWG36 leads plus factory32AWG SH pigtail are fitted to this reserve; do not directly crimp AWG36 into SH. Connector plug modeled as reserve; no exact formed-wire CAD claimed.'}
r['power_cap_to_shell_volume_mm3']=volume(o['power_cap'],o['shell'])
# Discharge reserve, tolerance margin to the blower mouth and unobstructed side slots.
r['side_discharge_probe_mm']={'x':[-40.1,-37.4],'y':[-45.8,-30.2],'z':[11.01,15.49]}
discharge=Pos(-38.75,-38,13.25)*Box(2.7,15.6,4.48)
r['side_discharge_hits']={n:volume(discharge,o[n]) for n in ['shell','fan_collar','fan_corner_pads','pi4b','pi_baseboard_lite','passive_heatsink']}
r['front_exhaust_closed']=[]
for i in range(4):
 off=(i-1.5)*4.4
 probe=Pos(-11.5+off,-56.3,13.25)*Box(2.36,2.4,4.46)
 filled=volume(probe,o['shell']);r['front_exhaust_closed'].append({'probe_volume_mm3':round(probe.volume,6),'filled_volume_mm3':filled,'passed':abs(filled-probe.volume)<1e-4})
r['geometry_checks_passed']=all(v<=1e-5 for v in r['side_discharge_hits'].values()) and all(x['passed'] for x in r['front_exhaust_closed']) and all(v<=1e-5 for x in r['checked'].values() for v in x['volume_mm3'].values()) and all(not x['pcb_hits'] for x in r['checked'].values()) and all(v<=1e-5 for v in r['inlet_hits'].values()) and not r['inlet_pcb_hits'] and all(v<=1e-5 for v in r.get('J_FAN_front_access_hits',{}).values()) and all(v['shell_obstruction_mm3']<=1e-5 and not v['internal_hits'] for v in r['vent_slots']) and not wire_hits and length<=70
Path(a.output).write_text(json.dumps(r,indent=2)+'\n');print('FINAL',json.dumps({k:v for k,v in r.items() if k not in ['bounds','checked']}),flush=True)
