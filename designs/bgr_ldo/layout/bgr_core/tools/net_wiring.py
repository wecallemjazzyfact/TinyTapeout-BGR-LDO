#!/usr/bin/env python3
"""
net_wiring.py - Net wiring inventory generator.
Reads build/inventory.json + bgr_mos.spice to analyze metal wiring, areas, via counts,
and detect multi-layer label overlap warnings ("명명 단락" hazards).
"""

import sys
import os
import json
import re
from collections import defaultdict

def rect_area(r):
    return (r["x2"] - r["x1"]) * (r["y2"] - r["y1"])

def point_in_rect(x, y, r, tol=0.01):
    return (r["x1"] - tol <= x <= r["x2"] + tol) and (r["y1"] - tol <= y <= r["y2"] + tol)

def rect_intersects(r1, r2, tol=0.001):
    return not (r1["x2"] < r2["x1"] - tol or r1["x1"] > r2["x2"] + tol or
                r1["y2"] < r2["y1"] - tol or r1["y1"] > r2["y2"] + tol)

def main():
    if len(sys.argv) > 1:
        inv_file = sys.argv[1]
    else:
        inv_file = '/foss/designs/designs/bgr_ldo/layout/bgr_core/build/inventory.json'
        
    if len(sys.argv) > 2:
        spice_file = sys.argv[2]
    else:
        spice_file = '/foss/designs/designs/bgr_ldo/layout/bgr_core/bgr_mos.spice'
        
    if len(sys.argv) > 3:
        out_json = sys.argv[3]
    else:
        out_json = '/foss/designs/designs/bgr_ldo/layout/bgr_core/build/net_wiring.json'
        
    out_md = os.path.splitext(out_json)[0] + '.md'

    if not os.path.exists(inv_file):
        print(f"Error: Inventory file '{inv_file}' not found.")
        sys.exit(1)
        
    with open(inv_file, 'r', encoding='utf-8') as f:
        inv = json.load(f)

    labels = inv.get("labels", [])
    layer_rects = inv.get("layer_rects", [])

    # Group labels by net name
    net_labels = defaultdict(list)
    for lbl in labels:
        net_labels[lbl["name"]].append(lbl)

    # Detect multi-layer label overlap warnings (명명 단락 경고)
    warnings = []
    for lbl in labels:
        lx, ly = lbl["x"], lbl["y"]
        overlapping_layers = set()
        for r in layer_rects:
            if point_in_rect(lx, ly, r):
                overlapping_layers.add(r["layer"])
        if len(overlapping_layers) > 1:
            warnings.append({
                "label_name": lbl["name"],
                "layer": lbl["layer"],
                "coords": [lx, ly],
                "overlapping_layers": sorted(list(overlapping_layers)),
                "message": f"WARNING: Label '{lbl['name']}' at ({lx}, {ly}) overlaps multiple layers: {sorted(list(overlapping_layers))}"
            })

    # For each net with labels, find connected rects per layer
    net_inventory = {}
    
    for net_name, lbl_list in net_labels.items():
        # Find all rects connected to any label of this net
        connected_rects = []
        for r in layer_rects:
            # Match if rect overlaps label point or is in layer rects of net
            for lbl in lbl_list:
                if point_in_rect(lbl["x"], lbl["y"], r):
                    connected_rects.append(r)
                    break
        
        # Expand connected rects (flood fill overlap within cell)
        added = True
        current_set = list(connected_rects)
        visited_indices = set(layer_rects.index(r) for r in current_set if r in layer_rects)
        
        while added:
            added = False
            new_rects = []
            for idx, r in enumerate(layer_rects):
                if idx in visited_indices:
                    continue
                # Check if r intersects any rect in current_set
                for cr in current_set:
                    if rect_intersects(r, cr):
                        visited_indices.add(idx)
                        new_rects.append(r)
                        added = True
                        break
            current_set.extend(new_rects)

        # Aggregate area per metal layer & via counts
        metal_areas = defaultdict(float)
        via_counts = defaultdict(int)
        all_x = []
        all_y = []

        for r in current_set:
            lay = r["layer"]
            area = rect_area(r)
            if 'metal' in lay or lay in ('metal1', 'metal2', 'metal3', 'metal4', 'locali'):
                metal_areas[lay] += area
            elif 'via' in lay or 'cont' in lay:
                via_counts[lay] += 1
            all_x.extend([r["x1"], r["x2"]])
            all_y.extend([r["y1"], r["y2"]])

        for lbl in lbl_list:
            all_x.extend([lbl["x1"], lbl["x2"]])
            all_y.extend([lbl["y1"], lbl["y2"]])

        bbox = [
            round(min(all_x), 4) if all_x else 0.0,
            round(min(all_y), 4) if all_y else 0.0,
            round(max(all_x), 4) if all_x else 0.0,
            round(max(all_y), 4) if all_y else 0.0
        ]

        net_inventory[net_name] = {
            "labels": [{"layer": l["layer"], "coords": [l["x"], l["y"]], "is_port": l["is_port"]} for l in lbl_list],
            "label_count": len(lbl_list),
            "metal_areas_um2": {k: round(v, 4) for k, v in metal_areas.items()},
            "via_counts": dict(via_counts),
            "total_rects": len(current_set),
            "bbox_um": bbox
        }

    output_data = {
        "warnings": warnings,
        "net_count": len(net_inventory),
        "nets": net_inventory
    }

    os.makedirs(os.path.dirname(os.path.abspath(out_json)), exist_ok=True)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    # Generate Markdown Report
    md_lines = [
        "# Net Wiring Inventory Report (`net_wiring.md`)",
        "",
        f"**Source Inventory**: `{inv_file}`  ",
        f"**SPICE Netlist**: `{spice_file}`  ",
        f"**Total Labeled Nets**: {len(net_inventory)}  ",
        f"**Warnings Count**: {len(warnings)}  ",
        ""
    ]

    if warnings:
        md_lines.extend([
            "## ⚠️ Naming Short Hazards (Multi-Layer Label Overlap Warnings)",
            "",
            "The following labels overlap with 2 or more routing layers at their placement coordinates:",
            ""
        ])
        for w in warnings:
            md_lines.append(f"- **`{w['label_name']}`** on layer `{w['layer']}` at `({w['coords'][0]}, {w['coords'][1]})` -> Overlaps layers: `{', '.join(w['overlapping_layers'])}`")
        md_lines.append("")

    md_lines.extend([
        "## 📊 Labeled Nets Summary Table",
        "",
        "| Net Name | Labels (Layer @ Coords) | met1 Area (µm²) | met2 Area (µm²) | met3 Area (µm²) | Vias | BBox (µm) |",
        "| :--- | :--- | ---: | ---: | ---: | :--- | :--- |"
    ])

    for net_name, info in sorted(net_inventory.items()):
        lbl_str = ", ".join([f"{l['layer']}@({l['coords'][0]},{l['coords'][1]})" for l in info["labels"]])
        m1_area = info["metal_areas_um2"].get("metal1", 0.0)
        m2_area = info["metal_areas_um2"].get("metal2", 0.0)
        m3_area = info["metal_areas_um2"].get("metal3", 0.0)
        via_str = ", ".join([f"{k}:{v}" for k, v in info["via_counts"].items()]) if info["via_counts"] else "-"
        bbox_str = f"({info['bbox_um'][0]},{info['bbox_um'][1]})..({info['bbox_um'][2]},{info['bbox_um'][3]})"
        
        md_lines.append(f"| **`{net_name}`** | {lbl_str} | {m1_area:.2f} | {m2_area:.2f} | {m3_area:.2f} | {via_str} | `{bbox_str}` |")

    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"[net_wiring] Saved JSON to '{out_json}' and MD to '{out_md}'")
    print(f"  Processed {len(net_inventory)} nets, found {len(warnings)} label overlap warnings.")

if __name__ == '__main__':
    main()
