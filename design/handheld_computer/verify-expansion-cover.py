"""Inspect the exact committed sealed cover, hardware clearance and removal path."""
import argparse
import json
from pathlib import Path
from build123d import Box, Cylinder, Pos, import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

p = argparse.ArgumentParser()
p.add_argument('--revision', required=True)
p.add_argument('--output', required=True)
a = p.parse_args()
root = Path(f'.work/cache/cad-workbench/designs/handheld_computer/builds/{a.revision}/validated/objects')
objects = {f.stem: import_step(f) for f in root.glob('*/*.step')}

def bounds(s):
    b = s.bounding_box()
    return {'min': list(b.min), 'max': list(b.max)}

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

pcb = objects['pi_baseboard_lite']
physical = [s for s in pcb.children if s.label not in ('board_copper', 'board_pad', 'board_via')]
assert physical, 'Missing released PCB physical bodies'
cover = objects['front_module_blank']
changed = ['front_module_blank', 'pcb_mount_screw_1', 'pcb_mount_screw_2', 'pcb_mount_spacer_1', 'pcb_mount_spacer_2']
targets = ['shell', 'base', 'pi4b', 'cooling_fan', 'fascia', 'fan_collar', 'passive_heatsink']
r = {'revision': a.revision, 'method': 'Exact OCC per-solid checks of committed world-frame STEP; PCB copper/pad/via visualization excluded.', 'checks': {}, 'limits': ['No physical print, module insertion, torque, load or repeated-removal test.', 'The central underside recess leaves a nominal0.645001mm non-load-bearing roof and0.1mm air; actual print and component tolerances remain unverified.', 'Removal checks sample vertical positions; monotonic clearance pockets and absence of undercuts are also checked visually.', 'Existing whole-product FPC, harness and cooling qualification remains outside this cover change.']}
for name in changed:
    s = objects[name]
    checks = {n: common(s, objects[n]) for n in targets}
    checks['physical_pcb'] = round(sum(common(s, t) for t in physical), 7)
    for n in changed:
        if n != name:
            checks[n] = common(s, objects[n])
    r['checks'][name] = {'bounds': bounds(s), 'solid_count': len(s.solids()), 'shared_volume_mm3': checks}
    print(name, r['checks'][name], flush=True)

# Probe the former through-openings at their old positions. These probes must
# lie completely inside the new cover's skin, above its blind underside pockets.
probes = {
    'former_left_tip_hole': Pos(-16, -32, 26.85)*Cylinder(1.0, 0.2),
    'former_right_tip_hole': Pos(16, -32, 26.85)*Cylinder(1.0, 0.2),
    'sealed_flat_socket_roof': Pos(0, -34, 26.85)*Box(8, 3, 0.2),
}
r['closed_skin'] = {n: {'probe_volume_mm3': round(s.volume, 7), 'cover_volume_mm3': common(s, cover)} for n, s in probes.items()}
r['closed_skin_passed'] = all(abs(c['probe_volume_mm3']-c['cover_volume_mm3']) < 1e-5 for c in r['closed_skin'].values())

# Four cover fasteners are removed for this service operation; every PCB
# fastener, spacer and enclosure-mounted body stays in place.
fixed = {n: objects[n] for n in targets + changed[1:] + ['retainer', 'bezel']}
r['vertical_removal'] = {}
for lift in [0.1, 0.6, 1.4, 2.0, 5.0, 10.0]:
    moving = Pos(0, 0, lift)*cover
    collisions = {n: common(moving, s) for n, s in fixed.items()}
    collisions['physical_pcb'] = round(sum(common(moving, s) for s in physical), 7)
    r['vertical_removal'][str(lift)] = collisions
    print('cover lift', lift, collisions, flush=True)

r['socket_top_z_mm'] = max(s.bounding_box().max.Z for s in physical)
r['socket_air_mm'] = 0.1
r['socket_central_roof_mm'] = round(cover.bounding_box().max.Z-r['socket_top_z_mm']-r['socket_air_mm'], 6)
r['screw_tip_cover_clearance_mm'] = {n: round(objects[n].distance_to(cover), 6) for n in changed[1:3]}
r['corner_mounts'] = {n: {'shared_volume_with_cover_mm3': common(objects[n], cover), 'head_top_z_mm': round(objects[n].bounding_box().max.Z, 6)} for n in [f'front_module_screw_{i}' for i in range(1, 5)]}
r['collision_passed'] = all(v < 1e-5 for c in r['checks'].values() for v in c['shared_volume_mm3'].values())
r['removal_passed'] = all(v < 1e-5 for c in r['vertical_removal'].values() for v in c.values())
r['minimum_roof_passed'] = r['socket_central_roof_mm'] >= 0.6-1e-5
r['flat_top_passed'] = abs(cover.bounding_box().max.Z-27) < 1e-5
design = json.loads(Path('design/handheld_computer/source/design.json').read_text())
cover_object = next(o for o in design['objects'] if o['id'] == 'front_module_blank')
r['separate_part_passed'] = cover_object['target'] == 'front_module_cover'
r['cover_part_id'] = cover_object['target']
r['corner_fasteners_passed'] = all(v['shared_volume_with_cover_mm3'] < 1e-5 and abs(v['head_top_z_mm']-27) < 1e-5 for v in r['corner_mounts'].values())
r['single_piece_cover_passed'] = len(cover.solids()) == 1
Path(a.output).write_text(json.dumps(r, ensure_ascii=False, indent=2)+'\n')
print({k:v for k,v in r.items() if k.endswith('_passed')}, flush=True)
assert all(v for k,v in r.items() if k.endswith('_passed')), 'Cover acceptance check failed'
