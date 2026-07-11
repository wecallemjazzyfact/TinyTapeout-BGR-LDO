# TinyTapeout Analog (BGR + LDO) Tapeout Guardrails

This document outlines the hard rules and design constraints that the AI agent must enforce and remember throughout the design, simulation, and layout process of the BGR and LDO project.

## 1. Electrical & Schematic Guardrails
* **LDO Voltage Configuration**: 
  * Input voltage ($V_{in}$): 3.3V (connected to the analog supply rail `VAPWR`).
  * Target output voltage ($V_{out}$): 1.8V.
* **Error Amplifier (EA) Power Supply**: 
  * The Error Amplifier MUST be powered by `VAPWR` (3.3V) to guarantee sufficient headroom for control loop and pass device gate drive.
* **BGR Resistor Ratios**: 
  * The feedback divider / current mirror resistors must be matched precisely. R2 must be twice R1 ($R_2 = 2R_1$) where applicable to align with the core bandgap reference specifications.

## 2. Layout & Metal Constraints (Sky130A)
* **Metal 5 Prohibition**: 
  * **NEVER** use the `metal 5` (met5) layer in any custom cell or routing. This layer is exclusively reserved for the global TinyTapeout power grid.
* **Power Pin Stripes (met4)**: 
  * Power pins (`VGND`, `VDPWR`, `VAPWR`) must be drawn as vertical stripes on the `met4` (metal 4) layer.
  * Power stripes must start within the bottom 10 µm of the module and extend to at least the top 10 µm of the module.
  * The minimum width for any power stripe is **1.2 µm**.
  * For 3.3V operation, the `tt_analog_*_3v3.def` template must be used, and `uses_vapwr: true` must be configured in `info.yaml`.

## 3. Pin Mapping & Unused Pin Treatments
* **Analog Pin Sequence**:
  * Analog pins must be allocated in order, starting from `ua[0]` up to `ua[5]`. Do not skip pin indices.
  * Any unused or unconnected analog pins (`ua[]`) must be tied directly to `VGND` or connected to `conb` cells to avoid floating gate nodes.
* **Digital Outputs**:
  * All unused digital outputs (`uo_out[]`, `uio_out[]`, `uio_oe[]`) must be tied to `VGND`. Do not leave them floating.

## 4. File Structure, Naming & Tool Operations
* **Top Module Naming**: 
  * The top module name must start with `tt_um_` (e.g., `tt_um_bgr_ldo_shuttle`).
  * GDS and LEF filenames must match the top module name exactly: `gds/tt_um_name.gds` and `lef/tt_um_name.lef`.
* **LEF Generation (Magic)**: 
  * When exporting the LEF file, you must use the `-pinonly` command parameter:
    `lef write ../lef/tt_um_project_name.lef -pinonly`
* **Hierarchy Conservation**: 
  * Do not flatten layouts or cell hierarchies inside the `.mag` file. Keep the hierarchical structure intact to prevent DRC mapping errors.
