# Trim Ladder Path Length & Resistance Report (`trim_paths.md`)

**Target Nets**: `n_b0`, `n_b1`, `n_b2`, `n_b3`  
**PDK Sheet Resistance Source**: Sky130A process nominal (met1: ~0.125 Ω/sq, met2: ~0.125 Ω/sq)  
**Methodology**: Geometrically verified path segment decomposition based on Handoff §6.7 coordinates  

## 📊 Trim Ladder Paths Summary Table

| Net Name | Total Route Len (µm) | met1 Len (µm) | met2 Len (µm) | met1 (sq) | met2 (sq) | Total Squares (sq) | Est. Resistance (Ω) | Via1 / Via2 |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| **`n_b0`** | ~58.4 | 6.15 | 52.22 | 15.38 | 130.55 | 145.93 | ~18.24 Ω | 2 / 0 |
| **`n_b1`** | ~24.8 | 0.26 | 24.54 | 1.00 | 61.35 | 62.35 | ~7.79 Ω | 1 / 0 |
| **`n_b2`** | ~30.7 | 0.26 | 30.48 | 1.00 | 76.20 | 77.20 | ~9.65 Ω | 1 / 0 |
| **`n_b3`** | ~47.9 | 0.26 | 47.62 | 1.00 | 156.90 | 157.90 | ~19.74 Ω | 1 / 0 |

## 🔍 Path Breakdown Details

### Net `n_b0`
* **Handoff Route Specification**: met1 bar (110.30–114.34, y 5.3–5.7) -> via1 -> met2 vert 110.95–111.35 -> y -3.3 horiz -> x 83.3–83.7 vert -> y -18.27 horiz -> via1 -> b0 D comb
* **Via Counts**: Via1 = 2, Via2 = 0
* **Segment Breakdown**:
  1. **metal1**: Length = 4.04 µm, Width = 0.4 µm -> **10.1 sq**
  2. **metal2**: Length = 9.0 µm, Width = 0.4 µm -> **22.5 sq**
  3. **metal2**: Length = 27.85 µm, Width = 0.4 µm -> **69.62 sq**
  4. **metal2**: Length = 15.37 µm, Width = 0.4 µm -> **38.42 sq**
  5. **metal1**: Length = 2.11 µm, Width = 0.4 µm -> **5.28 sq**

### Net `n_b1`
* **Handoff Route Specification**: met1 L (R2b0<->R2b1) -> via1 (113.79–114.05, y7.1..7.36) -> met2 vert 113.7–114.1 (y -17.12..7.42) -> b0 S comb
* **Via Counts**: Via1 = 1, Via2 = 0
* **Segment Breakdown**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 24.54 µm, Width = 0.4 µm -> **61.35 sq**

### Net `n_b2`
* **Handoff Route Specification**: via1 (115.68–115.94, y3.62..3.88) -> met2 vert 115.6–116.0 (y -24.6..3.88) -> b1 S comb / b2.D met2 horiz y-33.1..-32.7
* **Via Counts**: Via1 = 1, Via2 = 0
* **Segment Breakdown**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 28.48 µm, Width = 0.4 µm -> **71.2 sq**
  3. **metal2**: Length = 2.0 µm, Width = 0.4 µm -> **5.0 sq**

### Net `n_b3`
* **Handoff Route Specification**: via1 (116.24–116.50, y13.97..14.23) -> met2 horiz y13.9..14.3 -> vert 114.3..114.6 (y -31.12..14.3) -> b2 S comb
* **Via Counts**: Via1 = 1, Via2 = 0
* **Segment Breakdown**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 2.2 µm, Width = 0.4 µm -> **5.5 sq**
  3. **metal2**: Length = 45.42 µm, Width = 0.3 µm -> **151.4 sq**

