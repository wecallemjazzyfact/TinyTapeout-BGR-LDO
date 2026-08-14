#!/usr/bin/env python3
"""
mag_inventory.py - Magic .mag layout file inventory extractor.
Parses a Magic .mag file and extracts instances, rects, labels, and cell bounding box to JSON.
"""

import sys
import os
import json
import re

def parse_subcell_bbox(sub_path):
    """Returns internal unit (min_x, min_y, max_x, max_y) of a subcell mag file."""
    if not os.path.exists(sub_path):
        return None
    lay = None
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    has_rect = False
    for line in open(sub_path, errors='ignore'):
        line = line.strip()
        if line.startswith('<< ') and line.endswith(' >>'):
            lay = line[3:-3]
        elif line.startswith('rect '):
            parts = line.split()
            if len(parts) >= 5 and lay and not ('error' in lay or lay == 'labels'):
                x1, y1, x2, y2 = [int(p) for p in parts[1:5]]
                min_x = min(min_x, x1, x2)
                min_y = min(min_y, y1, y2)
                max_x = max(max_x, x1, x2)
                max_y = max(max_y, y1, y2)
                has_rect = True
    if has_rect:
        return (min_x, min_y, max_x, max_y)
    return None

def transform_bbox(transform, sub_bbox):
    """
    Magic transform matrix: a b c d e f
    x' = a*x + b*y + c
    y' = d*x + e*y + f
    """
    if not sub_bbox:
        return None
    a, b, c, d_t, e, f = transform
    x1, y1, x2, y2 = sub_bbox
    corners = [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
    t_corners = [(a*cx + b*cy + c, d_t*cx + e*cy + f) for cx, cy in corners]
    tx1 = min(pt[0] for pt in t_corners) / 200.0
    ty1 = min(pt[1] for pt in t_corners) / 200.0
    tx2 = max(pt[0] for pt in t_corners) / 200.0
    ty2 = max(pt[1] for pt in t_corners) / 200.0
    return [round(tx1, 4), round(ty1, 4), round(tx2, 4), round(ty2, 4)]

def parse_mag(mag_path, base_dir):
    lines = open(mag_path, errors='ignore').read().splitlines()
    
    instances = []
    layer_rects = []
    labels = []
    
    curr_lay = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('<< ') and line.endswith(' >>'):
            curr_lay = line[3:-3]
            i += 1
            continue
            
        if line.startswith('rect '):
            parts = line.split()
            if len(parts) >= 5 and curr_lay and curr_lay != 'labels':
                x1, y1, x2, y2 = [int(p)/200.0 for p in parts[1:5]]
                layer_rects.append({
                    "layer": curr_lay,
                    "x1": round(min(x1, x2), 4),
                    "y1": round(min(y1, y2), 4),
                    "x2": round(max(x1, x2), 4),
                    "y2": round(max(y1, y2), 4)
                })
            i += 1
            continue
            
        if any(line.startswith(k) for k in ('rlabel', 'flabel', 'label')):
            parts = line.split()
            # rlabel <layer> x1 y1 x2 y2 <orient> <text>
            if len(parts) >= 8:
                lay = parts[1]
                lx1, ly1, lx2, ly2 = [int(p)/200.0 for p in parts[2:6]]
                name = parts[7]
                cx = (lx1 + lx2) / 2.0
                cy = (ly1 + ly2) / 2.0
                
                is_port = False
                port_num = None
                # Check next line for port
                if i + 1 < len(lines) and lines[i+1].strip().startswith('port '):
                    p_parts = lines[i+1].strip().split()
                    is_port = True
                    port_num = int(p_parts[1]) if len(p_parts) > 1 and p_parts[1].isdigit() else None
                
                labels.append({
                    "name": name,
                    "layer": lay,
                    "x": round(cx, 4),
                    "y": round(cy, 4),
                    "x1": round(min(lx1, lx2), 4),
                    "y1": round(min(ly1, ly2), 4),
                    "x2": round(max(lx1, lx2), 4),
                    "y2": round(max(ly1, ly2), 4),
                    "is_port": is_port,
                    "port_num": port_num
                })
            i += 1
            continue
            
        if line.startswith('use '):
            parts = line.split()
            cell_name = parts[1]
            inst_name = parts[2]
            
            transform = None
            raw_box = None
            j = i + 1
            while j < len(lines) and j < i + 5:
                sub_l = lines[j].strip()
                if sub_l.startswith('transform '):
                    transform = [int(x) for x in sub_l.split()[1:]]
                elif sub_l.startswith('box '):
                    raw_box = [int(x)/200.0 for x in sub_l.split()[1:]]
                elif sub_l.startswith('use ') or (sub_l.startswith('<< ') and sub_l.endswith(' >>')):
                    break
                j += 1
            
            # Find subcell file
            sub_path = os.path.join(base_dir, cell_name + '.mag')
            if not os.path.exists(sub_path):
                sub_path = os.path.join('/foss/pdks/sky130A/libs.ref/sky130_fd_pr/mag', cell_name + '.mag')
            
            sub_raw_bbox = parse_subcell_bbox(sub_path)
            if transform and sub_raw_bbox:
                t_bbox = transform_bbox(transform, sub_raw_bbox)
            elif raw_box and len(raw_box) == 4:
                t_bbox = [round(min(raw_box[0], raw_box[2]), 4), round(min(raw_box[1], raw_box[3]), 4),
                          round(max(raw_box[0], raw_box[2]), 4), round(max(raw_box[1], raw_box[3]), 4)]
            else:
                t_bbox = None
                
            instances.append({
                "cell_name": cell_name,
                "instance_name": inst_name,
                "transform_raw": transform,
                "bbox_um": t_bbox
            })
            i = j
            continue
            
        i += 1

    # Overall bbox
    all_x = []
    all_y = []
    for r in layer_rects:
        all_x.extend([r["x1"], r["x2"]])
        all_y.extend([r["y1"], r["y2"]])
    for inst in instances:
        if inst["bbox_um"]:
            all_x.extend([inst["bbox_um"][0], inst["bbox_um"][2]])
            all_y.extend([inst["bbox_um"][1], inst["bbox_um"][3]])
    for lbl in labels:
        all_x.extend([lbl["x1"], lbl["x2"]])
        all_y.extend([lbl["y1"], lbl["y2"]])
        
    cell_bbox_um = [
        round(min(all_x), 4) if all_x else 0.0,
        round(min(all_y), 4) if all_y else 0.0,
        round(max(all_x), 4) if all_x else 0.0,
        round(max(all_y), 4) if all_y else 0.0
    ]

    return {
        "source_file": os.path.abspath(mag_path),
        "cell_bbox_um": cell_bbox_um,
        "instance_count": len(instances),
        "instances": instances,
        "rect_count": len(layer_rects),
        "layer_rects": layer_rects,
        "label_count": len(labels),
        "labels": labels
    }

def main():
    if len(sys.argv) > 1:
        mag_file = sys.argv[1]
    else:
        mag_file = '/foss/designs/designs/bgr_ldo/layout/bgr_core/bgr_mos.mag'
        
    if len(sys.argv) > 2:
        out_file = sys.argv[2]
    else:
        out_file = '/foss/designs/designs/bgr_ldo/layout/bgr_core/build/inventory.json'

    base_dir = os.path.dirname(os.path.abspath(mag_file))
    res = parse_mag(mag_file, base_dir)

    os.makedirs(os.path.dirname(os.path.abspath(out_file)), exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)

    print(f"[mag_inventory] Saved inventory for '{mag_file}' to '{out_file}'")
    print(f"  Cell BBox (µm): {res['cell_bbox_um']}")
    print(f"  Instances: {res['instance_count']}, Layer Rects: {res['rect_count']}, Labels: {res['label_count']}")

if __name__ == '__main__':
    main()
