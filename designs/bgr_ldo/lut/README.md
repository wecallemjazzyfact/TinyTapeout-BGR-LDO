# gm/Id Lookup Table (LUT) Infrastructure

This directory contains the common transistor characterization data and lookup utilities for $g_m/I_D$-based sizing. This asset is shared by all sub-blocks (`bgr/`, `ldo/`, and `top/`).

## 1. Directory Structure

* **`pygmid/`**: Local copy of the `pygmid` package, making the tool self-contained and path-independent.
* **`gen/`**: Contains the configs and scripts to generate the lookup tables:
  * `sample_config_nfet.cfg` / `sample_config_pfet.cfg` (Reference config files)
  * `run_sweep.py` (The ngspice 4D characterization sweep script)
  * `verify_gmid.py` (Script to verify lookup accuracy against anchors)
* **`data/`**: Directory where the generated 4D lookup tables (`.pkl` format) are saved:
  * `nfet_g5v0d10v5.pkl` (NFET table)
  * `pfet_g5v0d10v5.pkl` (PFET table)
* **`lookup.py`**: Common Python wrapper providing `lookup` and `lookupVGS` functions.

---

## 2. Characterization Specifications

* **Technology Model**: SkyWater Sky130A (`tt` corner)
* **Transistor Type**: 5V/10.5V Thick-Oxide devices:
  * NMOS: `sky130_fd_pr__nfet_g5v0d10v5`
  * PMOS: `sky130_fd_pr__pfet_g5v0d10v5`
* **Transistor Dimensions**: $W = 10\,\mu\text{m}$, $N_{fing} = 1$.
* **Sweep Grid Axes**:
  * **$L$ (6 points)**: `[0.5, 1.0, 2.0, 4.0, 8.0, 20.0]` $\mu\text{m}$
  * **$V_{SB}$ (4 points)**: `[0.0, 0.4, 0.8, 1.2]` V
  * **$V_{DS}$ (7 points)**: `[0.1, 0.3, 0.6, 1.0, 1.65, 2.5, 3.3]` V
  * **$V_{GS}$ (133 points)**: `0.0` to `3.3` V (25 mV steps)
* **Saved Variables**: `ID`, `VT` (Threshold Voltage), `GM`, `GDS`, `CGG`, `CGS`, `CGD`, `CGB`, `VDSAT`

---

## 3. Verification Anchors (tt corner, 27°C)

To verify the generated lookup table, compare the lookup results against these known physical anchors from the simulated circuit:

* **NFET $V_{th}$ at $L = 4.0\,\mu\text{m}$, $V_{DS} = 0.25\,\text{V}$**:
  * **$V_{SB} = 0.0\,\text{V}$**: $V_{th} \approx 0.647\,\text{V}$
  * **$V_{SB} = 0.78\,\text{V}$** (Body Effect): $V_{th} \approx 1.068\,\text{V}$
* **PFET $V_{th}$ at $L = 0.5\,\mu\text{m}$, $V_{DS} = 1.5\,\text{V}$**:
  * **$V_{SB} = 0.0\,\text{V}$**: $V_{th} \approx 0.871\,\text{V}$

---

## 4. Usage Example in Python

To perform lookups, add the `lut/` directory to your python path and use the common wrapper:

```python
import os
import sys

# Add lut directory to python path
sys.path.insert(0, '/foss/designs/designs/bgr_ldo/lut')

import lookup

# Example 1: Look up gm/Id and Id for a given VGS
gm = lookup.lookup('nfet', 'GM', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.0)
id_val = lookup.lookup('nfet', 'ID', L=4e-6, VGS=1.0, VDS=0.25, VSB=0.0)
gmid = gm / id_val
print(f"gm/Id ratio: {gmid:.2f} V^-1")

# Example 2: Look up VGS for a target gm/Id ratio
vgs_needed = lookup.lookupVGS('nfet', GM_ID=10.0, L=4e-6, VDS=0.25, VSB=0.0)
print(f"Required VGS for gm/Id=10: {vgs_needed:.3f} V")
```
