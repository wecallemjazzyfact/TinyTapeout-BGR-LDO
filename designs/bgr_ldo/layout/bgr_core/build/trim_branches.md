# Trim Ladder Branch & Residual Resistance Report (`trim_branches.md`)

**Target Branches**: `P1` ~ `P6`  
**Source Coordinates**: Handoff §6.7 & `bgr_mos.mag` verified layout measurements  
**Process Corner Parameters**:
  - **Sky130A Typical**: metal1/metal2 = 125 mΩ/□ ($0.125\,\Omega/\text{sq}$), via1 (m2c) = 4,500 mΩ/cut ($4.5\,\Omega/\text{cut}$)
  - **HRHC Corner**: metal1/metal2 = 145 mΩ/□ ($0.145\,\Omega/\text{sq}$), via1 (m2c) = 15,000 mΩ/cut ($15.0\,\Omega/\text{cut}$)

## 📊 1. Trim Branch Geometry & Resistance Breakdown (P1–P6)

| Branch | Net | Route Description | Total Len (µm) | met1 Len (µm) | met2 Len (µm) | met1 (sq) | met2 (sq) | Total (sq) | Via1 Cuts | R_typ (Ω) | R_hrhc (Ω) |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **`P1`** | `n_b0` | n_b0 resistor side (met1 bar 110.30–114.34) -> b0.D comb | 58.37 | 6.15 | 52.22 | 15.38 | 130.55 | 145.93 | 2 | **27.24 Ω** | **51.16 Ω** |
| **`P2`** | `n_b1` | n_b1 resistor side (met1 L bridge x113.90–114.55) -> b0.S comb (= b1.D) | 25.30 | 0.76 | 24.54 | 2.92 | 61.35 | 64.27 | 1 | **12.53 Ω** | **24.32 Ω** |
| **`P3`** | `n_b2` | n_b2 resistor side (met1 bar 114.98–116.64) -> b1.S comb | 28.74 | 0.26 | 28.48 | 1.00 | 71.20 | 72.20 | 1 | **13.53 Ω** | **25.47 Ω** |
| **`P4`** | `n_b2` | n_b2 resistor side -> b2.D comb (bottom bypass: vert 115.60-116.00 -> y-25 horiz -> vert 114.86-115.16 -> y-33.1 horiz x99.90-115.16 -> via1 x100.00) | 53.84 | 0.66 | 53.18 | 2.00 | 139.70 | 141.70 | 2 | **26.71 Ω** | **50.55 Ω** |
| **`P5`** | `n_b3` | n_b3 resistor side -> b2.S comb (= b3.D) | 47.88 | 0.26 | 47.62 | 1.00 | 156.90 | 157.90 | 1 | **24.24 Ω** | **37.90 Ω** |
| **`P6`** | `b3.S` | b3.S comb -> VGND (x143.00-143.40 vert -> p-tap) | 29.30 | 0.40 | 28.90 | 1.00 | 72.25 | 73.25 | 1 | **13.66 Ω** | **25.62 Ω** |

## 🔌 2. Switch Residual Resistance Table (`R_short`)

> **Condition Note**: $R_{on} = 4.573\,\Omega$ is the fixed schematic simulated value (corner variation not applied).  

| Switch | Formula | P_head (Ω, Typ) | Ron (Ω) | P_tail (Ω, Typ) | **R_short (Typical)** | **R_short (HRHC)** |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| **`b0`** | `P1 + Ron + P2` | 27.24 | 4.573 | 12.53 | **44.35 Ω** | **80.05 Ω** |
| **`b1`** | `P2 + Ron + P3` | 12.53 | 4.573 | 13.53 | **30.63 Ω** | **54.36 Ω** |
| **`b2`** | `P4 + Ron + P5` | 26.71 | 4.573 | 24.24 | **55.52 Ω** | **93.01 Ω** |
| **`b3`** | `P5 + Ron + P6` | 24.24 | 4.573 | 13.66 | **42.47 Ω** | **68.09 Ω** |

## 🔍 3. Branch Detailed Segment Breakdown

### Branch `P1` (n_b0)
* **Description**: n_b0 resistor side (met1 bar 110.30–114.34) -> b0.D comb
* **Via1 Cuts**: 2
* **Typical Resistance**: 27.24 Ω | **HRHC Resistance**: 51.16 Ω
* **Segment Decomposition**:
  1. **metal1**: Length = 4.04 µm, Width = 0.4 µm -> **10.1 sq**
  2. **metal2**: Length = 9.0 µm, Width = 0.4 µm -> **22.5 sq**
  3. **metal2**: Length = 27.85 µm, Width = 0.4 µm -> **69.62 sq**
  4. **metal2**: Length = 15.37 µm, Width = 0.4 µm -> **38.42 sq**
  5. **metal1**: Length = 2.11 µm, Width = 0.4 µm -> **5.27 sq**

### Branch `P2` (n_b1)
* **Description**: n_b1 resistor side (met1 L bridge x113.90–114.55) -> b0.S comb (= b1.D)
* **Via1 Cuts**: 1
* **Typical Resistance**: 12.53 Ω | **HRHC Resistance**: 24.32 Ω
* **Segment Decomposition**:
  1. **metal1**: Length = 0.76 µm, Width = 0.26 µm -> **2.92 sq**
  2. **metal2**: Length = 24.54 µm, Width = 0.4 µm -> **61.35 sq**

### Branch `P3` (n_b2)
* **Description**: n_b2 resistor side (met1 bar 114.98–116.64) -> b1.S comb
* **Via1 Cuts**: 1
* **Typical Resistance**: 13.53 Ω | **HRHC Resistance**: 25.47 Ω
* **Segment Decomposition**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 28.48 µm, Width = 0.4 µm -> **71.2 sq**

### Branch `P4` (n_b2)
* **Description**: n_b2 resistor side -> b2.D comb (bottom bypass: vert 115.60-116.00 -> y-25 horiz -> vert 114.86-115.16 -> y-33.1 horiz x99.90-115.16 -> via1 x100.00)
* **Via1 Cuts**: 2
* **Typical Resistance**: 26.71 Ω | **HRHC Resistance**: 50.55 Ω
* **Segment Decomposition**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 28.88 µm, Width = 0.4 µm -> **72.2 sq**
  3. **metal2**: Length = 0.94 µm, Width = 0.4 µm -> **2.35 sq**
  4. **metal2**: Length = 8.1 µm, Width = 0.3 µm -> **27.0 sq**
  5. **metal2**: Length = 15.26 µm, Width = 0.4 µm -> **38.15 sq**
  6. **metal1**: Length = 0.4 µm, Width = 0.4 µm -> **1.0 sq**

### Branch `P5` (n_b3)
* **Description**: n_b3 resistor side -> b2.S comb (= b3.D)
* **Via1 Cuts**: 1
* **Typical Resistance**: 24.24 Ω | **HRHC Resistance**: 37.90 Ω
* **Segment Decomposition**:
  1. **metal1**: Length = 0.26 µm, Width = 0.26 µm -> **1.0 sq**
  2. **metal2**: Length = 2.2 µm, Width = 0.4 µm -> **5.5 sq**
  3. **metal2**: Length = 45.42 µm, Width = 0.3 µm -> **151.4 sq**

### Branch `P6` (b3.S)
* **Description**: b3.S comb -> VGND (x143.00-143.40 vert -> p-tap)
* **Via1 Cuts**: 1
* **Typical Resistance**: 13.66 Ω | **HRHC Resistance**: 25.62 Ω
* **Segment Decomposition**:
  1. **metal2**: Length = 28.9 µm, Width = 0.4 µm -> **72.25 sq**
  2. **metal1**: Length = 0.4 µm, Width = 0.4 µm -> **1.0 sq**

