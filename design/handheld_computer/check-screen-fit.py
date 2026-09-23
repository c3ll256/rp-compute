"""Read-only supplementary checks of the exact Workbench STEP.
Run with CAD runtime Python: check-screen-fit.py STEP_PATH REVISION.
Reports only numeric geometry; physical display/FPC are drawing envelopes.
"""
import sys, json, math, hashlib
from pathlib import Path
from build123d import *
p=Path(sys.argv[1]); revision=sys.argv[2]
assembly=import_step(str(p)); objects={c.label:c for c in assembly.children}
F=Pos(0,21.521201483,35.310909266)*Rot(13,0,0)

def bounds(s):
 b=s.bounding_box(); return {'min':list(b.min),'max':list(b.max)}
def possible(a,b):
 a=a.bounding_box(); b=b.bounding_box()
 return all(min(hi_a,hi_b)-max(lo_a,lo_b)>1e-7 for hi_a,hi_b,lo_a,lo_b in zip(a.max,b.max,a.min,b.min))
def overlap(a,b):
 if not possible(a,b): return 0.0
 v=a.intersect(b)
 if v is None: return 0.0
 return sum(s.volume for s in v.solids())
def against(shape, names):
 return {n:round(sum(overlap(shape,s) for s in objects[n].solids()),8) for n in names}
raw_r=1.5; cy=-24.18; cz=-3.73; end_y=-16.192388980384692
thick=.8
arc=Pos(0,cy,cz)*Rot(0,90,0)*(Cylinder(raw_r+thick/2,11)-Cylinder(raw_r-thick/2,12))
arc=arc & (Pos(0,cy-raw_r-thick/2,cz)*Box(12,2*raw_r+thick,2*raw_r+thick))
start=Pos(0,-23.68,-2.23)*Box(11,1,thick)
back=Pos(0,(cy+end_y)/2,-5.23)*Box(11,end_y-cy,thick)
printed=['shell','fascia','bezel','retainer','front_cushion','rear_cushion','pi4b']
route_checks={key:against(F*shape,printed) for key,shape in [('entry',start),('bend',arc),('return',back)]}
# Conservative closed+open actuator reservation; perform operations with pod removed.
latch=F*Pos(0,end_y-1.4,(-10.03-4.53)/2)*Box(11.1,8,5.5)
glass=F*Pos(0,-1.77,(-1.4-3.04)/2)*Box(62.8,42.82,1.64)
pi_shell=[]
for i,s in enumerate(objects['pi4b'].solids()):
 v=overlap(objects['shell'],s)
 if v>1e-5: pi_shell.append({'solid':i,'volume_mm3':v})
contacts={a+'/'+b:objects[a].distance_to(objects[b]) for a,b in [('front_cushion','bezel'),('rear_cushion','retainer'),('bezel','fascia'),('bezel','retainer'),('retainer','fascia')]}
# Workbench stores parameters by target. Keep literal expected values in report.
report={'revision':revision,'step_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'method':'Supplementary per-solid OCC checks on exact exported STEP; drawing-derived negative envelopes are not real panel/FPC models','solid_count':len(assembly.solids()),'valid':all(s.is_valid for s in assembly.solids()),'pi_shell_overlap_mm3':pi_shell,'fpc_negative_envelope_overlap_mm3':route_checks,'latch_reservation_overlap_mm3':against(latch,printed),'nominal_glass_overlap_mm3':against(glass,printed),'contact_distances_mm':contacts,'object_bounds_mm':{n:bounds(s) for n,s in objects.items()},'nominal_front_rise_mm':1.0,'glass_locator_mm':[63.4,43.42],'physical_qualification':'13.7mm native tail total length, pad stress/material and actual insertion stop remain unverified; no PCB'}
print(json.dumps(report,indent=2))
