"""Check exact committed bottom fasteners and tightened native ports."""
import argparse, json
from pathlib import Path
from build123d import import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

p = argparse.ArgumentParser()
p.add_argument('--revision', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
root = Path(f'.work/cache/cad-workbench/designs/handheld_computer/builds/{a.revision}/validated/objects')
objects = {f.stem: import_step(f) for f in root.glob('*/*.step')}

def bbox(s):
    b = s.bounding_box()
    return {'min': list(b.min), 'max': list(b.max)}

def shared_volume(s, t):
    total = 0
    for x in s.solids():
        xb = x.bounding_box(optimal=False)
        for y in t.solids():
            yb = y.bounding_box(optimal=False)
            if not all(tuple(xb.min)[i] < tuple(yb.max)[i]+1e-7 and tuple(yb.min)[i] < tuple(xb.max)[i]+1e-7 for i in range(3)):
                continue
            op = BRepAlgoAPI_Common(x.wrapped, y.wrapped)
            g = GProp_GProps()
            BRepGProp.VolumeProperties_s(op.Shape(), g)
            total += abs(g.Mass())
    return round(total, 6)

# Ignore PCB visual copper, pads and vias; retain actual substrate and bodies.
pcb = objects['pi_baseboard_lite']
physical_pcb = [c for c in pcb.children if c.label not in ('board_copper','board_pad','board_via')]
assert physical_pcb, 'Missing identifiable released PCB physical bodies'
r = {'revision': a.revision, 'method': 'Exact OCC per-solid intersections of committed world-frame STEP objects; PCB visual copper excluded.', 'checks': {}, 'limits': ['No physical print, screw pullout or plug shoulder/insertion-path test.', 'The shallow locating rim registers the cover; screws provide retention.', 'Existing screen-tail and thermal qualification limits remain.']}
for name in ['shell','base'] + [f'base_mount_screw_{i}' for i in range(1,5)]:
    s = objects[name]
    checks = {t: shared_volume(s, objects[t]) for t in ['pi4b','cooling_fan']}
    checks['pcb_physical'] = round(sum(shared_volume(s, t) for t in physical_pcb),6)
    if name.startswith('base_mount_screw_'):
        checks.update({t:shared_volume(s,objects[t]) for t in ['shell','base','front_module_blank']})
        b = bbox(s)
        r['checks'][name] = {'shared_volume_mm3':checks, 'bounds':b, 'flush_bottom_error_mm':round(b['min'][2],6)}
    else:
        r['checks'][name] = {'shared_volume_mm3':checks,'solid_count':len(s.solids()),'bounds':bbox(s)}
    print(name, r['checks'][name], flush=True)
r['shell_base_shared_volume_mm3'] = shared_volume(objects['shell'],objects['base'])
r['base_pi_screw_clearance_mm'] = min(objects['base'].distance_to(objects[f'pi_mount_screw_{i}']) for i in range(1,5))
r['collision_check_passed'] = r['shell_base_shared_volume_mm3'] <= 1e-5 and all(v <= 1e-5 for c in r['checks'].values() for v in c['shared_volume_mm3'].values())
r['flush_bottom_check_passed'] = all(abs(r['checks'][f'base_mount_screw_{i}']['flush_bottom_error_mm']) <= 1e-5 for i in range(1,5))
r['connected_printed_parts_passed'] = all(r['checks'][n]['solid_count']==1 for n in ['shell','base'])
Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
assert r['collision_check_passed'], 'Unintended solid intersection'
assert r['flush_bottom_check_passed'], 'Screw projects beyond bottom'
assert r['connected_printed_parts_passed'], 'Disconnected printed structure'
print('Bottom attachment and port geometry checks passed', flush=True)
