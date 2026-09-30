"""Read-only body checks for a recorded CAD build and immutable PCB release.
Run from project root. This does not rebuild or edit CAD/PCB geometry.
"""
import json, hashlib, math
from pathlib import Path
from build123d import import_step, Location, Box, Pos
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
ROOT=Path.cwd()
REVISION='9a3dede54ad704a9ee8bb8a1d49fa1f3453efcacc46d7d06d5e1468546e00744'
RELEASE='a183ffa45c8d8cf64f65fdf30fee1c9048fcdda8b56f28e06d5ca1ee549fda45'
POSITION=(-100,81,17.5)
step=ROOT/f'manufacturing/pi_baseboard_lite/releases/{RELEASE}/package/assembly.step'
raw=import_step(step)
parts=[]
for i,c in enumerate(raw.children):
 if c.label in ['board_copper','board_pad','board_via']:continue
 parts.append((f'{i}:{c.label}',c.moved(Location(POSITION))))
root=ROOT/f'.work/cache/cad-workbench/designs/handheld_computer/builds/{REVISION}/validated/objects'
objects={}
for path in root.glob('*/*.step'):
 if path.stem in ['shell','base','fascia','retainer','bezel','front_module_blank','front_cushion','rear_cushion','pi4b','retainer_screw_1','retainer_screw_3']:
  objects[path.stem]=import_step(path)
# Sharp p26 nominal glass is a drawing-derived clearance probe, never a vendor asset.
glass=(Pos(0,-1.77,-2.22)*Box(62.8,42.82,1.64)).moved(Location((0,21.521201483,35.310909266),(13,0,0)))
objects['nominal_panel_envelope']=glass

def bbox(s):
 b=s.bounding_box();return {'min':[round(x,6) for x in b.min],'max':[round(x,6) for x in b.max]}
def meet(a,b):
 a=a.bounding_box(optimal=False);b=b.bounding_box(optimal=False)
 return all(tuple(a.min)[i]<tuple(b.max)[i]+1e-6 and tuple(b.min)[i]<tuple(a.max)[i]+1e-6 for i in range(3))
r={'cad_revision':REVISION,'pcb_release':RELEASE,'pcb_step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),'placement':{'position_mm':list(POSITION),'rotation_deg':[0,0,0],'xy_basis':'J_PI source pad centroid(-13.5,21) aligns with Pi world(-13.5,2). KiCad STEP offset(+100,-100) yields translation(-100,81).','z_basis':'17.5mm provisional lower substrate datum within official Pi pin-tip15.5 plus SLW4.57 housing minus2.16..2.92 insertion =>17.15..17.91. Generic socket STEP is not exact SLW; third-party Pi pins reach17mm.'},'method':'OCC per-solid volume intersections of real released substrate/component bodies against world-transformed CAD objects; copper/pad/via visual bodies excluded. Nominal glass is an explicit drawing-based negative probe.','body_bounds':{n:bbox(s) for n,s in parts},'target_bounds':{n:bbox(s) for n,s in objects.items()},'collisions':{},'limits':['Stock KiCad sockets have8.5mm bodies, selected SLW housing4.57mm; socket collisions are proxy observations, not actual SLW qualification.','PCB STEP substrate0.71mm versus finished thickness0.8mm; use finished stack for manufacturing.','Native FPC path/contact/stop not represented by a vendor panel STEP.']}
for name,target in sorted(objects.items(),key=lambda kv:kv[0]=='pi4b'):
 hits=[]
 for label,part in parts:
  if not meet(part,target):continue
  volume=0
  for ps in part.solids():
   for ts in target.solids():
    if not meet(ps,ts):continue
    op=BRepAlgoAPI_Common(ps.wrapped,ts.wrapped);prop=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),prop);volume+=prop.Mass()
  if volume>1e-5:hits.append({'component':label,'volume_mm3':round(volume,6)})
 r['collisions'][name]=hits
 print(name,hits,flush=True)
 Path('/tmp/rp-compact-pcb-fit.json').write_text(json.dumps(r,indent=2)+'\n')
board_body=next(part for label,part in parts if label.endswith(':board_PCB'))
r['screw1_to_substrate_clearance_mm']=round(board_body.distance_to(objects['retainer_screw_1']),6)
r['screw1_clearance_expectation']={'source':'default','minimum_mm':0.5,'passed':r['screw1_to_substrate_clearance_mm']>=0.5}
Path('/tmp/rp-compact-pcb-fit.json').write_text(json.dumps(r,indent=2)+'\n')
print('Completed',r['screw1_to_substrate_clearance_mm'],flush=True)
