"""Read supplier models and land patterns; produce comparison evidence only.

Does not edit PCB/CAD source, manufacturing outputs, or build caches.
Run from project root: python3 design/pi_baseboard_lite/inspect-fpc-candidates.py
"""
import hashlib
import json
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "replicator-fpc-mpl"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(tempfile.gettempdir()) / "replicator-fpc-fontcache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from build123d import import_step

REFS = Path("product/references/fpc-candidates")
OUT = Path("design/pi_baseboard_lite")
CODES = ["C588226", "C5373447", "C262583"]
# Supplier drawing and silhouette inspection: AFC07's native entrance is +Y;
# rotate its whole footprint 180 degrees to preserve the existing -Y entrance.
ROTATIONS = {"C5139870": 0, "C588226": 0, "C5373447": 0, "C262583": 180}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def package(code):
    return json.loads((REFS / f"{code}-easyeda.json").read_text())["result"]

def pads(code):
    data = package(code)["packageDetail"]["dataStr"]
    ox, oy = data["head"]["x"], data["head"]["y"]
    sign = -1 if ROTATIONS[code] == 180 else 1
    result = []
    for item in data["shape"]:
        if not item.startswith("PAD~"):
            continue
        fields = item.split("~")
        result.append({
            "pin": fields[8],
            "x_mm": round(sign * (float(fields[2]) - ox) * .254, 6),
            "y_mm": round(-sign * (float(fields[3]) - oy) * .254, 6),
            "width_mm": round(float(fields[4]) * .254, 6),
            "height_mm": round(float(fields[5]) * .254, 6),
        })
    return result

facts = {"schema_version": 1, "scope": "Read-only candidate model and footprint comparison", "frame": "PCB source XY after target -Y opening rotation; millimetres", "baseline": {"code": "C5139870", "pads": pads("C5139870")}, "candidates": []}
fig = plt.figure(figsize=(15, 9), facecolor="#fafafa")
for index, code in enumerate(CODES):
    p = REFS / f"{code}-easyeda.step"
    shape = import_step(p)
    bbox = shape.bounding_box()
    eda = package(code)
    model_node = next(json.loads(s.split("~", 1)[1])["attrs"] for s in eda["packageDetail"]["dataStr"]["shape"] if s.startswith("SVGNODE~"))
    candidate_pads = pads(code)
    signal = {int(p["pin"]): p for p in candidate_pads if p["pin"].isdigit() and 1 <= int(p["pin"]) <= 10}
    assert set(signal) == set(range(1, 11)), f"{code}: incomplete 10-pin signal row"
    assert signal[1]["x_mm"] < signal[10]["x_mm"], f"{code}: target opening pin order reversed"
    assert all(abs((signal[n+1]["x_mm"] - signal[n]["x_mm"]) - .5) < .001 for n in range(1, 10)), f"{code}: pitch mismatch"
    assert shape.is_valid, f"{code}: invalid STEP"
    entry = {"code": code, "mpn": eda["title"], "model_uuid": model_node["uuid"], "model_title": model_node["title"], "source": "JLCEDA/EasyEDA Official Library", "api_url": f"https://easyeda.com/api/products/{code}/components", "model_url": "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/" + model_node["uuid"], "step_sha256": digest(p), "library_response_sha256": digest(REFS / f"{code}-easyeda.json"), "raw_step_bbox_mm": {"min": list(bbox.min), "max": list(bbox.max), "size": list(bbox.size)}, "valid": shape.is_valid, "solid_count": len(shape.solids()), "face_count": len(shape.faces()), "pcb_rotation_for_target_opening_deg": ROTATIONS[code], "pads": candidate_pads, "signal_pitch_pass": True, "target_pin1_left_pass": True, "drop_in_footprint": False}
    facts["candidates"].append(entry)
    ax = fig.add_subplot(2, 3, index+1, projection="3d")
    vertices, triangles = shape.tessellate(.035, .12)
    vertices = np.array([list(v) for v in vertices]); triangles = np.array(triangles)
    center = (np.array(list(bbox.min)) + np.array(list(bbox.max))) / 2
    verts = vertices-center
    polys = verts[triangles]
    collection = Poly3DCollection(polys, facecolors="#d7cbb6", edgecolors="#77736c", linewidth=.04, shade=True, lightsource=matplotlib.colors.LightSource(azdeg=315, altdeg=40))
    ax.add_collection3d(collection)
    extent = np.array(list(bbox.size)) / 2
    ax.set_xlim(-extent[0]-.3, extent[0]+.3); ax.set_ylim(-extent[1]-.3, extent[1]+.3); ax.set_zlim(-extent[2]-.2, extent[2]+.2)
    ax.set_box_aspect(np.array(list(bbox.size)) + .4)
    ax.view_init(elev=28, azim=-65)
    ax.set_axis_off()
    ax.set_title(f"{code}\n{eda['title']}\nSTEP {bbox.size.X:.2f} x {bbox.size.Y:.2f} x {bbox.size.Z:.3f} mm", fontsize=11, pad=0)
    ax2 = fig.add_subplot(2, 3, index+4)
    for pp in facts["baseline"]["pads"]:
        ax2.add_patch(Rectangle((pp["x_mm"]-pp["width_mm"]/2, pp["y_mm"]-pp["height_mm"]/2), pp["width_mm"], pp["height_mm"], facecolor="none", edgecolor="#b8b8b8", linewidth=1, linestyle="--"))
    for pp in candidate_pads:
        ax2.add_patch(Rectangle((pp["x_mm"]-pp["width_mm"]/2, pp["y_mm"]-pp["height_mm"]/2), pp["width_mm"], pp["height_mm"], facecolor="#66aeca", edgecolor="#14607a", alpha=.7))
        if pp["pin"] in ("1", "10", "11", "12"):
            ax2.text(pp["x_mm"], pp["y_mm"], pp["pin"], ha="center", va="center", fontsize=9, color="#15232d")
    ax2.annotate("FPC entrance -Y", xy=(0,-5), xytext=(0,-3.8), ha="center", arrowprops={"arrowstyle":"->", "color":"#15232d"}, fontsize=10)
    ax2.set_xlim(-6.5,6.5); ax2.set_ylim(-5.7,3.2); ax2.set_aspect("equal"); ax2.grid(alpha=.2)
    ax2.set_xlabel("X (mm)"); ax2.set_ylabel("Y (mm)")
    ax2.set_title("Blue: candidate pads | dashed: existing FH12A\nSame footprint origin; native AFC07 rotated 180 deg", fontsize=10)
fig.suptitle("Downloaded FPC connector models and footprint comparison", fontsize=16, y=.98)
fig.text(.5,.015,"Source: JLCEDA/EasyEDA Official Library | https://lceda.cn/ | https://easyeda.com/\nClosed model geometry only; these candidates require a new footprint, rerouting, and assembled clearance review.", ha="center", fontsize=10)
fig.subplots_adjust(top=.87,bottom=.10,hspace=.23,wspace=.19)
fig.savefig(OUT / "fpc-candidate-models.png", dpi=180)
(OUT / "fpc-candidate-geometry.json").write_text(json.dumps(facts, indent=2, ensure_ascii=False)+"\n")
print(json.dumps({"candidates": [{k:v for k,v in row.items() if k not in ("pads",)} for row in facts["candidates"]], "evidence": "fpc-candidate-geometry.json", "image": "fpc-candidate-models.png"}, ensure_ascii=False))
