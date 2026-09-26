# Supplementary geometry check; run from project root. Requires the recorded Workbench build cache.
import json,math,hashlib
from pathlib import Path
from build123d import import_step,Location,Box,Pos
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
ROOT=Path.cwd(); release='a86e69186bf23c3da05e2f175206bed8d832595bc02e720044ea76bf4abc8db3'
step=ROOT/f'manufacturing/pi_baseboard_lite/releases/{release}/package/assembly.step'

# Use the root-transformed solids from each child, not its unplaced underlying prototype.
# Assembly children do not inherit the new root location in build123d bounding_box;
# apply rigid world placement independently to the original STEP occurrences.
raw=import_step(step)
parts=[]
for i,c in enumerate(raw.children):
 if c.label in ['board_copper','board_pad','board_via']:continue
 parts.append((c.label+'_'+str(i),c.moved(Location((-100,86.8,20)))))
root=ROOT/'.work/cache/cad-workbench/designs/handheld_computer/builds/b49c0e0d8b89ea780446f1519afb5778f70234261dc1e2f2a94ad350a1c84688/validated/objects'
objects={}
for path in root.glob('*/*.step'):
 if path.stem in ['shell','base','fascia','retainer','bezel','front_module_blank','front_cushion','rear_cushion','pi4b','retainer_screw_1','retainer_screw_3']:
  objects[path.stem]=import_step(path)
# Sharp p26 nominal panel: 62.8 x42.82 x1.64, active-centre datum and existing locator.
# This probe is a drawing-derived negative envelope, never a vendor panel model.
glass=(Pos(0,-1.77,-2.22)*Box(62.8,42.82,1.64)).moved(Location((0,21.521201483,35.310909266),(13,0,0)))
objects['nominal_panel_envelope']=glass

def bbox(s):
 b=s.bounding_box();return {'min':[round(x,6) for x in b.min],'max':[round(x,6) for x in b.max]}
def meet(a,b):
 a=a.bounding_box(optimal=False);b=b.bounding_box(optimal=False);return all(tuple(a.min)[i]<tuple(b.max)[i]+1e-6 and tuple(b.min)[i]<tuple(a.max)[i]+1e-6 for i in range(3))
r={'pcb_release':release,'pcb_step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),'placement':{'position_mm':[-100,86.8,20],'rotation_deg':[0,0,0],'xy_basis':'Pi official drawing GPIO centroid is32.5mm from board front and3.5mm from left edge; current Pi frontY=-30.5, leftX=-17 gives world(-13.5,2.0). PCB J_PI centroid(-13.5,15.2) hence board deltaY=-13.2. STEP is offset(+100,-100) from source board frame.','z_basis':'Provisional PCB substrate lower datum20mm; original Pi STEP pins endZ17 but official Pi drawing says GPIO height8.5 above board, hence15.5 world. Retained SSQ housing8.51, engagement range3.68..6.35. This discrepancy is not an exact stack qualification.'},'method':'Supplementary OCC exact body intersections and distances, using immutable released STEP and Workbench object STEP geometry. Board copper/pad/via visual subobjects excluded from structural collision probes; substrate and all mounted component bodies included. Nominal panel is a drawing-derived clearance envelope, not a manufactured screen model.','body_bounds':{n:bbox(s) for n,s in parts},'target_bounds':{n:bbox(s) for n,s in objects.items()},'collisions':{}}
for n,t in sorted(objects.items(),key=lambda kv:kv[0]=='pi4b'):
 hits=[]
 for label,p in parts:
  if not meet(p,t):continue
  try:
   vol=0
   for ps in p.solids():
    for ts in t.solids():
     if not meet(ps,ts):continue
     op=BRepAlgoAPI_Common(ps.wrapped,ts.wrapped);prop=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),prop);vol+=prop.Mass()
   if vol>1e-5:hits.append({'component':label,'volume_mm3':round(vol,6)})
  except Exception as e:hits.append({'component':label,'error':str(e)})
 r['collisions'][n]=hits
 print(n,hits,flush=True)
 Path('/tmp/pi_baseboard_lite_fit_recheck.json').write_text(json.dumps(r,indent=2)+'\n')
r['panel_distance_status']='Separating-axis lower bound recorded separately; no exact nearest-point claim'
Path('/tmp/pi_baseboard_lite_fit_recheck.json').write_text(json.dumps(r,indent=2)+'\n')
print('DONE',flush=True)
