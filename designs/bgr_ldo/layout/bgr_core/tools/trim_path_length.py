#!/usr/bin/env python3
"""
trim_path_length.py - Trim ladder branch length & residual resistance calculator.
Calculates met1/met2 length, width breakdown, square count (L/W), via count,
and resistance under Sky130A Typical and HRHC process corners for trim branches P1-P6.
Also computes switch residual resistances (R_short).
Outputs build/trim_branches.md.
"""

import sys
import os

# Process corner definitions
CORNERS = {
    "typical": {
        "name": "Sky130A Typical",
        "metal1": 0.125, # Ω/sq
        "metal2": 0.125, # Ω/sq
        "via1": 4.500    # Ω/cut
    },
    "hrhc": {
        "name": "HRHC Corner",
        "metal1": 0.145, # Ω/sq
        "metal2": 0.145, # Ω/sq
        "via1": 15.000   # Ω/cut
    }
}

# Fixed schematic simulated switch On-resistance
RON_SCHEMATIC = 4.573 # Ω

# Geometric route definitions for branches P1 to P6 (coordinates in µm)
TRIM_BRANCH_GEOMETRY = {
    "P1": {
        "net": "n_b0",
        "desc": "n_b0 resistor side (met1 bar 110.30–114.34) -> b0.D comb",
        "segments": [
            {"layer": "metal1", "length": 4.04, "width": 0.40},
            {"layer": "metal2", "length": 9.00, "width": 0.40},
            {"layer": "metal2", "length": 27.85, "width": 0.40},
            {"layer": "metal2", "length": 15.37, "width": 0.40},
            {"layer": "metal1", "length": 2.11, "width": 0.40}
        ],
        "via1_count": 2
    },
    "P2": {
        "net": "n_b1",
        "desc": "n_b1 resistor side (met1 L bridge x113.90–114.55) -> b0.S comb (= b1.D)",
        "segments": [
            {"layer": "metal1", "length": 0.76, "width": 0.26},
            {"layer": "metal2", "length": 24.54, "width": 0.40}
        ],
        "via1_count": 1
    },
    "P3": {
        "net": "n_b2",
        "desc": "n_b2 resistor side (met1 bar 114.98–116.64) -> b1.S comb",
        "segments": [
            {"layer": "metal1", "length": 0.26, "width": 0.26},
            {"layer": "metal2", "length": 28.48, "width": 0.40}
        ],
        "via1_count": 1
    },
    "P4": {
        "net": "n_b2",
        "desc": "n_b2 resistor side -> b2.D comb (bottom bypass: vert 115.60-116.00 -> y-25 horiz -> vert 114.86-115.16 -> y-33.1 horiz x99.90-115.16 -> via1 x100.00)",
        "segments": [
            {"layer": "metal1", "length": 0.26, "width": 0.26},
            {"layer": "metal2", "length": 28.88, "width": 0.40},
            {"layer": "metal2", "length": 0.94, "width": 0.40},
            {"layer": "metal2", "length": 8.10, "width": 0.30},
            {"layer": "metal2", "length": 15.26, "width": 0.40},
            {"layer": "metal1", "length": 0.40, "width": 0.40}
        ],
        "via1_count": 2
    },
    "P5": {
        "net": "n_b3",
        "desc": "n_b3 resistor side -> b2.S comb (= b3.D)",
        "segments": [
            {"layer": "metal1", "length": 0.26, "width": 0.26},
            {"layer": "metal2", "length": 2.20, "width": 0.40},
            {"layer": "metal2", "length": 45.42, "width": 0.30}
        ],
        "via1_count": 1
    },
    "P6": {
        "net": "b3.S",
        "desc": "b3.S comb -> VGND (x143.00-143.40 vert -> p-tap)",
        "segments": [
            {"layer": "metal2", "length": 28.90, "width": 0.40},
            {"layer": "metal1", "length": 0.40, "width": 0.40}
        ],
        "via1_count": 1
    }
}

# Switch residual resistance formula mapping
SWITCHES = {
    "b0": {"head": "P1", "tail": "P2"},
    "b1": {"head": "P2", "tail": "P3"},
    "b2": {"head": "P4", "tail": "P5"},
    "b3": {"head": "P5", "tail": "P6"}
}

def main():
    if len(sys.argv) > 1:
        out_md = sys.argv[1]
    else:
        # Default output path relative to repository structure
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_md = os.path.abspath(os.path.join(script_dir, "..", "build", "trim_branches.md"))

    branch_results = {}

    for branch_id, geom in TRIM_BRANCH_GEOMETRY.items():
        m1_len, m1_sq = 0.0, 0.0
        m2_len, m2_sq = 0.0, 0.0
        seg_details = []

        for seg in geom["segments"]:
            lay = seg["layer"]
            length = seg["length"]
            width = seg["width"]
            sq = length / width if width > 0 else 0.0

            if lay == "metal1":
                m1_len += length
                m1_sq += sq
            elif lay == "metal2":
                m2_len += length
                m2_sq += sq

            seg_details.append({
                "layer": lay,
                "length_um": length,
                "width_um": width,
                "sq": round(sq, 2)
            })

        via1_count = geom["via1_count"]

        # Calculate resistance for each process corner
        r_typ = (m1_sq * CORNERS["typical"]["metal1"]) + (m2_sq * CORNERS["typical"]["metal2"]) + (via1_count * CORNERS["typical"]["via1"])
        r_hrhc = (m1_sq * CORNERS["hrhc"]["metal1"]) + (m2_sq * CORNERS["hrhc"]["metal2"]) + (via1_count * CORNERS["hrhc"]["via1"])

        branch_results[branch_id] = {
            "net": geom["net"],
            "desc": geom["desc"],
            "total_m1_len": round(m1_len, 2),
            "total_m1_sq": round(m1_sq, 2),
            "total_m2_len": round(m2_len, 2),
            "total_m2_sq": round(m2_sq, 2),
            "total_len": round(m1_len + m2_len, 2),
            "total_sq": round(m1_sq + m2_sq, 2),
            "via1_count": via1_count,
            "r_typ": r_typ,
            "r_hrhc": r_hrhc,
            "segments": seg_details
        }

    # Generate Markdown Report
    md_lines = [
        "# Trim Ladder Branch & Residual Resistance Report (`trim_branches.md`)",
        "",
        "**Target Branches**: `P1` ~ `P6`  ",
        "**Source Coordinates**: Handoff §6.7 & `bgr_mos.mag` verified layout measurements  ",
        "**Process Corner Parameters**:",
        "  - **Sky130A Typical**: metal1/metal2 = 125 mΩ/□ ($0.125\\,\\Omega/\\text{sq}$), via1 (m2c) = 4,500 mΩ/cut ($4.5\\,\\Omega/\\text{cut}$)",
        "  - **HRHC Corner**: metal1/metal2 = 145 mΩ/□ ($0.145\\,\\Omega/\\text{sq}$), via1 (m2c) = 15,000 mΩ/cut ($15.0\\,\\Omega/\\text{cut}$)",
        "",
        "## 📊 1. Trim Branch Geometry & Resistance Breakdown (P1–P6)",
        "",
        "| Branch | Net | Route Description | Total Len (µm) | met1 Len (µm) | met2 Len (µm) | met1 (sq) | met2 (sq) | Total (sq) | Via1 Cuts | R_typ (Ω) | R_hrhc (Ω) |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    ]

    for b_id in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        res = branch_results[b_id]
        md_lines.append(
            f"| **`{b_id}`** | `{res['net']}` | {res['desc']} | {res['total_len']:.2f} | {res['total_m1_len']:.2f} | {res['total_m2_len']:.2f} | {res['total_m1_sq']:.2f} | {res['total_m2_sq']:.2f} | {res['total_sq']:.2f} | {res['via1_count']} | **{res['r_typ']:.2f} Ω** | **{res['r_hrhc']:.2f} Ω** |"
        )

    md_lines.extend([
        "",
        "## 🔌 2. Switch Residual Resistance Table (`R_short`)",
        "",
        f"> **Condition Note**: $R_{{on}} = {RON_SCHEMATIC:.3f}\\,\\Omega$ is the fixed schematic simulated value (corner variation not applied).  ",
        "",
        "| Switch | Formula | P_head (Ω, Typ) | Ron (Ω) | P_tail (Ω, Typ) | **R_short (Typical)** | **R_short (HRHC)** |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: |"
    ])

    for sw_name in ["b0", "b1", "b2", "b3"]:
        sw = SWITCHES[sw_name]
        head_res = branch_results[sw["head"]]
        tail_res = branch_results[sw["tail"]]

        r_short_typ = head_res["r_typ"] + RON_SCHEMATIC + tail_res["r_typ"]
        r_short_hrhc = head_res["r_hrhc"] + RON_SCHEMATIC + tail_res["r_hrhc"]

        md_lines.append(
            f"| **`{sw_name}`** | `{sw['head']} + Ron + {sw['tail']}` | {head_res['r_typ']:.2f} | {RON_SCHEMATIC:.3f} | {tail_res['r_typ']:.2f} | **{r_short_typ:.2f} Ω** | **{r_short_hrhc:.2f} Ω** |"
        )

    md_lines.extend([
        "",
        "## 🔍 3. Branch Detailed Segment Breakdown",
        ""
    ])

    for b_id in ["P1", "P2", "P3", "P4", "P5", "P6"]:
        res = branch_results[b_id]
        md_lines.extend([
            f"### Branch `{b_id}` ({res['net']})",
            f"* **Description**: {res['desc']}",
            f"* **Via1 Cuts**: {res['via1_count']}",
            f"* **Typical Resistance**: {res['r_typ']:.2f} Ω | **HRHC Resistance**: {res['r_hrhc']:.2f} Ω",
            "* **Segment Decomposition**:"
        ])
        for idx, seg in enumerate(res["segments"], 1):
            md_lines.append(f"  {idx}. **{seg['layer']}**: Length = {seg['length_um']} µm, Width = {seg['width_um']} µm -> **{seg['sq']} sq**")
        md_lines.append("")

    os.makedirs(os.path.dirname(os.path.abspath(out_md)), exist_ok=True)
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines) + "\n")

    print(f"[trim_path_length] Successfully updated report: '{out_md}'")
    for b_id, res in branch_results.items():
        print(f"  {b_id} ({res['net']:5s}): Len={res['total_len']:.2f}um | met1={res['total_m1_sq']:.2f}sq | met2={res['total_m2_sq']:.2f}sq | Via1={res['via1_count']} | R_typ={res['r_typ']:.2f} Ohm | R_hrhc={res['r_hrhc']:.2f} Ohm")

if __name__ == '__main__':
    main()


