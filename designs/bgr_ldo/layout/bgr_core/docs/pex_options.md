# Magic VLSI PEX (Parasitic Extraction) Command & Options Reference

This document serves as the authoritative reference for Magic VLSI Parasitic Extraction (PEX) commands, suboptions, parameter meanings, and exact configuration choices for the TinyTapeout BGR & LDO Analog Shuttle project.

---

## 1. Overview & Extraction Workflow

In Magic VLSI, parasitic extraction follows a two-stage pipeline:
1. **Geometric Extraction (`extract`)**: Scans layout geometry, identifies nodes, transistors, resistors, capacitors, and writes intermediate `.ext` files.
2. **Post-Processing & Conversion (`ext2spice` / `extresist`)**: Converts `.ext` files into SPICE netlists with extracted parasitic resistance ($R$) and capacitance ($C$).

### Standard Execution Routine (in Magic Tcl)
```tcl
# Stage 1: Configure & run geometric extraction
extract style sky130(full)
extract do resistance
extract do coupling
cthresh 0.01
rthresh 10
extract all

# Stage 2: Convert to SPICE netlist
ext2spice lvs
ext2spice cthresh 0.01
ext2spice rthresh 10
ext2spice extresist on
ext2spice -o bgr_mos_pex.spice
```

---

## 2. Command & Suboption Reference

### 2.1 `extract style`
* **What it does**: Selects the technology extraction style file section defined in the Sky130A `.tech` file (`sky130A.tech`). Each style specifies capacitive capacitance models, fringe capacitances, sidewall factors, and layer thicknesses.
* **Meaning of values**:
  * `sky130(full)`: Extracts all parasitic ground capacitances, sidewall capacitances, and overlap capacitances across all metal and diffusion layers.
  * `sky130(fast)`: Simplified/approximate capacitance extraction for fast preliminary checks.
* **Project Choice & Rationale**:
  * **Selected**: `extract style sky130(full)`
  * **Why**: Analog BGR & LDO design requires exact parasitic capacitance values to predict loop bandwidth, phase margin, startup time, and PSRR without underestimating interconnect parasitics.
  * **Source**: Sky130 PDK Tech File (`sky130A.tech`), Magic VLSI Command Reference (`extract style`).

---

### 2.2 `extract do | no coupling`
* **What it does**: Enables (`do`) or disables (`no`) inter-wire coupling capacitance extraction between adjacent parallel signal traces on the same layer or adjacent metal layers.
* **Meaning of values**:
  * `do coupling`: Calculates inter-node coupling capacitance $C_{ij}$ between distinct electrical nodes $i$ and $j$.
  * `no coupling`: Lump all parasitic capacitances to ground ($C_{gnd}$).
* **Project Choice & Rationale**:
  * **1차 PEX (BGR 코어 단독 검증)**: `extract no coupling`
    * **Why**: Focuses on node-to-ground load capacitance and net series resistance without noise coupling from unplaced top/LDO lines.
  * **2차 PEX (Top 조립 및 최종 PEX)**: `extract do coupling`
    * **Why**: Mandatory for sensitive nodes (`VREF_LOW`, `IB_EA`, EA inputs) to detect crosstalk from RO (Ring Oscillator) and switching pass gates.
  * **Source**: Magic User's Guide (Section 9: Extracting Circuit Parasitics).

---

### 2.3 `extract do | no resistance`
* **What it does**: Enables (`do`) or disables (`no`) extraction of lumped or distributed parasitic resistance along metal interconnects and diffusion strips.
* **Meaning of values**:
  * `do resistance`: Generates resistor networks along interconnect paths.
  * `no resistance`: Treats all conductive traces on the same node as ideal zero-resistance short circuits.
* **Project Choice & Rationale**:
  * **Selected**: `extract do resistance`
  * **Why**: Essential for evaluating trim ladder routing IR drops ($n\_b0 \sim n\_b3$), power rail drops (`VAPWR`, `VGND`), and poly resistor head contact drops.
  * **Source**: Magic Command Reference (`extract`).

---

### 2.4 `cthresh <threshold_fF>`
* **What it does**: Sets the minimum parasitic capacitance threshold (in femtofarads `fF`). Capacitances below this threshold are omitted from the extracted netlist to prevent netlist bloating.
* **Meaning of values**:
  * `0.01` ($0.01\,\text{fF} = 10\,\text{aF}$): Retains ultra-small parasitic capacitances.
  * `1.0` ($1.0\,\text{fF}$): Ignores small parasitic capacitances below $1\,\text{fF}$.
* **Project Choice & Rationale**:
  * **Selected**: `cthresh 0.01` ($10\,\text{aF}$)
  * **Why**: High-impedance internal nodes in BGR ($V_{mid1}$, $V_{gate\_top}$) are sensitive to sub-femtofarad parasitics that alter high-frequency pole/zero locations.
  * **Source**: Magic Open Tooling Documentation (`cthresh`).

---

### 2.5 `rthresh <threshold_ohms>`
* **What it does**: Sets the minimum parasitic resistance threshold (in Ohms $\Omega$). Parasitic resistors below this value are merged or omitted.
* **Meaning of values**:
  * `10` ($10\,\Omega$): Filters out negligible parasitic resistances below $10\,\Omega$.
  * `0` ($0\,\Omega$): Retains all parasitic resistances regardless of value.
* **Project Choice & Rationale**:
  * **Selected**: `rthresh 10`
  * **Why**: Keeps netlist size manageable while capturing trim path resistances (which range from $7.8\,\Omega$ to $19.7\,\Omega$).
  * **Source**: Magic Command Reference (`rthresh`).

---

### 2.6 `extresist`
* **What it does**: Runs the detailed resistance extractor on `.ext` files, calculating 2D mesh resistance trees for wide metal geometries and multi-finger nodes.
* **Suboptions**:
  * `extresist on`: Enables hierarchical resistance calculation.
  * `extresist skip`: Skips resistance tree calculation.
  * `extresist geometry`: Uses geometric mesh solver for non-rectangular interconnect corners.
* **Project Choice & Rationale**:
  * **Selected**: `ext2spice extresist on`
  * **Why**: Ensures multi-branch power rails (`VAPWR`, `VGND`) and trim ladder paths are accurately represented as resistor networks.
  * **Source**: Magic Maintainer's Manual (`extresist`).

---

### 2.7 `ext2sim`
* **What it does**: Converts `.ext` layout files into `.sim` simulation format (legacy format used by IRSIM and precursor tools).
* **Suboptions**:
  * `ext2sim labels`: Preserves layout labels as node names.
  * `ext2sim alias`: Generates alias names for shorted nets.
* **Project Choice & Rationale**:
  * **Selected**: Not used (bypassed in favor of `ext2spice` for direct SPICE/ngspice simulation).
  * **Source**: Magic Command Reference (`ext2sim`).

---

### 2.8 `ext2spice`
* **What it does**: Converts `.ext` files into SPICE netlist format (`.spice`).
* **Suboptions**:
  * `ext2spice lvs`: Configures extraction format for LVS comparison (hides parasitic R/C, matches schematic subcircuits).
  * `ext2spice cthresh <val>`: Applies capacitance cutoff to netlist output.
  * `ext2spice rthresh <val>`: Applies resistance cutoff to netlist output.
  * `ext2spice default`: Resets options to default settings.
  * `ext2spice scale on|off`: Enables/disables metric scaling (`.option scale=1u`).
  * `ext2spice subcircuit on|off`: Wraps extracted circuit in `.subckt` block.
  * `ext2spice format ngspice|hspice`: Generates simulator-specific syntax.
* **Project Choice & Rationale**:
  * **For LVS**: `ext2spice lvs` + `ext2spice -o bgr_mos.spice`
  * **For PEX**: `ext2spice cthresh 0.01` + `ext2spice rthresh 10` + `ext2spice extresist on` + `ext2spice -o bgr_mos_pex.spice`
  * **Why**: Strictly separates clean LVS netlists from parasitic-rich PEX netlists to guarantee zero false mismatches during LVS while retaining parasitic fidelity during ngspice simulation.
  * **Source**: Magic Tcl Command Reference (`ext2spice`).
