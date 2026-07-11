# TinyTapeout Analog (BGR + LDO) Project Rules

Below are the project-specific guardrails and constraints that must be adhered to at all times during this workspace session.

## Rules & Constraints

### 1. Circuit Design Specifications
* **Voltage Levels**: LDO Input = 3.3V (`VAPWR`), Target Output = 1.8V.
* **Error Amplifier Supply**: The EA must be supplied by the 3.3V `VAPWR` rail to ensure adequate gate drive headroom.
* **BGR Resistors**: Keep the ratio $R_2 = 2R_1$ for bandgap reference core matching.

### 2. Layout Layout & DRC Guardrails (Sky130A)
* **Metal 5 Prohibition**: **NEVER** use the `metal 5` (met5) layer anywhere in the design routing.
* **Power Pin Stripes**: `VGND`, `VDPWR`, and `VAPWR` pins must be vertical stripes on the `met4` (metal 4) layer.
  * Must span from within the bottom 10 µm to the top 10 µm of the tile.
  * Minimum stripe width = 1.2 µm.
  * `uses_vapwr: true` must be specified in `info.yaml` for 3.3V template usage.
* **Unused Pin Tie-off**:
  * Unused analog pins (`ua[]`) must be tied to `VGND` or connected to `conb` cells. Do not leave them floating.
  * Unused digital output pins (`uo_out`, `uio_out`, `uio_oe`) must be tied to `VGND`.

### 3. Submission & Export Requirements
* **Naming**: The top module name must start with `tt_um_`. GDS/LEF file names must match this module name exactly.
* **LEF Write Option**: In Magic, export the LEF file using:
  `lef write ../lef/tt_um_project_name.lef -pinonly`
* **Hierarchy**: Do not flatten the cell hierarchy in the `.mag` file to prevent mapping/DRC validation errors.

### 4. Agent Tool Usage & Modification Rules
* **Schematic File Modifications:** The AI agent must **NEVER** modify schematic files (`.sch` or extension-less xschem formats) unless explicitly requested by the USER.
* **Mandatory Backup:** If the USER explicitly requests a modification to a schematic file, the agent must create a backup copy of the file first (e.g. by appending `.bak` to the filename) before performing any edits.

