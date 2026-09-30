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
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--revision',required=True)
parser.add_argument('--output',default='/tmp/rp-raised-pcb-fit.json')
parser.add_argument('--release',required=True)
args=parser.parse_args()
REVISION=args.revision
RELEASE=args.release
design=json.loads((ROOT/'design/handheld_computer/source/design.json').read_text())
placed=next(o for o in design['objects'] if o['id']=='pi_baseboard_lite')
POSITION=tuple(placed['transform']['positionMm'])
assert placed['transform']['rotationDeg']==[0,0,0]
step=ROOT/f'manufacturing/pi_baseboard_lite/releases/{RELEASE}/package/assembly.step'
root=ROOT/f'.work/cache/cad-workbench/designs/handheld_computer/builds/{REVISION}/validated/objects'
objects={}
for path in root.glob('*/*.step'):
 if path.stem in ['shell','base','fascia','retainer','bezel','front_module_blank','front_cushion','rear_cushion','pi4b','retainer_screw_1','retainer_screw_3','pcb_mount_screw_1','pcb_mount_screw_2']:
  objects[path.stem]=import_step(path)
raw=import_step(step)
parts=[]
for i,c in enumerate(raw.children):
 if c.label in ['board_copper','board_pad','board_via']:continue
 parts.append((f'{i}:{c.label}',c.moved(Location(POSITION))))
# Sharp p26 nominal glass is a drawing-derived clearance probe, never a vendor asset.
glass=(Pos(0,-1.77,-2.22)*Box(62.8,42.82,1.64)).moved(Location((0,21.521201483,35.310909266),(13,0,0)))
objects['nominal_panel_envelope']=glass
required={'shell','front_module_blank','fascia','retainer','pi4b','pcb_mount_screw_1','pcb_mount_screw_2','retainer_screw_1','retainer_screw_3'}
assert required<=objects.keys(), f'Missing exact CAD objects for revision{REVISION}: {required-objects.keys()}'

def bbox(s):
 b=s.bounding_box();return {'min':[round(x,6) for x in b.min],'max':[round(x,6) for x in b.max]}
def meet(a,b):
 a=a.bounding_box(optimal=False);b=b.bounding_box(optimal=False)
 return all(tuple(a.min)[i]<tuple(b.max)[i]+1e-6 and tuple(b.min)[i]<tuple(a.max)[i]+1e-6 for i in range(3))
r={'cad_revision':REVISION,'pcb_release':RELEASE,'pcb_step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),'placement':{'position_mm':list(POSITION),'rotation_deg':[0,0,0],'xy_basis':'J_PI source pad centroid(-13.5,21) aligns with Pi world(-13.5,2). KiCad STEP offset(+100,-100) yields translation(-100,81).','z_basis':'User requested raised upper-shell mounting;21.8mm is agent default4.3mm lift. User authorized higher GPIO and lower8pin sockets. ESQ11.05mm nominal housing gives4.75..6.25mm engagement from official/third-party Pi tip datums; STEP also offsets bottom bodies by0.085mm.'},'method':'OCC per-solid volume intersections of real released substrate/component bodies against world-transformed CAD objects; copper/pad/via visual bodies excluded. Nominal glass is an explicit drawing-based negative probe.','body_bounds':{n:bbox(s) for n,s in parts},'target_bounds':{n:bbox(s) for n,s in objects.items()},'collisions':{},'limits':['ESQ and HLE are explicitly modeled manufacturer-drawing reference envelopes, not vendor STEP or internal contact qualification.','PCB STEP substrate0.71mm versus finished0.8mm; model pads/components add face offsets.','Native tail13.7+/-0.5mm is an authorized estimate. FPC contact, insertion stop and physical latch access remain prototype checks.','No physical print, connector mating or thermal test performed.']}
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
 Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
board_body=next(part for label,part in parts if label.endswith(':board_PCB'))
r['screw1_to_substrate_clearance_mm']=round(board_body.distance_to(objects['retainer_screw_1']),6)
r['screw1_clearance_expectation']={'source':'default','minimum_mm':0.5,'passed':r['screw1_to_substrate_clearance_mm']>=0.5}
r['pcb_to_shell_distance_mm']=round(board_body.distance_to(objects['shell']),6)
r['fixed_mount_screw_lengths_mm']={name:round(objects[name].bounding_box().max.Z-POSITION[2],6) for name in ['pcb_mount_screw_1','pcb_mount_screw_2']}
fpc=next(part for label,part in parts if label.startswith('6:'))
r['fpc_body_to_nominal_glass_clearance_mm']=round(fpc.distance_to(glass),6)
Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
print('Completed',r['screw1_to_substrate_clearance_mm'],flush=True)

# Ordinary top electronics: geometric air clearance, excluding connectors and solder copper.
thermal={}
for label,part in parts:
 if label.endswith(':board_PCB') or 'drawing-reference' in label or label.startswith('6:'):continue
 if part.bounding_box().min.Z<POSITION[2]+0.7:continue
 ds={n:round(part.distance_to(objects[n]),6) for n in ['shell','fascia','retainer','front_module_blank','nominal_panel_envelope']}
 thermal[label]={'clearance_mm':min(ds.values()),'to':min(ds,key=ds.get),'by_target_mm':ds}
r['ordinary_top_air_clearances']=thermal
r['minimum_ordinary_top_air_mm']=min(x['clearance_mm'] for x in thermal.values())
r['thermal_clearance_expectation']={'source':'default','minimum_mm':1.5,'passed':r['minimum_ordinary_top_air_mm']>=1.5-1e-5}
r['hle_top_world_z_mm']=next(part.bounding_box().max.Z for label,part in parts if 'hle-104' in label)
r['hle_top_below_deck_mm']=27-r['hle_top_world_z_mm']
r['required_structural_intersection_check_passed']=all(not r['collisions'][n] for n in ['shell','front_module_blank','fascia','retainer','bezel','nominal_panel_envelope','pcb_mount_screw_1','pcb_mount_screw_2','retainer_screw_1','retainer_screw_3'])
Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
print('THERMAL',r['minimum_ordinary_top_air_mm'],thermal,flush=True)

# Upper-shell beams/guides are new; check the retained real Pi independently.
volume=0
for ps in objects['pi4b'].solids():
 for ts in objects['shell'].solids():
  if not meet(ps,ts):continue
  op=BRepAlgoAPI_Common(ps.wrapped,ts.wrapped);prop=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),prop);volume+=prop.Mass()
r['pi_to_upper_shell_shared_volume_mm3']=round(volume,6)
r['pi_to_upper_shell_clearance_check_passed']=volume<=1e-5
Path(args.output).write_text(json.dumps(r,indent=2)+'\n')
print('PI_TO_SHELL',round(volume,6),flush=True)
