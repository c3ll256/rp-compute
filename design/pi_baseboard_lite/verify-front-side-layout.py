"""Read compiled PCB evidence against side, pin-map and edge-spacing intent.

Run only after pcb.run(check); this reads its outputs and writes a design review,
never the board, routing cache or manufacturing release.
"""
import json
import hashlib
import re
from pathlib import Path
from shapely.geometry import Polygon, box

ROOT = Path.cwd()
DESIGN = ROOT / "design/pi_baseboard_lite"
rows = json.loads((ROOT / ".work/pcb/pi_baseboard_lite/build/circuit.json").read_text())
source_components = {r["source_component_id"]: r for r in rows if r["type"] == "source_component"}
components = {source_components[r["source_component_id"]]["name"]: r for r in rows if r["type"] == "pcb_component"}
source_ports = {r["source_port_id"]: r for r in rows if r["type"] == "source_port"}
pcb_ports = {r["pcb_port_id"]: r for r in rows if r["type"] == "pcb_port"}
net_by_connectivity = {r["subcircuit_connectivity_map_key"]: r["name"] for r in rows if r["type"] == "source_net"}
board = next(r for r in rows if r["type"] == "pcb_board")
outline = Polygon([(p["x"], p["y"]) for p in board["outline"]])
bottom = sorted(n for n, c in components.items() if c["layer"] == "bottom")
assert bottom == ["J_PI"], bottom

def envelope(c):
    x, y = c["center"]["x"], c["center"]["y"]
    return box(x-c["width"]/2, y-c["height"]/2, x+c["width"]/2, y+c["height"]/2)

fpc_id = components["J_LCD"]["pcb_component_id"]
fpc_pads = {}
for pad in rows:
    if pad["type"] != "pcb_smtpad" or pad.get("pcb_component_id") != fpc_id:
        continue
    port = pcb_ports.get(pad.get("pcb_port_id"))
    if not port:
        continue
    sp = source_ports[port["source_port_id"]]
    number = sp.get("pin_number")
    if number and 1 <= int(number) <= 10:
        fpc_pads[int(number)] = {"signal": sp["name"], "net": net_by_connectivity.get(sp.get("subcircuit_connectivity_map_key")), "xy_mm": [pad["x"], pad["y"]]}
assert set(fpc_pads) == set(range(1, 11)), fpc_pads
external_pin_review = json.loads((DESIGN / "fpc-physical-pin-review.json").read_text())
for row in external_pin_review["rows"]:
    actual = fpc_pads[row["socket_terminal"]]
    assert actual["signal"] == row["signal"], (row, actual)
    assert actual["net"] == row["expected_net"], (row, actual)
assert fpc_pads[1]["xy_mm"][0] < fpc_pads[10]["xy_mm"][0]
assert all(abs(fpc_pads[n+1]["xy_mm"][0]-fpc_pads[n]["xy_mm"][0]-.5)<.001 for n in range(1, 10))

buffer_gaps = {name: round(envelope(components[name]).distance(envelope(components["J_LCD"])), 6) for name in ("U_BUF1", "U_BUF2")}
assert min(buffer_gaps.values()) >= 3, buffer_gaps
decoupling = {}
for name, cap_name in (("U_BUF1", "C_BUF1"), ("U_BUF2", "C_BUF2")):
    vcc = next(port for port in pcb_ports.values() if port["pcb_component_id"] == components[name]["pcb_component_id"] and source_ports[port["source_port_id"]]["name"] == "VCC")
    cap = components[cap_name]
    distance = ((vcc["x"]-cap["center"]["x"])**2+(vcc["y"]-cap["center"]["y"])**2)**.5
    assert distance <= 3, (name, distance)
    decoupling[name] = {"VCC_xy_mm": [vcc["x"], vcc["y"]], "capacitor": cap_name, "capacitor_center_distance_mm": round(distance, 6)}

edge_clearance = {}
for name, component in components.items():
    if name.startswith("J_"):
        continue
    shape = envelope(component)
    assert outline.covers(shape), name
    edge_clearance[name] = round(shape.distance(outline.boundary), 6)
assert min(edge_clearance.values()) >= 2, edge_clearance

# Source-owned component exclusion: do not turn a cable-service region into a
# copper keepout; tracks and flush vias below the cable remain permissible.
layout_source = (DESIGN / "source/layout.ts").read_text()
corridor_source = re.search(r"export const fpcInsertionClearance = \{(.*?)\};", layout_source, re.S).group(1)
coords = {name: float(re.search(rf"{name}:\s*([-\d.]+)", corridor_source).group(1)) for name in ("minX", "maxX", "minY", "maxY")}
corridor = box(coords["minX"], coords["minY"], coords["maxX"], coords["maxY"])
service_gaps = {name: round(envelope(c).distance(corridor), 6) for name, c in components.items() if c["layer"] == "top" and name != "J_LCD"}
assert min(service_gaps.values()) >= .5, service_gaps
pi_pads = []
for pad in rows:
    if pad["type"] != "pcb_plated_hole" or pad.get("pcb_component_id") != components["J_PI"]["pcb_component_id"]:
        continue
    x, y = pad["x"], pad["y"]
    if pad["shape"] == "circle":
        from shapely.geometry import Point
        shape = Point(x, y).buffer(pad["outer_diameter"]/2, resolution=128)
    else:
        # ESQ square land: rotation does not change this square envelope.
        shape = box(x-pad["rect_pad_width"]/2, y-pad["rect_pad_height"]/2, x+pad["rect_pad_width"]/2, y+pad["rect_pad_height"]/2)
    pi_pads.append(shape)
pi_cap_gap = min(envelope(components["C_LCD_IN"]).distance(p) for p in pi_pads)
assert pi_cap_gap >= 2, pi_cap_gap

report = {
    "schema_version": 1, "status": "passed_compiled_side_pin_map_and_land_envelope_checks",
    "frame": "Compiled PCB source XY, millimetres; native supplier top footprints, side transforms applied",
    "area_mm2": round(outline.area, 6), "previous_area_mm2": 2284.54,
    "area_increase_percent": round((outline.area/2284.54-1)*100, 3),
    "outline_envelope_mm": [board["width"], board["height"]],
    "top_component_count": len(components)-len(bottom), "bottom_components": bottom,
    "fpc_supplier_code": "C5373447", "fpc_pin_map": fpc_pads,
    "screen_terminal_formula": "socket terminal = 11 - panel terminal",
    "buffer_land_envelope_to_fpc_mm": buffer_gaps, "decoupling": decoupling,
    "ordinary_land_envelope_edge_clearance_mm": edge_clearance,
    "minimum_ordinary_land_envelope_edge_clearance_mm": min(edge_clearance.values()),
    "fpc_insertion_service_corridor": {"source": "default", "bounds_mm": coords, "width_mm": coords["maxX"]-coords["minX"], "top_land_envelope_gaps_mm": service_gaps, "minimum_gap_mm": min(service_gaps.values()), "limits": "Component exclusion only; actual cable seating, folding and finger access require prototype checks."},
    "C_LCD_IN_land_envelope_to_nearest_Pi_copper_land_mm": round(pi_cap_gap, 6),
    "model_sha256": hashlib.sha256((DESIGN / "source/models/C5373447-easyeda.step").read_bytes()).hexdigest(),
    "model_origin_evidence": {"supplier_head_relative_Y_mm": -1.2800076, "loader_pad_center_recenter_Y_mm": .35, "net_model_Y_offset_mm": -.9300076, "raw_min_Z_mm": -1, "model_Z_offset_mm": 1},
    "limits": ["Land-envelope distances are not body or courtyard distances.", "Native tail length, actual seating/retention and slider operation require prototype checks.", "Assembly collision and thermal air clearance are reviewed separately against the exported STEP."]
}
(DESIGN / "front-side-layout-review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
print(json.dumps({k: report[k] for k in ("status", "area_mm2", "area_increase_percent", "top_component_count", "bottom_components", "buffer_land_envelope_to_fpc_mm", "minimum_ordinary_land_envelope_edge_clearance_mm")}, ensure_ascii=False))
