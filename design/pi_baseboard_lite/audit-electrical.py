"""Read-only cross-check of compiled connectivity, KiCad pads and native ERC.

Run from the project root after pcb.run(check) and the native KiCad ERC.
This audits evidence; it never patches generated boards/schematics or waives ERC.
"""
import collections
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / ".work/pcb/pi_baseboard_lite"
RELEASE = ROOT / "manufacturing/pi_baseboard_lite/releases/cd04f943ef57c8363e042d7d455cd9599f11065206ac235a43715b5c526e2ad6/package/circuit.json"
BASELINE_COMMIT = "25c91b6378c3f4c38c63fa9622700a91152c878b"


def read_json(path):
    return json.loads(path.read_text())


def connectivity(data):
    components = {r["source_component_id"]: r["name"] for r in data if r["type"] == "source_component"}
    ports = {r["source_port_id"]: r for r in data if r["type"] == "source_port"}
    names = {r["source_net_id"]: r["name"] for r in data if r["type"] == "source_net"}
    pin_nets = collections.defaultdict(set)
    for row in data:
        if row["type"] != "source_trace":
            continue
        for port_id in row.get("connected_source_port_ids", []):
            port = ports[port_id]
            key = (components[port["source_component_id"]], str(port["pin_number"]))
            pin_nets[key].update(names[n] for n in row.get("connected_source_net_ids", []))
    pins = {(components[p["source_component_id"]], str(p["pin_number"])): p for p in ports.values()}
    return components, pins, {k: sorted(v) for k, v in pin_nets.items()}


def parse_sexpr(text):
    tokens = iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text))

    def node(token):
        if token != "(":
            return json.loads(token) if token.startswith('"') else token
        result = []
        for token in tokens:
            if token == ")":
                return result
            result.append(node(token))
        raise ValueError("Unclosed KiCad expression")

    return node(next(tokens))


def children(node, tag):
    return [v for v in node if isinstance(v, list) and v and v[0] == tag]


def audit():
    data = read_json(WORK / "build/circuit.json")
    components, pins, pin_nets = connectivity(data)
    # Releases may be pruned by the owning tool. Git retains the original
    # reviewed baseline; never restore or alter manufacturing outputs by hand.
    if RELEASE.exists():
        baseline = read_json(RELEASE)
    else:
        object_name = BASELINE_COMMIT + ":" + RELEASE.relative_to(ROOT).as_posix()
        baseline = json.loads(subprocess.run(
            ["git", "show", object_name], cwd=ROOT,
            check=True, capture_output=True, text=True,
        ).stdout)
    _, _, previous = connectivity(baseline)
    failures = []
    if previous != pin_nets:
        failures.append("Compiled pin-to-net membership changed from the released circuit")

    def geometry(elements):
        names = {r["source_component_id"]: r["name"] for r in elements if r["type"] == "source_component"}
        placements = {names[r["source_component_id"]]: {
            key: r.get(key) for key in ["x", "y", "width", "height", "rotation", "layer"]
        } for r in elements if r["type"] == "pcb_component"}
        keys = ["width", "height", "thickness", "num_layers", "center", "outline", "x", "y", "hole_diameter"]
        mechanics = [{key: r[key] for key in keys if key in r}
                     for r in elements if r["type"] in ["pcb_board", "pcb_hole"]]
        return placements, mechanics

    geometry_preserved = geometry(baseline) == geometry(data)

    # TI DBV/PW terminal tables and the established connector assembly mapping.
    # These are independently stated expectations, not generated from main.tsx.
    expected = {
        "U_BUF1": ["GND", "GPIO11", "LCD_SCLK", "GND", "GPIO10", "LCD_SI", "GND", "LCD_SCS", "GPIO8", "GND", "LCD_DISP", "GPIO25", "GND", "V3V3_LCD"],
        "U_BUF2": ["GND", "GPIO12", "LCD_COM", "V3V3_LCD", "GND", None, "GND", None, "GND", "V3V3_LCD", None, "GND", "V3V3_LCD", "V3V3_LCD"],
        "U_LCD_LIMIT": ["V5_PI_IN", "GND", "GPIO24", "FAULT_N", "LCD_ILIM", "V5_LCD"],
        "U_AUX_LIMIT": ["V5_PI_IN", "GND", "V3V3_PI", "FAULT_N", "AUX_ILIM", "V5_AUX"],
        "U_LCD_LDO": ["V5_LCD", "GND", "V5_LCD", None, "V3V3_LCD"],
        "U_AUX_LDO": ["V5_AUX", "GND", "V5_AUX", None, "AUX_3V3"],
        "J_LCD": ["GND", "GND", "V5_LCD", "V5_LCD", "V5_LCD", "LCD_DISP", "LCD_COM", "LCD_SCS", "LCD_SI", "LCD_SCLK", None, None],
        "J_MOD": ["AUX_3V3", "GND", "GPIO2", "GPIO3", "GPIO10", "GPIO9", "GPIO11", "GPIO7"],
    }
    for ref, nets in expected.items():
        for number, net in enumerate(nets, 1):
            key = (ref, str(number))
            if pin_nets.get(key, []) != ([] if net is None else [net]):
                failures.append(f"Wrong net on {ref}.{number}: expected {net}")
            if net is None and not pins[key].get("do_not_connect"):
                failures.append(f"Missing deliberate NC declaration on {ref}.{number}")

    for ref in [r for r in expected if r.startswith("U_")]:
        ports = [p for (r, _), p in pins.items() if r == ref]
        if not any(p.get("requires_power") for p in ports):
            failures.append(f"Missing power metadata on {ref}")
        if not any(p.get("requires_ground") for p in ports):
            failures.append(f"Missing ground metadata on {ref}")

    board = parse_sexpr((WORK / "kicad/pi_baseboard_lite.kicad_pcb").read_text())
    checked_pads = 0
    seen = set()
    for footprint in children(board, "footprint"):
        refs = [p[2] for p in children(footprint, "property") if p[1] == "Reference"]
        if not refs:
            refs = [p[2] for p in children(footprint, "fp_text") if p[1] == "reference"]
        if not refs:
            failures.append("Native footprint has no reference")
            continue
        for pad in children(footprint, "pad"):
            key = (refs[0], pad[1])
            if key not in pins:  # NPTH mounts and extra, unconnected mechanical tabs.
                continue
            net_nodes = children(pad, "net")
            # KiCad 9 uses (net code name); KiCad 10 uses (net name).
            actual = [net_nodes[0][-1]] if net_nodes and len(net_nodes[0]) >= 2 else []
            if actual != pin_nets.get(key, []):
                failures.append(f"Native PCB pad net mismatch on {key}: {actual}")
            checked_pads += 1
            seen.add(key)
    if set(pins) != seen:
        failures.append(f"Missing native PCB pads: {sorted(set(pins) - seen)}")

    native_netlist_path = WORK / "reports/native-schematic-netlist.xml"
    if native_netlist_path.stat().st_mtime < (WORK / "kicad/pi_baseboard_lite.kicad_sch").stat().st_mtime:
        raise ValueError("Re-export the native schematic netlist after the latest build")
    native_netlist = ET.parse(native_netlist_path)
    native_groups = []
    for net in native_netlist.findall(".//nets/net"):
        group = {(n.get("ref"), n.get("pin")) for n in net.findall("node")}
        group &= set(pins)
        if group:
            native_groups.append((net.get("name"), group))
    expected_groups = collections.defaultdict(set)
    for pin, nets in pin_nets.items():
        for net in nets:
            expected_groups[net].add(pin)
    parity_failures = []
    for net, group in expected_groups.items():
        matches = [(name, actual) for name, actual in native_groups if actual & group]
        if len(matches) != 1 or matches[0][1] != group:
            parity_failures.append(net)
    for name, group in native_groups:
        if any(pins[p].get("do_not_connect") for p in group) and len(group) > 1:
            parity_failures.append(f"Connected deliberate NC: {name}")
    native_refs = {r.get("ref") for r in native_netlist.findall(".//components/comp")}
    if native_refs != set(components.values()):
        parity_failures.append("Native schematic component references differ from the compiled circuit")

    erc = read_json(WORK / "reports/electrical-repair-erc.json")
    violations = [v for sheet in erc.get("sheets", []) for v in sheet.get("violations", [])]
    errors = [v for v in violations if v["severity"] == "error"]
    classified = []
    for error in errors:
        for item in error.get("items", []):
            match = re.search(r"Symbol (\S+) Pin (\d+)", item["description"])
            key = (match[1], match[2]) if match else None
            port = pins.get(key)
            classified.append({
                "item": item["description"],
                "source_nets": pin_nets.get(key, []),
                "source_explicit_nc": bool(port and port.get("do_not_connect")),
            })
    drc = read_json(WORK / "reports/kicad-drc-diagnostics.json")["drcDigest"]
    raw = drc.get("rawReport", {})
    return {
        "build_id": read_json(WORK / "generated/current/state.json").get("buildId"),
        "source_and_native_pcb_failures": failures,
        "released_net_membership_preserved": previous == pin_nets,
        "mechanical_geometry_and_all_32_component_placements_preserved": geometry_preserved,
        "source_component_count": len(components),
        "source_net_count": len({n for nets in pin_nets.values() for n in nets}),
        "connected_terminal_count": len(pin_nets),
        "native_pcb_pads_checked": checked_pads,
        "explicit_nc_terminals": sum(bool(p.get("do_not_connect")) for p in pins.values()),
        "critical_terminal_expectations_checked": sum(map(len, expected.values())),
        "native_schematic_component_count": len(native_refs),
        "native_schematic_net_partitions_checked": len(expected_groups),
        "native_schematic_parity_failures": parity_failures,
        "raw_native_pcb_violations": dict(collections.Counter(f'{v["severity"]}:{v["type"]}' for v in raw.get("violations", []))),
        "raw_native_pcb_unconnected": len(raw.get("unconnected_items", [])),
        "native_schematic_violations": dict(collections.Counter(f'{v["severity"]}:{v["type"]}' for v in violations)),
        "native_schematic_nc_markers": len(re.findall(r"\(no_connect\b", (WORK / "kicad/pi_baseboard_lite.kicad_sch").read_text())),
        "native_schematic_error_details": classified,
        "native_schematic_error_count": len(errors),
        "limitation": "Digital checks do not verify physical soldering, dynamic waveforms, COM/boot/shutdown timing, heat rise or actual FPC fit. Native warning counts are preserved; only pcb.run(release) can publish fabrication deliverables.",
    }


if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
