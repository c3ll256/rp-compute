"""Check the removed rear-left inlet in the exact committed world-frame geometry."""
import argparse
import json
from pathlib import Path
from build123d import Box, Pos, import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
p=argparse.ArgumentParser()
p.add_argument('--revision',required=True)
p.add_argument('--output',required=True)
a=p.parse_args()
root=Path(f'.work/cache/cad-workbench/designs/handheld_computer/builds/{a.revision}/validated/objects')
objects={f.stem:import_step(f) for f in root.glob('*/*.step')}
def common(s, t):
    v = 0.0
    for x in s.solids():
        xb = x.bounding_box(optimal=False)
        for y in t.solids():
            yb = y.bounding_box(optimal=False)
            if not all(tuple(xb.min)[i] < tuple(yb.max)[i]+1e-7 and tuple(yb.min)[i] < tuple(xb.max)[i]+1e-7 for i in range(3)):
                continue
            op = BRepAlgoAPI_Common(x.wrapped, y.wrapped)
            assert op.IsDone(), 'Exact solid intersection failed'
            g = GProp_GProps()
            BRepGProp.VolumeProperties_s(op.Shape(), g)
            v += abs(g.Mass())
    return round(v, 7)

wall=Pos(-41.3,36,19)*Box(2.4,15.6,6)
shell=objects['shell']
result={'revision':a.revision,'scope':'Rear-left inlet removal only; exact OCC checks of the restored wall volume against committed world-frame solids.','restored_wall':{'expected_volume_mm3':round(wall.volume,7),'shell_volume_mm3':common(wall,shell),'thickness_mm':2.4},'retained_exhaust_slots':{},'hardware_shared_volume_mm3':{},'limits':['No full-product interference verdict or installed airflow/temperature measurement.']}
result['closed_wall_passed']=abs(result['restored_wall']['expected_volume_mm3']-result['restored_wall']['shell_volume_mm3'])<1e-5
for i in range(4):
 y=-38+(i-1.5)*4.4
 probe=Pos(-41.3,y,13.25)*Box(2.4,2.4,4.5)
 result['retained_exhaust_slots'][str(i+1)]={'center_y_mm':y,'shell_volume_mm3':common(probe,shell)}
result['exhaust_retained_passed']=all(c['shell_volume_mm3']<1e-5 for c in result['retained_exhaust_slots'].values())
for name,s in objects.items():
 if name=='shell': continue
 if name=='pi_baseboard_lite':
  physical=[c for c in s.children if c.label not in ('board_copper','board_pad','board_via')]
  assert physical,'Missing physical PCB bodies'
  v=round(sum(common(wall,c) for c in physical),7)
 else: v=common(wall,s)
 result['hardware_shared_volume_mm3'][name]=v
result['restored_wall_clearance_passed']=all(v<1e-5 for v in result['hardware_shared_volume_mm3'].values())
result['shell_single_valid_solid_passed']=len(shell.solids())==1 and shell.is_valid
Path(a.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
assert all(v for k,v in result.items() if k.endswith('_passed'))
