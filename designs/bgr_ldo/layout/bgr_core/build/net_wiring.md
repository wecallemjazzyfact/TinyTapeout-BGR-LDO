# Net Wiring Inventory Report (`net_wiring.md`)

**Source Inventory**: `/foss/designs/designs/bgr_ldo/layout/bgr_core/build/inventory.json`  
**SPICE Netlist**: `/foss/designs/designs/bgr_ldo/layout/bgr_core/bgr_mos.spice`  
**Total Labeled Nets**: 38  
**Warnings Count**: 15  

## ⚠️ Naming Short Hazards (Multi-Layer Label Overlap Warnings)

The following labels overlap with 2 or more routing layers at their placement coordinates:

- **`VGND`** on layer `metal1` at `(-0.325, -2.2)` -> Overlaps layers: `locali, metal1`
- **`net3`** on layer `metal2` at `(20.0, 52.35)` -> Overlaps layers: `metal2, nwell`
- **`net6`** on layer `metal2` at `(8.0, 53.25)` -> Overlaps layers: `metal2, nwell`
- **`net2`** on layer `metal2` at `(3.0, 54.15)` -> Overlaps layers: `metal2, nwell`
- **`net_tap`** on layer `metal2` at `(31.5, 55.05)` -> Overlaps layers: `metal2, nwell`
- **`VREF_LOW`** on layer `metal2` at `(55.0, 38.0)` -> Overlaps layers: `metal2, metal3`
- **`IB_EA`** on layer `metal2` at `(55.0, 38.9)` -> Overlaps layers: `metal2, metal3`
- **`V_bias`** on layer `metal2` at `(55.0, 39.8)` -> Overlaps layers: `metal2, metal3, nwell`
- **`net7`** on layer `metal2` at `(130.0, 13.21)` -> Overlaps layers: `metal2, nwell`
- **`net8`** on layer `metal2` at `(130.0, 15.45)` -> Overlaps layers: `metal2, nwell`
- **`V_bias_n_uq0`** on layer `metal2` at `(127.5, -0.18)` -> Overlaps layers: `metal2, nwell`
- **`VAPWR`** on layer `viali` at `(30.0, 78.4)` -> Overlaps layers: `nwell, viali`
- **`VBE1`** on layer `metal3` at `(100.0, -2.1)` -> Overlaps layers: `locali, metal1, metal3, viali`
- **`VBE1_uq0`** on layer `metal2` at `(22.5, -1.0)` -> Overlaps layers: `metal2, psubdiffcont`
- **`VBE1_uq0`** on layer `metal2` at `(22.0, -1.0)` -> Overlaps layers: `metal2, psubdiffcont`

## 📊 Labeled Nets Summary Table

| Net Name | Labels (Layer @ Coords) | met1 Area (µm²) | met2 Area (µm²) | met3 Area (µm²) | Vias | BBox (µm) |
| :--- | :--- | ---: | ---: | ---: | :--- | :--- |
| **`IB_EA`** | metal2@(55.0,38.9), metal2@(117.3,-35.7) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, psubdiffcont:14, mvnsubdiffcont:4, viali:37 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`TRIM0`** | metal1@(100.0,-6.51) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`TRIM1`** | metal1@(130.0,-6.51) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`TRIM2`** | metal1@(100.0,-20.51) | 11.12 | 0.00 | 0.00 | - | `(86.1,-20.71)..(113.9,-20.31)` |
| **`TRIM3`** | metal1@(130.0,-20.51) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VAPWR`** | viali@(30.0,78.4) | 796.24 | 651.36 | 826.31 | viali:37, mvnsubdiffcont:4, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VBE1`** | metal3@(100.0,-2.1) | 796.24 | 651.36 | 826.31 | viali:37, via2:54, psubdiffcont:14, via1:244, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VBE1_uq0`** | metal2@(22.5,-1.0), metal2@(22.0,-1.0) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, via1:244, via2:54, viali:37, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VBE8`** | via1@(78.19,6.59) | 796.24 | 651.36 | 826.31 | via1:244, viali:37, psubdiffcont:14, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VGND`** | metal1@(-0.325,-2.2) | 796.24 | 651.36 | 826.31 | viali:37, psubdiffcont:14, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`VREF_LOW`** | metal2@(55.0,38.0), metal2@(136.62,-36.5) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, psubdiffcont:14, mvnsubdiffcont:4, viali:37 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_bias`** | metal2@(55.0,39.8) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_bias_n`** | metal2@(119.5,20.0) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_bias_n_uq0`** | metal2@(127.5,-0.18) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_bias_uq0`** | metal2@(138.0,35.2) | 796.24 | 651.36 | 826.31 | via2:54, psubdiffcont:14, mvnsubdiffcont:4, viali:37, via1:244 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_casc_n`** | metal2@(30.0,35.4) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, mvnsubdiffcont:4, viali:37, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_gate_top`** | metal2@(25.0,37.1) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, mvnsubdiffcont:4, viali:37, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_gate_top_uq0`** | metal2@(138.0,-0.7) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, psubdiffcont:14, mvnsubdiffcont:4, viali:37 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_mid1`** | metal2@(20.0,36.2) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, mvnsubdiffcont:4, viali:37, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`V_su_mid`** | metal1@(130.0,38.15) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`cn_mid`** | metal1@(138.0,25.15) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, mvnsubdiffcont:4, viali:37, via1:244, via2:54 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_b0`** | metal2@(100.0,-3.3) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_b1`** | metal2@(100.0,-17.37) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_b2`** | via1@(130.0,-17.37), metal2@(115.2,-24.8) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_b3`** | metal2@(116.0,14.1) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_r6m`** | metal2@(95.0,41.0) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`n_r7m`** | metal2@(95.0,41.8) | 796.24 | 651.36 | 826.31 | via1:244, psubdiffcont:14, viali:37, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net1`** | metal3@(50.0,-0.28) | 796.24 | 651.36 | 826.31 | via2:54, psubdiffcont:14, viali:37, via1:244, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net2`** | metal2@(3.0,54.15) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net3`** | metal2@(20.0,52.35) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net4`** | metal2@(12.0,23.25) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, mvnsubdiffcont:4, viali:37, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net5`** | metal2@(17.5,22.25) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, mvnsubdiffcont:4, viali:37, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net6`** | metal2@(8.0,53.25) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net7`** | metal2@(130.0,13.21) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net8`** | metal2@(130.0,15.45) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net9`** | metal3@(110.0,26.3) | 796.24 | 651.36 | 826.31 | psubdiffcont:14, viali:37, via1:244, via2:54, mvnsubdiffcont:4 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`net_tap`** | metal2@(31.5,55.05) | 796.24 | 651.36 | 826.31 | mvnsubdiffcont:4, viali:37, via1:244, via2:54, psubdiffcont:14 | `(-1.8,-36.7)..(143.4,79.2)` |
| **`sense_out`** | metal1@(135.0,35.7) | 796.24 | 651.36 | 826.31 | via1:244, via2:54, psubdiffcont:14, mvnsubdiffcont:4, viali:37 | `(-1.8,-36.7)..(143.4,79.2)` |
