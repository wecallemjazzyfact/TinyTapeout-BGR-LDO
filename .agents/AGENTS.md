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

### 5. Schematic-First Simulation Guardrails
* **Schematic as Golden Source (정본):**
  * 회로 시뮬레이션의 최종 정본은 항상 **xschem schematic (.sch)** 파일이어야 합니다.
  * AI 에이전트는 절대 `.spice` 넷리스트 파일을 직접 수동 편집하여 시뮬레이션을 수행해서는 안 됩니다.
  * 회로 수정이 필요할 경우 반드시 **"xschem에서 Schematic 수정 ➜ 넷리스트 재추출 ➜ ngspice 시뮬레이션"** 프로세스를 엄격히 준수해야 합니다.

### 6. Simulation Reporting Rules
* **Simulation Result Verification**: 모든 시뮬레이션 보고서 작성 시, 데이터 오염 방지 및 검증 투명성을 위해 다음 3종 세트를 반드시 원문 그대로 첨부해야 합니다:
  1. 시뮬레이션에 사용된 `.spice` 넷리스트 파일의 SHA256/MD5 지문(Checksum).
  2. ngspice 실행 로그 첫 줄 또는 헤더에 표시된 정확한 타임스탬프.
  3. 시뮬레이션 핵심 측정치(V_ref, V_bias, I_top 등)를 나타내는 로그의 raw 텍스트 원문 (요약 또는 재기입 금지, 복사-붙여넣기 형태).

### 7. Transistor Sizing & gm/Id LUT Rules
* **LUT-Only Device Parameters:** 소자 파라미터 수치는 LUT 조회 결과만 사용한다. 기억 기반 수치(Vth, mobility, Cox 등) 인용 금지. 조회 코드와 결과를 함께 보고하지 않은 사이징 계산은 무효.
* **Sizing Proposal Principle:** LUT 조회로 도출한 사이징은 "제안"이며, 최종 확정은 사용자의 회로 시뮬 검증 후에만 결정한다.

