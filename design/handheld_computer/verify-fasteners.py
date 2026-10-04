"""Read-only checks of the committed world-frame mount and flush-screw geometry."""
import argparse,json
from pathlib import Path
from build123d import import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
p=argparse.ArgumentParser();p.add_argument('--revision',required=True);a=p.parse_args()
root=Path(f'.work/cache/cad-workbench/designs/handheld_computer/builds/{a.revision}/validated/objects')
o={f.stem:import_step(f) for f in root.glob('*/*.step')}
def meet(a,b):
 x=a.bounding_box(optimal=False);y=b.bounding_box(optimal=False)
 return all(tuple(x.min)[i]<tuple(y.max)[i]+1e-6 and tuple(y.min)[i]<tuple(x.max)[i]+1e-6 for i in range(3))
def volume(a,b):
 v=0
 for x in a.solids():
  for y in b.solids():
   if not meet(x,y):continue
   op=BRepAlgoAPI_Common(x.wrapped,y.wrapped);g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g);v+=g.Mass()
 return round(v,6)
r={'revision':a.revision,'nominal_corner_axes_mm':[[-13.5,-27],[-13.5,31],[35.5,-27],[35.5,31]],'checks':{},'physical_limits':['No printed fit, screw pullout, tightening torque or cooler compatibility qualified.','Pi four screw heads seat in printed shelves; PCB laminate holes are not countersunk. Metal heatsink threads receive2.4mm engagement.']}
for i in range(1,5):
 n=f'pi_mount_screw_{i}';s=o[n]
 v={k:volume(s,o[k]) for k in ['shell','pi4b','pi_baseboard_lite','base']}
 r['checks'][n]={'shared_volume_mm3':v,'base_clearance_mm':round(s.distance_to(o['base']),6),'bounds':{'min':list(s.bounding_box().min),'max':list(s.bounding_box().max)}}
 print(n,r['checks'][n],flush=True)
for i in range(1,5):
 n=f'front_module_screw_{i}'
 r['checks'][n]={'head_top_z':round(o[n].bounding_box().max.Z,6),'flush_to_deck_mm':round(o[n].bounding_box().max.Z-27,6),'shared_volume_mm3':{k:volume(o[n],o[k]) for k in ['shell','front_module_blank']}}
for i in range(1,5):
 n=f'retainer_screw_{i}'
 r['checks'][n]={'shared_volume_mm3':{k:volume(o[n],o[k]) for k in ['fascia','retainer','bezel','pi_baseboard_lite']}}
for i in range(1,3):
 n=f'fan_collar_screw_{i}'
 r['checks'][n]={'shared_volume_mm3':{k:volume(o[n],o[k]) for k in ['shell','fan_collar','cooling_fan','pi_baseboard_lite','pi4b']},'head_top_z':round(o[n].bounding_box().max.Z,6),'flush_to_collar_mm':round(o[n].bounding_box().max.Z-17.4,6)}
r['new_screw_collision_check_passed']=all(v<=1e-5 for x in r['checks'].values() for v in x['shared_volume_mm3'].values())
r['external_flush_check_passed']=all(abs(r['checks'][f'front_module_screw_{i}']['flush_to_deck_mm'])<=1e-5 for i in range(1,5))
r['bottom_head_gap_check_passed']=all(r['checks'][f'pi_mount_screw_{i}']['base_clearance_mm']>=0.3 for i in range(1,5))
Path('design/handheld_computer/fastener-fit-check.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if 'passed' in k}),flush=True)
