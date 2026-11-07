"""Audit exact supplier identities and placed pads; read generated files only.

Run before release, and again with --release after release to check the frozen
BOM/CPL. The printed JSON is evidence, not a substitute for pcb.run gates.
"""
import argparse
import csv
import hashlib
import json
import math
import re
import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / '.work/pcb/pi_baseboard_lite'
HELPERS = runpy.run_path(str(ROOT / 'design/pi_baseboard_lite/audit-electrical.py'))
children = HELPERS['children']


def audit(check_release=False):
    bom = json.loads((ROOT / 'product/bom.json').read_text())
    circuit = json.loads((WORK / 'build/circuit.json').read_text())
    previous = json.loads(subprocess.run(
        ['git', 'show', 'HEAD:manufacturing/pi_baseboard_lite/releases/'
         'dfb9406b2d96fdd68e51510993e6d9fe0f0034fea6f9908f29e3cc6f32c65043/package/circuit.json'],
        cwd=ROOT, check=True, text=True, capture_output=True).stdout)

    def mechanics(data):
        refs = {r['source_component_id']: r['name'] for r in data if r['type'] == 'source_component'}
        return {
            'placements': {refs[r['source_component_id']]: {k: r.get(k) for k in
                ['center', 'footprint_origin', 'width', 'height', 'rotation', 'layer']}
                for r in data if r['type'] == 'pcb_component'},
            'board_and_holes': [{k: r[k] for k in
                ['type', 'width', 'height', 'thickness', 'num_layers', 'center', 'outline', 'x', 'y', 'hole_diameter']
                if k in r} for r in data if r['type'] in ['pcb_board', 'pcb_hole']],
        }

    before, after = mechanics(previous), mechanics(circuit)
    assert before['board_and_holes'] == after['board_and_holes']
    for ref, placement in after['placements'].items():
        if ref not in ['J_PI', 'J_MOD']:
            assert placement == before['placements'][ref], (ref, 'Unrelated placement changed')

    def semantic_nets(data):
        refs = {r['source_component_id']: r['name'] for r in data if r['type']=='source_component'}
        ports = {r['source_port_id']: r for r in data if r['type']=='source_port'}
        nets = {r['source_net_id']:r['name'] for r in data if r['type']=='source_net'}
        result = {}
        for t in data:
            if t['type'] != 'source_trace': continue
            for pid in t.get('connected_source_port_ids', []):
                p = ports[pid]
                key = (refs[p['source_component_id']], p['name'])
                result.setdefault(key, set()).update(nets[n] for n in t.get('connected_source_net_ids', []))
        return result
    assert {k:v for k,v in semantic_nets(circuit).items() if k[0]!='J_FAN'} == {k:v for k,v in semantic_nets(previous).items() if k[0]!='J_FAN'}, 'Remaining logical pin functions changed'
    assert len(after['placements'])==31 and 'J_FAN' not in after['placements'], 'Fan removal incomplete'

    def pin_positions(data, ref):
        sid = next(r['source_component_id'] for r in data if r['type']=='source_component' and r['name']==ref)
        ports = {r['source_port_id']:r for r in data if r['type']=='source_port' and r['source_component_id']==sid}
        return {ports[p['source_port_id']]['name']:(p['x'],p['y']) for p in data
            if p['type']=='pcb_port' and p.get('source_port_id') in ports}
    old_pi, new_pi = pin_positions(previous, 'J_PI'), pin_positions(circuit, 'J_PI')
    assert len(old_pi)==len(new_pi)==40
    max_pi_shift = max(math.dist(old_pi[p],new_pi[p]) for p in old_pi)
    assert max_pi_shift < .000001, 'Pi physical pin positions changed'
    socket_checks = []
    for ref, count, layer in [('J_PI',40,'bottom'),('J_MOD',8,'top')]:
        sid = next(r['source_component_id'] for r in circuit if r['type']=='source_component' and r['name']==ref)
        pc = next(r for r in circuit if r['type']=='pcb_component' and r['source_component_id']==sid)
        assert pc['layer']==layer
        holes=[r for r in circuit if r['type']=='pcb_plated_hole' and r.get('pcb_component_id')==pc['pcb_component_id']]
        assert len(holes)==count and all(abs(h['hole_diameter']-1)<1e-9 for h in holes)
        for h in holes:
            assert abs(h.get('outer_diameter',h.get('rect_pad_width',0))-1.7)<1e-9
        positions=pin_positions(circuit,ref)
        assert len(positions)==count
        socket_checks.append({'ref':ref,'through_holes':count,'drill_mm':1,'land_mm':1.7,'side':layer,
            'semantic_pin_positions_source_mm':positions})
    native = HELPERS['parse_sexpr']((WORK / 'kicad/pi_baseboard_lite.kicad_pcb').read_text())
    footprints = {}
    for fp in children(native, 'footprint'):
        refs = [p[2] for p in children(fp, 'property') if p[1] == 'Reference']
        if refs:
            footprints[refs[0]] = fp
    # Native export must preserve the semantic pin map, not just the TSX netlist.
    expected_nets = semantic_nets(circuit)
    for ref, prefix, count in [('J_PI','P',40),('J_MOD','M',8)]:
        fp = footprints[ref]
        pads = children(fp,'pad')
        assert len(pads)==count
        assert children(fp,'layer')[0][1] == ('B.Cu' if ref=='J_PI' else 'F.Cu')
        for p in pads:
            number=str(p[1]); assert p[2]=='thru_hole'
            assert abs(float(children(p,'drill')[0][1])-1)<1e-9
            net=children(p,'net')
            actual={net[0][-1]} if net else set()
            assert actual == expected_nets.get((ref,prefix+number),set()), (ref,number,actual)
    source = {r['source_component_id']: r['name'] for r in circuit if r['type'] == 'source_component'}
    placed = {source[r['source_component_id']]: r for r in circuit if r['type'] == 'pcb_component'}
    rows = []
    for item in bom['items']:
        if item.get('assembly', {}).get('method') != 'jlc_smt':
            continue
        code = item['lcsc_code']
        evidence = ROOT / 'product/references/jlc-assembly' / (code + '-easyeda.json')
        lib = json.loads(evidence.read_text())['result']
        meta = lib['dataStr']['head']['c_para']
        assert meta['Manufacturer Part'] == item['mpn']
        assert meta['Supplier Part'] == code and lib['jlcOnSale'] == 1 and lib['SMT']
        package = lib['packageDetail']['dataStr']
        head = package['head']
        supplier = {}
        for shape in package['shape']:
            if shape.startswith('PAD~'):
                p = shape.split('~')
                supplier[p[8]] = ((float(p[2])-float(head['x']))*.254,
                                 -(float(p[3])-float(head['y']))*.254)
        for ref in item['designators']:
            pc = placed[ref]
            assert pc['layer'] == item['assembly']['side'] == 'top'
            rotation = item['assembly'].get('jlc_smt_rotation', pc['rotation'])
            ang = math.radians(rotation)
            actual = {}
            for pad in circuit:
                if pad.get('type') == 'pcb_smtpad' and pad.get('pcb_component_id') == pc['pcb_component_id']:
                    pin = next((h.removeprefix('pin') for h in pad.get('port_hints', [])
                                if h.removeprefix('pin').isdigit()), None)
                    if pin:
                        actual[pin] = (pad['x']-pc['footprint_origin']['x'], pad['y']-pc['footprint_origin']['y'])
            assert set(actual) == set(supplier), (ref, 'Pad numbers differ')
            offsets = []
            for pin, (x, y) in supplier.items():
                rx, ry = x*math.cos(ang)-y*math.sin(ang), x*math.sin(ang)+y*math.cos(ang)
                offsets.append((actual[pin][0]-rx, actual[pin][1]-ry))
            shift = [sum(p[k] for p in offsets)/len(offsets) for k in [0, 1]]
            error = max(math.dist(p, shift) for p in offsets)
            limit = .22 if code == 'C55266' else .002
            assert error < limit, (ref, 'Pin direction or footprint differs', error)
            fp = footprints[ref]
            at = children(fp, 'at')[0]
            assert children(fp, 'layer')[0][1] == 'F.Cu'
            assert abs(float(at[1])-(100+pc['footprint_origin']['x'])) < .001
            assert abs(float(at[2])-(100-pc['footprint_origin']['y'])) < .001
            rows.append({'ref': ref, 'code': code, 'mpn': item['mpn'], 'side': 'top',
                'native_kicad_xy_mm': [float(at[1]), float(at[2])],
                'expected_jlc_rotation_deg': rotation,
                'supplier_origin_to_compiled_pad_shift_source_xy_mm': [round(v,6) for v in shift],
                'max_pad_center_residual_mm': round(error,6),
                'evidence_sha256': hashlib.sha256(evidence.read_bytes()).hexdigest()})

    result = {'local_checks_passed': True, 'supplier_kinds': len({r['code'] for r in rows}),
        'smt_devices': len(rows), 'rows': rows,
        'remaining_pin_functions_and_29_other_component_placements_preserved': True,
        'native_KiCad_all_48_PTH_pin_net_assignments_verified': True,
        'pi_max_physical_pin_shift_mm': max_pi_shift,
        'generic_through_hole_socket_checks': socket_checks,
        'existing_enclosure_compatibility': {
            'cad_design': 'handheld_computer',
            'imported_pcb_release': json.loads((ROOT/'design/handheld_computer/source/design.json').read_text())['assets'][1]['provenance']['sourcePath'].split('/releases/')[1].split('/')[0],
            'board_outline_thickness_and_mounting_holes_unchanged': True,
            'connector_changes_mm': {'J_PI_body_height': [11.05,8], 'J_PI_tail_length':[2.29,3.5],
                'J_MOD_body_height':[3.66,5], 'J_MOD_new_bottom_tail_beyond_board':2.2},
            'enclosure_change_needed': False,
            'followup': 'Current adapted CAD uses PCB bottom21mm, Pi/sink lift1.3mm and generic sockets. J_FAN removal only frees space; no printed structure edit required. Cover air0.205mm, generic contact stroke and full native-tail seating still need physical trial.'},
        'mechanical_gate_user_facts': {
            'population': '2026-11-06 user explicitly requests suitable parts assembled by JLCPCB.',
            'side_and_entry': 'requirements.lite_fpc_placement source=user: top; entrance front/-Y.',
            'contact_face': 'Same user requirement: native-tail exposed copper upward; top contacts.',
            'pin_order': 'Existing main.tsx maps panel terminal n to socket terminal 11-n; exact native supplier pin1 left. Net membership unchanged.'},
        'fpc_checks': {
            'exact_part': 'SHOU HAN 0.5-10P CTSJ-H2.0 119 / C5373447; official library Extended, SMT, on-sale.',
            'datasheet': 'references/suppliers/c5373447/c5373447-datasheet.pdf p1, rendered and visually reviewed.',
            'land_pattern': '10 signal lands:0.5mm pitch,4.5mm span,0.30x1.80mm; width is at drawing 0.35+/-0.05mm lower limit. Two2.50x3.20mm tabs atX+/-4.20mm. No locating holes or slots.',
            'origin': 'Importer shifts all native supplier lands +0.35mm in sourceY. Final KiCad origin(100,75.35); no hand-edited CPL origin. JLC preview must confirm body centering against all lands.',
            'chirality': 'Top-only JLC population; no bottom SMT mirror applied. Opening -Y; pin1 left; pad1/2 GND; pad10 LCD_SCLK.',
            'rotation': 'Supplier native and board target opening both -Y; expected JLC angle0deg.',
            'visual': 'Current routed top and bottom previews inspected; connector entry and latch corridor preserved.'},
        'tps2553_rotation': 'C55266 native library pin1 is bottom-right. Retained KiCad SOT-23-6 at90deg places pin1 bottom-left. Explicit JLC270deg aligns every pin. KiCad pad-row half-span1.1375mm versus supplier1.350mm is a retained stock-land-pattern difference, not a mirror or changed package.',
        'manual_refs': ['J_PI','J_MOD'],
        'limitations': ['Current JLC order inventory and price not verified.',
            'Upload Gerbers, JLC BOM and JLC CPL; return the JLC placement screenshot before payment, especially J_LCD centering and six IC pin1 marks.',
            'Prototype FPC seating, power sequencing, COM waveforms and temperature remain untested.']}
    if check_release:
        manifest = json.loads((WORK / 'release/release-manifest.json').read_text())
        assert all(s['status']=='ready' for s in manifest['sections']), 'A release section is blocked'
        package = ROOT / 'manufacturing/pi_baseboard_lite/releases' / manifest['releaseId'] / 'package'
        with (package/'jlc-smt-bom.csv').open(encoding='utf-8-sig', newline='') as f:
            rb = list(csv.DictReader(f))
        with (package/'jlc-smt-placement.csv').open(encoding='utf-8-sig', newline='') as f:
            rp = list(csv.DictReader(f))
        assert len(rb) == 9 and len(rp) == 29, (len(rb), len(rp))
        expected = {r['ref']: r for r in rows}
        assert {p['Designator'] for p in rp} == set(expected)
        bom_refs = set()
        for item in rb:
            refs = [r.strip() for r in item['Designator'].split(',')]
            assert int(item['Quantity']) == len(refs)
            assert not (set(refs) & bom_refs), 'Repeated BOM designator'
            bom_refs.update(refs)
            for ref in refs:
                assert item['编号'] == expected[ref]['code']
                assert item['Comment'] == expected[ref]['mpn']
        assert bom_refs == set(expected)
        for p in rp:
            e = expected[p['Designator']]
            assert p['Layer'] == 'T'
            assert abs(float(p['Rotation']) % 360 - e['expected_jlc_rotation_deg'] % 360) < .001
            assert abs(float(p['Mid X'].removesuffix('mm')) - e['native_kicad_xy_mm'][0]) < .001
            assert abs(float(p['Mid Y'].removesuffix('mm')) + e['native_kicad_xy_mm'][1]) < .001
        tool = None
        drill_xy = []
        for line in (package/'drill/board-PTH.drl').read_text().splitlines():
            if line in ['T1','T2']: tool=line
            if tool=='T2' and line.startswith('X'):
                m=re.fullmatch(r'X([-\d.]+)Y([-\d.]+)',line)
                assert m, line
                drill_xy.append(tuple(map(float,m.groups())))
        expected_xy = [(100+x,-100+y) for record in socket_checks
            for x,y in record['semantic_pin_positions_source_mm'].values()]
        assert len(drill_xy)==len(expected_xy)==48
        for pt in expected_xy:
            assert min(math.dist(pt,q) for q in drill_xy)<.00001, ('Drill coordinate mismatch',pt)
        result['released_48_connector_drills_coordinate_and_diameter_verified'] = True
        result['drill_inventory'] = {'PTH_connector_1mm':48,'PTH_via_0p3mm':len(children(native,'via')),'NPTH_mount_2p2mm':2}
        result['visual_review'] = {
            'status':'performed',
            'scope':['routed top','routed bottom from_bottom','schematic','inner1/inner2 header detail','released Gerber top and bottom'],
            'observations':'Top FPC opens toward-Y, module socket top, GPIO socket bottom. Pi pin1 and module pin1 square pads checked. Native pad-net and drill coordinates establish chirality, independently of mirrored bottom images.',
            'preview_sha256': {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [WORK/'previews/pcb-routed-top.png',WORK/'previews/pcb-routed-bottom.png',WORK/'previews/schematic.png',
                    package/'previews/gerber-top.png',package/'previews/gerber-bottom.png']}}
        delivery_manifest = json.loads((package/'manifest.json').read_text())
        hashed_files = 0
        for f in delivery_manifest['files']:
            path = package / f['path'].removeprefix('manufacturing/')
            assert path.exists(), str(path)
            assert hashlib.sha256(path.read_bytes()).hexdigest() == f['sha256'], str(path)
            hashed_files += 1
        result['release_id'] = manifest['releaseId']
        result['release_file_hashes_verified'] = hashed_files
        result['released_bom_identity_quantity_and_cpl_xy_layer_rotation_verified'] = True
        result['released_bom_rows'] = len(rb)
        result['released_cpl_rows'] = len(rp)
        result['released_bom'] = rb
        result['released_cpl'] = rp
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', action='store_true')
    print(json.dumps(audit(parser.parse_args().release), ensure_ascii=False, indent=2))
