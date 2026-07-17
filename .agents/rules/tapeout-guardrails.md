---
trigger: always_on
---

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



## 실행 효율 규칙 (토큰 절약 — 위반 시 중단)
- 시뮬레이션은 반드시 동기 1회 실행: 
  `docker exec ... bash -l -c "cd <dir> && ngspice -b <file>.spice > <file>.log 2>&1"`
  실행 후 즉시 로그 파일을 읽는다. manage_task/schedule 로 폴링 대기 금지 —
  ngspice -b 는 blocking 이므로 기다릴 것이 없다.
- "waiting for simulation" 류의 대기 턴 생성 금지. 명령이 끝나면 결과가 있고,
  끝나지 않았으면 명령이 반환되지 않은 것이다.
- 정본(bgr_core_tb.spice 등)의 임시 사본/변형 파일 생성 금지. op 가 필요하면
  정본의 .control 블록을 수정하고, 완료 후 원복한다. (_op, _clean, _precise
  등 접미사 파일이 stale-file 사고의 원인이었음)
- 같은 목적의 명령 재시도는 2회까지. 2회 실패 시 시도를 멈추고 에러 원문과
  함께 사용자에게 보고 후 지시 대기.
- 한 번의 요청에 시뮬 실행은 최대 2회. 그 이상 필요하면 계획을 먼저 보고.
  * Do not flatten layouts or cell hierarchies inside the `.mag` file. Keep the hierarchical structure intact to prevent DRC mapping errors.

## 시뮬레이션 실행 권한 (위반 시 작업 중단)
- 모든 시뮬레이션 실행(ngspice, 배치, op, tran, sweep 포함)은 사용자의
  명시적 실행 지시가 있을 때만 수행한다. "설계안 제시" "계산" "계획" 요청에
  시뮬 실행을 포함하지 않는다.
- 설계 변경 후 워크플로우는 고정: (1) 계산/예측 표 제시 → (2) 사용자 승인
  → (3) 사용자가 xschem 수정 → (4) 사용자가 "시뮬 돌려" 라고 말한 뒤에만 실행.
- 실행 전 반드시 한 줄로 선언: "실행 대상 파일 / 해석 종류 / 예상 소요" —
  선언 없이 실행한 시뮬 결과는 무효로 간주하고 보고하지 않는다.
- 검증·확인 목적이라도 예외 없음. 궁금하면 실행하지 말고 사용자에게 물을 것.


## 넷리스트 무결성 (위반 시 결과 무효)
- 시뮬/해석 대상 넷리스트는 항상 사용자가 방금 추출한 것만 사용. 디스크에서
  발견한 기존 .spice 를 임의로 신뢰하지 않는다.
- 넷리스트를 읽기 전 반드시: (1) ls -l 로 .sch 와 .spice 타임스탬프 비교
  (.spice 가 더 최신이어야 함), (2) 대상 소자 라인을 grep 으로 원문 인용.
  이 두 가지를 보고에 포함하지 않은 분석은 무효.
- .spice 가 .sch 보다 오래됐으면 분석을 멈추고 "재추출 필요"만 보고.

## 5. Transistor Sizing & gm/Id LUT Rules
- **LUT-Only Device Parameters:** 소자 파라미터 수치는 LUT 조회 결과만 사용한다. 기억 기반 수치(Vth, mobility, Cox 등) 인용 금지. 조회 코드와 결과를 함께 보고하지 않은 사이징 계산은 무효.
- **Sizing Proposal Principle:** LUT 조회로 도출한 사이징은 "제안"이며, 최종 확정은 사용자의 회로 시뮬 검증 후에만 결정한다.