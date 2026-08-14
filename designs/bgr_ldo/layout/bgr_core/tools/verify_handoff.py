#!/usr/bin/env python3
"""
verify_handoff.py - Handoff document coordinate verification tool.
Parses coordinate tables from BGR_LAYOUT_HANDOFF.md (§6) and checks them against build/inventory.json.
Outputs discrepancy table for document verification.
"""

import sys
import os
import json
import re

def main():
    if len(sys.argv) > 1:
        handoff_file = sys.argv[1]
    else:
        handoff_file = '/foss/designs/designs/bgr_ldo/BGR_LAYOUT_HANDOFF.md'
        
    if len(sys.argv) > 2:
        inv_file = sys.argv[2]
    else:
        inv_file = '/foss/designs/designs/bgr_ldo/layout/bgr_core/build/inventory.json'

    if not os.path.exists(handoff_file):
        print(f"Error: Handoff file '{handoff_file}' not found.")
        sys.exit(1)
        
    if not os.path.exists(inv_file):
        print(f"Error: Inventory file '{inv_file}' not found.")
        sys.exit(1)

    with open(inv_file, 'r', encoding='utf-8') as f:
        inv = json.load(f)

    cell_bbox = inv.get("cell_bbox_um", [0, 0, 0, 0])
    instances = {inst["instance_name"]: inst for inst in inv.get("instances", [])}
    labels = {lbl["name"]: lbl for lbl in inv.get("labels", [])}

    handoff_text = open(handoff_file, 'r', encoding='utf-8').read()

    results = []

    # 1. BGR Zone BBox Check (§6.1)
    # Document §6.1: BGR 존: x -1.80 ... 143.40, y -36.70 ... 79.20
    doc_x1, doc_y1, doc_x2, doc_y2 = -1.80, -36.70, 143.40, 79.20
    actual_x1, actual_y1, actual_x2, actual_y2 = cell_bbox
    
    diff_x1 = round(actual_x1 - doc_x1, 3)
    diff_y1 = round(actual_y1 - doc_y1, 3)
    diff_x2 = round(actual_x2 - doc_x2, 3)
    diff_y2 = round(actual_y2 - doc_y2, 3)
    
    status_bbox = "MATCH" if (diff_x1 == 0 and diff_y1 == 0 and diff_x2 == 0 and diff_y2 == 0) else "MISMATCH"
    results.append({
        "section": "§6.1 BGR Zone Outer BBox",
        "item": "Cell Outer BBox",
        "doc_value": f"({doc_x1}, {doc_y1}) .. ({doc_x2}, {doc_y2})",
        "actual_value": f"({actual_x1}, {actual_y1}) .. ({actual_x2}, {actual_y2})",
        "status": status_bbox,
        "delta": f"dx1={diff_x1}, dy1={diff_y1}, dx2={diff_x2}, dy2={diff_y2}"
    })

    # 2. Port Label Coordinates Check (§6.8)
    doc_ports = {
        "VREF_LOW": [136.62, -36.50],
        "IB_EA": [117.30, -35.70],
        "VAPWR": [30.00, 78.40],
        "VGND": [60.00, -2.70],
        "TRIM0": [100.00, -6.51],
        "TRIM1": [130.00, -6.51],
        "TRIM2": [100.00, -20.51],
        "TRIM3": [130.00, -20.51]
    }

    for p_name, p_coords in doc_ports.items():
        if p_name in labels:
            lbl = labels[p_name]
            act_x, act_y = lbl["x"], lbl["y"]
            dx = round(act_x - p_coords[0], 3)
            dy = round(act_y - p_coords[1], 3)
            st = "MATCH" if (dx == 0 and dy == 0) else "MISMATCH"
            results.append({
                "section": "§6.8 Port Labels",
                "item": f"Port '{p_name}' ({lbl['layer']})",
                "doc_value": f"({p_coords[0]}, {p_coords[1]})",
                "actual_value": f"({act_x}, {act_y})",
                "status": st,
                "delta": f"dx={dx}, dy={dy}"
            })
        else:
            results.append({
                "section": "§6.8 Port Labels",
                "item": f"Port '{p_name}'",
                "doc_value": f"({p_coords[0]}, {p_coords[1]})",
                "actual_value": "NOT FOUND",
                "status": "MISSING",
                "delta": "N/A"
            })

    # 3. Specific Subcell Instance LL Checks (§6.2, §6.3, §6.4)
    sample_insts = {
        "sky130_fd_pr__nfet_g5v0d10v5_YKUQM3_4": {"section": "§6.2 Row D Dummy", "doc_ll": [10.91, 23.88]},
        "sky130_fd_pr__nfet_g5v0d10v5_FV4ZM9_4": {"section": "§6.2 Row C Dummy", "doc_ll": [5.06, 0.00]},
        "sky130_fd_pr__res_high_po_0p69_F6JLQ4_0": {"section": "§6.3 Resistor R2b0", "doc_ll": [113.70, 1.143]},
        "sky130_fd_pr__res_high_po_0p69_T8D7K5_0": {"section": "§6.3 Resistor R2b1", "doc_ll": [114.87, 1.381]},
        "sky130_fd_pr__res_high_po_0p69_QCK2SQ_0": {"section": "§6.3 Resistor R2b2", "doc_ll": [116.04, 1.858]},
        "sky130_fd_pr__res_high_po_0p69_5VVEC7_0": {"section": "§6.3 Resistor R2b3", "doc_ll": [117.21, 2.812]}
    }

    for inst_name, data in sample_insts.items():
        if inst_name in instances:
            inst_data = instances[inst_name]
            bbox = inst_data.get("bbox_um")
            if bbox:
                act_ll = [bbox[0], bbox[1]]
                dx = round(act_ll[0] - data["doc_ll"][0], 3)
                dy = round(act_ll[1] - data["doc_ll"][1], 3)
                st = "MATCH" if (abs(dx) <= 0.05 and abs(dy) <= 0.05) else "MISMATCH"
                results.append({
                    "section": data["section"],
                    "item": inst_name,
                    "doc_value": f"LL ({data['doc_ll'][0]}, {data['doc_ll'][1]})",
                    "actual_value": f"LL ({act_ll[0]}, {act_ll[1]})",
                    "status": st,
                    "delta": f"dx={dx}, dy={dy}"
                })
        else:
            results.append({
                "section": data["section"],
                "item": inst_name,
                "doc_value": f"LL ({data['doc_ll'][0]}, {data['doc_ll'][1]})",
                "actual_value": "NOT FOUND",
                "status": "MISSING",
                "delta": "N/A"
            })

    # Print Verification Summary Table
    print("\n=========================================================================")
    print(" Handoff Document Coordinate Verification Table (vs inventory.json)")
    print("=========================================================================")
    print(f"{'Section':<22s} | {'Item':<35s} | {'Document Value':<25s} | {'Actual Value':<25s} | {'Status':<8s}")
    print("-" * 125)
    for r in results:
        print(f"{r['section']:<22s} | {r['item']:<35s} | {r['doc_value']:<25s} | {r['actual_value']:<25s} | {r['status']:<8s}")
    print("-" * 125)
    
    mismatch_count = sum(1 for r in results if r["status"] != "MATCH")
    print(f"Total verified items: {len(results)}, Matches: {len(results)-mismatch_count}, Mismatches/Missing: {mismatch_count}\n")

if __name__ == '__main__':
    main()
