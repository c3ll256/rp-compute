"""Extract already-built Workbench STEP components as PCB source assets.

This performs serialization/frame conversion only. The modeled geometry is
owned by connector_fit_references, not reconstructed by this script.
"""
import hashlib
import json
import re
from pathlib import Path

from build123d import Location, export_step, import_step

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / 'manufacturing/connector_fit_references/releases/export-4f50cb2b848cda1db5be17eba8e0044a'
receipt = json.loads((RELEASE / 'receipt.json').read_text())
step = next(a for a in receipt['artifacts'] if a['role'] == 'model/step')
assert hashlib.sha256((ROOT / step['path']).read_bytes()).hexdigest() == step['sha256']
assembly = import_step(ROOT / step['path'])
children = {child.label: child for child in assembly.children}
source = ROOT / 'design/pi_baseboard_lite/source'
library = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Connector_PinSocket_2.54mm.pretty')
records = []
for obj, display_x, count, height, tail in [
    ('generic_40pin', 80, '20', 8, 3.5),
    ('generic_8pin', 100, '04', 5, 3),
]:
    shape = children[obj].moved(Location((-display_x, 0, 0)))
    shape.parent = None
    bb = shape.bounding_box()
    assert abs(bb.min.Z + tail) < .001 and abs(bb.max.Z - height) < .001
    model = source / 'models' / (obj + '-nominal.step')
    export_step(shape, model)
    original = library / ('PinSocket_2x' + count + '_P2.54mm_Vertical.kicad_mod')
    raw = original.read_text()
    text, replaced = re.subn(r'\n\t\(model [\s\S]*?\n\t\)\n', '\n', raw)
    assert replaced == 1, 'Only the unrelated stock model reference should be removed'
    # Rebase the complete published land pattern from pin1 to pad-grid center.
    # This is one uniform coordinate-frame translation, not regenerated pads.
    # The backend matches KiCad placement origins to component centers when it
    # backports routed copper; a corner-origin part otherwise fails calibration.
    dx, dy = 1.27, -(int(count)-1)*2.54/2
    number = r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'
    pattern = r'\((at|start|mid|end|center|xy)\s+('+number+r')\s+('+number+r')(?=[\s)])'
    def rebase(match):
        return '('+match[1]+' '+format(float(match[2])+dx,'.9g')+' '+format(float(match[3])+dy,'.9g')
    text = re.sub(pattern, rebase, text)
    name = 'KiCad_PinSocket_2x' + count + '_P2.54mm_GenericH' + str(height)
    footprint = source / 'footprints' / (name + '.kicad_mod')
    footprint.write_text(text)
    records.append({
        'object_id': obj, 'cad_revision': receipt['revision'], 'cad_export_id': receipt['exportId'],
        'cad_source_step_sha256': step['sha256'], 'source_step': step['path'],
        'removed_display_translation_mm': [display_x, 0, 0],
        'native_2d_origin_translation_mm': [dx, dy],
        'model_origin_position_mm': [-1.27, -(int(count)-1)*2.54/2, 0],
        'model_path': model.relative_to(ROOT).as_posix(),
        'model_sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
        'footprint': 'vendor:' + name,
        'footprint_source_url': 'https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Connector_PinSocket_2.54mm.pretty/' + original.name,
        'upstream_footprint_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
        'project_footprint_sha256': hashlib.sha256(footprint.read_bytes()).hexdigest(),
        'license': 'KiCad library GPL-3.0 with library exception; nominal model is project-generated reference',
        'modification': 'Remove the stock3D model stanza; rebase all published2D geometry uniformly from pin1 to pad-grid center. Copper/hole sizes, pairwise positions, numbering, silk and courtyard geometry remain unchanged.',
        'qualification': 'Nominal specification reference, not manufacturer-certified internal contact or mating geometry.',
    })
(source / 'models/generic-socket-provenance.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(records, ensure_ascii=False, indent=2))
