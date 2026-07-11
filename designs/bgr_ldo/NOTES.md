# TinyTapeout 아날로그 (BGR + LDO) 제출 하드 제약 사항 및 프로젝트 고정 사양

이 문서는 TinyTapeout 아날로그 프로젝트 규격 문서 및 제출 템플릿에 명시된 하드웨어적/설정상 제약 규칙을 원문 그대로 인용하여 정리하고, 우리 BGR+LDO 프로젝트의 고정 설계 사양을 명시합니다.

---

## 📋 1. 아날로그 제출 하드 제약 사항 표 (원문 인용)

| 제약 사항 구분 | 공식 규격 및 규칙 내용 (원문 그대로 인용) | 출처 파일명 |
| :--- | :--- | :--- |
| **사용 가능 아날로그 핀 `ua[]` 개수 및 순서** | <ul><li>`Even though there are 8 pins in the templates, you can only use the first 6.`</li><li>`You must use the pins in order, starting from 0.`</li><li>`only ua[5:0] can be used`</li><li>`The number of pins that will actually be connected to pads depends on the number of analog pins that you defined in the pinout section in info.yaml (and paid for). For example, if you purchased two analog pins, only ua[0] and ua[1] will be connected to the pads. The remaining pins will not be connected.`</li><li>`If you end up with pins which are not being driven and are floating, please either connect them to GND or use conb cells`</li><li>`Resistance: < 500 ohm`</li><li>`Capacitance: < 5 pf`</li><li>`Max current: 4 mA`</li></ul> | `analog-specs.md`<br>`project.v` |
| **파워 핀 (VDD/VAPWR/VGND) 규칙** | <ul><li>`VGND: Ground rail`</li><li>`VDPWR: 1.8V digital core voltage`</li><li>`VAPWR: 3.3V analog supply rail (optional, requires a different template)`</li><li>`A draw of around 20mA from the power supply will result in a 0.1V drop through the PDN.`</li><li>`Power pins need to be vertical stripes on met4 layer and must adhere to the following rules:`<br>`1. Start within the bottom 10 µm of the module and extend at least to the top 10 µm of the module.`<br>`2. Minimum width of 1.2 um.`<br>`5. The actual metal area can be larger or have a different shape, but the area defined as a pin must comply with these constraints.`</li><li>**[누락 주의]** 원문 규격의 met4 3번, 4번 규칙이 현재 표 인용에서 누락되었으므로, 레이아웃 진입 전에 공식 원문 문서를 파악하여 전체 규칙(1~5번)을 재확보 및 검증해야 함.</li></ul> | `analog-specs.md` |
| **3.3V 레일 사용 조건** | <ul><li>`3. Projects utilizing the 3.3V rail MUST use the tt_analog_*_3v3.def templates and set uses_3v3: true in info.yaml.`</li><li>`uses_vapwr: false # Set to true if your project uses second analog power supply (VAPWR) in addition to 1.8V (VDPWR)`</li><li>**[잠정 결론]** `uses_vapwr: true`로 설정하고 `_3v3.def` 템플릿을 사용함. 공식 문서(`analog-specs.md`)의 `uses_3v3: true` 표기는 구버전 양식으로 추정됨.</li></ul> | `analog-specs.md`<br>`info.yaml` |
| **금지 메탈층 및 파워핀 메탈층** | <ul><li>금지 레이어: `You are not allowed to use the metal 5 layer in your design, as it’s used by Tiny Tapeout’s power grid.`</li><li>파워핀 레이어: `Power pins need to be vertical stripes on met4 layer`</li></ul> | `analog-specs.md` |
| **아날로그 타일 크기** | <ul><li>`An analog project can either be 1x2 or 2x2 tiles large.`</li><li>`Projects with analog pins must be two tiles high.`</li><li>`1x2 tiles = 160x225um`</li><li>`2x2 tiles = 334x225um`</li><li>`3.3v designs are slightly narrower as an additional power FET is required. Make sure to use our templates linked above.`</li><li>**[설계 메모]** 3.3V 전원 사용 시 power FET 레이아웃으로 인해 1x2 타일 가용폭이 $160\,\text{µm}$보다 좁아집니다. 만약 1x2 타일에 아날로그 회로가 전부 올라가지 않는 경우, 2x2 타일 크기 ($334\times225\,\text{µm}$) 사용을 고려해야 합니다.</li></ul> | `analog-specs.md` |
| **디지털 핀 규칙 및 플로팅 방지** | <ul><li>디지털 포트 구성: `input wire [7:0] ui_in`, `output wire [7:0] uo_out`, `input wire [7:0] uio_in`, `output wire [7:0] uio_out`, `output wire [7:0] uio_oe`</li><li>디지털 핀 제약: `Drive strength (source/sink) | 4 mA`, `Maximum output frequency | 33 MHz`, `Maximum input frequency | 66 MHz`, `IO supply voltage * | 1.71V - 5.5V` (`* The demo board provides 3.3V IO supply voltage. The input pins are not 5V tolerant.`)</li><li>플로팅 방지 규칙: `Important: Do not leave any floating digital output pins in your design. Connect any unused uo_out, uio_out and uio_oe pins to GND.`</li></ul> | `analog-specs.md`<br>`project.v`<br>`gpio.md` |
| **info.yaml 필수 키 및 주석 의미** | <ul><li>`title: "" # Project title`</li><li>`author: "" # Your name`</li><li>`description: "" # One line description of what your project does`</li><li>`language: "Analog" # other examples include Verilog, Amaranth, VHDL, etc`</li><li>`clock_hz: 0 # Clock frequency in Hz (or 0 if not applicable)`</li><li>`tiles: "1x2" # Valid values for analog projects: 1x2, 2x2`</li><li>`analog_pins: 2 # Valid values: 0 to 6`</li><li>`uses_vapwr: false # Set to true if your project uses second analog power supply (VAPWR) in addition to 1.8V (VDPWR)`</li><li>`top_module: "tt_um_example" # Your top module name must start with "tt_um_". Make it unique by including your github username:`</li><li>`source_files: # List your project's source files here. Source files must be in ./src and you must list each source file separately, one per line:`</li><li>`pinout: # The pinout of your project. Leave unused pins blank. DO NOT delete or add any pins.`</li><li>`yaml_version: 6 # Do not change!`</li></ul> | `info.yaml` |

---

## 🎯 2. 우리 프로젝트 고정 사양 (Project Specifications)

우리 BGR + LDO 통합 아날로그 IP 프로젝트의 고정 하드웨어 설계 명세입니다.

### 2.1. 1단계/2단계 공정 산포 대응 전략 (2-Stage Variation Mitigation)
* **1차 대응 (Layout Matching):** Common-centroid 매칭 배치, Dummy 소자 가드, Guard-ring 분리 및 웰 격리를 통해 기생 성분 및 레이아웃 불일치를 근본적으로 최소화하는 것을 우선으로 함.
* **2차 대응 (Digital Trimming):** 공정 코너 산포($ss/ff$) 및 오차 증폭기의 정적 입력 오프셋(Input Offset)으로 인한 출력 편차를 제거하기 위해 디지털 트림 회로를 내장함.
* **제어 방식:** 3.3V 아날로그 블록의 면적과 패드 제한을 고려하여 외부 디지털 입력 핀(`ui_in`)을 사용하되, 입력단에 Level Shifter를 추가 장착하여 아날로그 전용 핀 소모를 방지하고 제어함.

### 2.2. BGR (Bandgap Reference)
* **목표 기준 전압 ($V_{ref}$):** $1.2\,\text{V}$ 고정.
* **BGR 코어 정합 저항비:** $R_2 = 2 \cdot R_1$ 준수.
* **3-bit 저항 트림 회로 내장:** 공정 산포 및 오프셋 보상을 위해 3-bit 디지털 가변 저항 트림 링크를 BGR 출력단 저항 사다리에 설계하여 $V_{ref}$의 절대값을 미세 튜닝함.

#### BGR 설계 목표 스펙
| 스펙 | 목표 | 근거/비고 |
| :--- | :--- | :--- |
| $V_{ref}$ | $1.2\,\text{V}$ | LDO 분압 $R_2=2R_1$ (→ $1.8\,\text{V}$)과 일관 |
| TC ($-40\sim125^\circ\text{C}$) | $< 50\,\text{ppm}/^\circ\text{C}$ (목표 $<30$) | cw_vref/tt_um_bgr 실측 20~40ppm |
| Line regulation | $< 0.5\,\%\text{/V}$ | VAPWR 2.8~3.6V 스윕 |
| PSRR @DC | $< -40\,\text{dB}$ | cascode + 후단 LDO |
| $I_Q$ (BGR only) | $< 15\sim20\,\text{µA}$ | 브랜치당 ~3~5µA |
| Startup time | $< \text{수 µs}$, 확정 기동 | 축퇴점 회피 |
| Area (BGR only) | $< \sim 2500\,\text{µm}^2$ | 1x2에 여유 |

#### BGR 설계 결정 사항
* **검증 조건:** 27°C 단일 온도 분석에 그치지 않고, **$-40 / 27 / 125^\circ\text{C} \times \text{코너(ss/tt/ff)}$** 조합 전체로 검증 수행.
* **소자 선택 (Devices):** BGR 코어 mirror는 저전압 고이득 매칭을 위해 **1.8V 소자(`nfet_01v8` / `pfet_01v8_lvt`)**를 사용하고, 3.3V(`VAPWR`)가 직접 인가되는 노드만 thick-oxide인 **`_g5v0d10v5`** 소자 사용.
* **Mirror 설계:** 고정밀 정합 및 미러 계수 안정성을 위해 **$V_{ov} \approx 120\sim150\,\text{mV}$ (저속/고정밀)**, **$L = 0.5\sim1.0\,\text{µm}$**로 설정하여 출력 저항($r_o$) 및 정합성을 개선하고, $W$는 pygmid(gm/Id 툴)를 사용해 역산하여 설계.
* **저항 소자:** 온도 보상 및 정밀도 정합을 위해 BGR 내부 저항($R_1$, $R_6$, $R_7$, $R_L$)은 모두 **`sky130_fd_pr__res_high_po`** 소자로 통일.
* **PNP BJT:** **`pnp_05v5_W0p68L0p68`** 사용. $Q_1 (m=1)$ / $Q_2 (m=8)$ 구조로 배치하며 에미터가 위쪽 노드이고 베이스와 컬렉터는 `VGND`에 접지.
* **참고 문헌/교재:** Razavi (기본 이론 및 원리) + Baker Ch. 20 (구현 및 레이아웃 매칭 기법)

### 2.3. LDO (Low-Dropout Regulator)
* **입력 전압 ($V_{in}$ / $VAPWR$):** $3.3\,\text{V}$ (3.3V analog supply rail).
* **출력 전압 ($V_{out}$):** $1.8\,\text{V}$ 고정.
* **LDO 분압 저항 트림 내장:** 오차 증폭기의 오프셋 전압 상쇄 및 $V_{out}$의 절대값 튜닝을 위해 피드백 분압 저항단에 저항 트림 회로를 추가함.
* **최대 부하 전류 ($I_{load, max}$):** $\le 4\,\text{mA}$ (하드웨어 제약 고려).
  * 패스 트랜지스터(PMOS Pass Device) 크기 및 특성화: 아날로그 핀 "Max current: 4 mA" 제약으로 인해 $V_{out}$을 `ua[0]`으로 인가할 경우 핀 최대 허용 전류 4mA 한계에 도달함. 따라서 공칭 2~3mA, 최대 4mA까지만 동작하도록 부하 전류를 명시하고 특성화 수행.
* **Load Transient 특성화 목표:** 부하 전류 스위칭($0 \leftrightarrow I_{load, max}$) 시 출력 전압 과도 응답 특성(Overshoot/Undershoot 특성 및 복구 시간)을 모니터링하고 보상망을 최적화함.
* **측정 및 로드 레귤레이션 주의사항:**
  * 아날로그 핀 경로 자체에 존재하는 기생 저항($R < 500\,\Omega$) 및 기생 용량($C < 5\,\text{pF}$)이 $V_{out} \leftrightarrow$ 외부 패드 사이에 직렬로 물리적 연결됨.
  * 이로 인해 외부에서 측정한 Load Regulation은 $V_{out, pad} = V_{out, chip} - I_{load} \cdot R_{path}$ 에 의해 `실제 load reg + I_load \times R_path`로 오염되어 보일 수 있으므로 켈빈 센싱 핀의 추가 여부 검토가 필요함.

### 2.4. 오차 증폭기 (Error Amplifier - EA)
* **전력 급전 전압:** $VAPWR$ ($3.3\,\text{V}$).
  * 오차 증폭기의 전력 공급단을 디지털 1.8V($VDPWR$)가 아닌 아날로그 $3.3\,\text{V}$($VAPWR$)에 직접 연결하여 게이트 구동 헤드룸 확보.

### 2.5. 제어 및 모니터링 인터페이스 (PG / EN)
* **EN (LDO Enable 신호):** 외부 디지털 핀 `ui_in[]`을 사용하여 컨트롤. (Level Shifter를 경유하여 3.3V EA 구동부 EN 게이트 전달)
* **PG (Power Good 신호):** LDO 출력이 안정 영역에 도달했음을 알리는 디지털 핀 `uo_out[]`을 통해 전송.


---

## 🛠️ 3. Verification & Layout Lessons Learned (레이아웃 및 검증 교훈)

### 3.1 레이아웃 크기 및 경계 (Boundary) 제약
* **물리적 크기 제약 (3.3V Analog):** 
  * TinyTapeout의 precheck (KLayout Checks 및 Pin check)를 통과하려면 GDS 레이아웃 경계가 DEF 템플릿의 정확한 다이 영역 크기와 일치해야 합니다.
  * 3.3V 아날로그 1x2 타일의 경우, 파워 트랜지스터(Power FET) 배치 공간으로 인해 폭이 다소 좁아져 **정확히 가로 $145.36\,\text{µm}$ (145360 DEF units), 세로 $225.76\,\text{µm}$ (225760 DEF units)** 크기로 맞춰야 합니다.
  * 따라서 레이아웃을 시작할 때 반드시 `tt_analog_1x2_3v3.def` 파일을 Magic으로 읽어(`def read tt_analog_1x2_3v3.def`) 경계(Boundary), Met4 파워 스트라이프 및 핀 위치 프레임을 생성하고 그 내부에서 레이아웃을 수행해야 합니다.

### 3.2 컨테이너 기반 LVS/DRC 검증 실행법
컨테이너 내에서 JKU 제공 레이아웃 검증 도구(`iic-drc.sh`, `iic-lvs.sh`) 및 TinyTapeout `precheck.py`를 실행할 때는, 환경 변수(`$PDK`, `$PDKPATH`)와 실행 파일 경로가 꼬이지 않도록 **반드시 로그인 쉘(`bash -l -c`) 옵션**과 함께 아래의 포맷으로 명령어를 전달해야 합니다.

* **TinyTapeout Precheck 실행 명령어:**
  `precheck.py`는 내부에서 `magic_drc.tcl` 등의 상대 경로 파일을 호출하므로 반드시 `tt/precheck` 폴더로 이동한 후 실행해야 하며, GDS 경로는 절대 경로를 사용하는 것이 안전합니다.
  ```bash
  docker exec -i iic-osic-tools_xvnc_uid_1000 bash -l -c "cd /foss/designs/tt-analog/repos/ttsky-analog-template/tt/precheck && export PDK=sky130A && python3 precheck.py --gds /foss/designs/tt-analog/repos/ttsky-analog-template/gds/tt_um_example.gds --tech sky130A"
  ```

* **JKU DRC (`iic-drc.sh`) 실행 명령어:**
  Magic과 KLayout DRC를 동시에 가동합니다.
  ```bash
  docker exec -i iic-osic-tools_xvnc_uid_1000 bash -l -c "export PDK=sky130A && export PDKPATH=/foss/pdks/sky130A && iic-drc.sh -b -w /foss/designs/designs/bgr_ldo/work /foss/designs/designs/bgr_ldo/layout/tt_um_bgr_ldo.gds"
  ```

* **JKU LVS (`iic-lvs.sh`) 실행 명령어:**
  xschem 회로도(`.sch` 또는 사전 추출된 `.spice`)와 layout GDS를 대조하여 핀 정합성을 확인합니다.
  ```bash
  docker exec -i iic-osic-tools_xvnc_uid_1000 bash -l -c "export PDK=sky130A && export PDKPATH=/foss/pdks/sky130A && iic-lvs.sh -w /foss/designs/designs/bgr_ldo/work -s /foss/designs/designs/bgr_ldo/src/tt_um_bgr_ldo.sch -l /foss/designs/designs/bgr_ldo/layout/tt_um_bgr_ldo.gds -c tt_um_bgr_ldo"
  ```

---

## 📊 4. BGR PNP Core Simulation Results

BGR 설계의 핵심 요소인 BJT 코어 단일 소자의 $V_{BE}$ 전압 특성 및 $1:8$ 소자쌍의 $\Delta V_{BE}$ 전압 특성을 시뮬레이션으로 검증한 실측 결과 기록입니다.

### 4.1. Testbench 1: 단일 PNP $V_{BE}$ 특성 (`pnp_vbe`)
* **시뮬레이션 조건 (Simulation Setup):**
  * **대상 소자 (DUT):** `sky130_fd_pr__pnp_05v5_W0p68L0p68` ($m=1$)
  * **결선 형태:** 다이오드 연결 (Collector와 Base를 모두 `VGND`(= 전역 접지 `0`)에 연결, Emitter를 능동 노드로 활용)
  * **바이어스 공급:** 3.3V DC 전원원($V_1$)을 급전하여, 이상 전류원($I_0$)을 통해 Emitter 단자에 전류를 주입
  * **시뮬레이션 타입:** DC 전류 스윕 (`.dc I0 1u 10u 0.1u`) 및 온도 고정 ($27^\circ\text{C}$)
* **검증 및 측정 결과:**
  * **바이어스 동작점:** 브랜치당 설계 목표 바이어스 전류인 **$I_0 = 3.0\,\text{µA}$**에서 에미터-베이스 다이오드 전압 $V_{BE}$ 측정
  * **측정 전압 ($vbe\_val$):** **$774.05\,\text{mV}$** ($0.774052\,\text{V}$)
* **물리적 의미:**
  * 본 설계의 CTAT(Complementary to Absolute Temperature) 브랜치의 기준 $V_{BE}$ 기저 동작 수준을 정의합니다.

### 4.2. Testbench 2: $1:8$ 매칭 $\Delta V_{BE}$ 특성 (`delta_vbe`)
* **시뮬레이션 조건 (Simulation Setup):**
  * **대상 소자 (DUT):** 
    * `QA` ($m=1$): `pnp_05v5_W0p68L0p68`
    * `QB` ($m=8$): `pnp_05v5_W0p68L0p68`
  * **바이어스 공급:** 각 BJT의 에미터에 독립적인 동일 스펙의 이상 전류원($I_0 = 3\,\text{µA}$, $I_1 = 3\,\text{µA}$)을 배치하여 정전류 공급
  * **시뮬레이션 타입:** 온도 스윕 (`.dc temp -40 125 5`)
  * **수식 정의:** $\Delta V_{BE} = V_{BE1} (m=1) - V_{BE8} (m=8)$
* **검증 및 측정 결과:**
  * **측정 전압 ($dvbe\_27$):** **$53.02\,\text{mV}$** ($5.30196 \times 10^{-2}\,\text{V}$) @ $27^\circ\text{C}$ ($300.15\,\text{K}$)
  * **이론 수식 대조:**
    $$\Delta V_{BE} = V_T \ln(N) = \frac{k T}{q} \ln(8)$$
    $T = 27^\circ\text{C}$ ($300.15\,\text{K}$) 조건 하에:
    $$\Delta V_{BE, \text{이론}} = 25.865\,\text{mV} \times \ln(8) \approx 25.865\,\text{mV} \times 2.07944 \approx 53.78\,\text{mV}$$
    * **오차율:** 실측 시뮬레이션 값($53.02\,\text{mV}$)은 이상 이론 수식 값($53.78\,\text{mV}$) 대비 **$-1.4\%$ 오차** 수준에서 매우 잘 부합합니다.
    * **실효 면적비 ($N_{eff}$):** 
      에미터 주변부 효과(periphery effects) 등으로 인해 실효적으로 결합된 면적비는 **$N_{eff} \approx 7.77$**로 수렴합니다. 따라서 향후 BGR 코어 저항 $R_1$ 계산 등 수식 계산 단계에서는 이론치 대신 **실측 시뮬레이션 값($53.02\,\text{mV}$)**을 사용합니다.
  * **온도 의존성 (PTAT 계수):**
    * 온도 스윕 결과 선형적으로 비례하여 상승하는 PTAT 특성을 보였으며, 시뮬레이션상의 실측 **PTAT 온도 계수는 $+0.176\,\text{mV}/^\circ\text{C}$**로 산출되었습니다. (이론 계수인 $\frac{k}{q}\ln(8) \approx 0.179\,\text{mV}/^\circ\text{C}$와 고도로 부합)

---

## 🛠️ 5. BGR Core TC Optimization Simulation (sim/bgr_core_tb.sch)

* **시뮬레이션 파일:** [sim/bgr_core_tb.sch](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/sim/bgr_core_tb.sch)
* **목표:** PTAT 전류 분지와 CTAT 전류 분지의 합전류($I_{total}$) 온도 계수(TC)의 최소점을 찾아 최적의 온도 보상 저항값($R_6 = R_7$) 확정

### 5.1. 테스트벤치 회로 구성
1. **BGR 코어 코어 루프:**
   * PNP 코어 구성 ($QA (m=1)$ / $QB (m=8)$). Emitter를 위로, Base/Collector를 `VGND`에 접지.
   * $R_1$ 저항 (두 Emitter 노드 사이에 직렬 브릿지로 결선, 값 $17.7\,\text{k}\Omega$ 고정).
   * $R_6, R_7$ 저항 (이상적 SPICE 저항 소자 `res.sym` 사용, 값은 파라미터 `{R7_val}`로 정의).
2. **전류 매칭:**
   * 두 브랜치에 이상적인 독립 전류원 $I_0 = 3\,\text{µA}$, $I_1 = 3\,\text{µA}$를 공급하여 각 브랜치 전류를 강제 매칭함.

### 5.2. 측정 및 스윕 파라미터 조건
* **스윕 파라미터:** 저항 파라미터 $R_{val}$을 **$120\,\text{k}\Omega$ (`dc1`)부터 $240\,\text{k}\Omega$ (`dc7`)까지 $20\,\text{k}\Omega$ 간격**으로 스윕.
* **측정 타겟:** $I_{total} = I_{PTAT} + I_{CTAT} = I(R_1) + I(R_6)$ 
* **분석 종류:** 온도 스윕 (`.dc temp -40 125 5`) 연동 루프 시뮬레이션

### 5.3. 시뮬레이션 결과 및 최적 저항값 선정
* **파형 관찰 분석:**
  * 저항값($R_7$)이 증가할수록 CTAT 전류 성분($I_{CTAT} = \frac{V_{BE1}}{R_6}$)의 기여도가 작아집니다. 이에 따라 온도에 비례해 상승하는 PTAT 전류 성분이 전체 전류를 지배하게 되어, $I_{total}$ 파형이 강한 우상향(Positive Slope) 곡선으로 변하는 것을 확인했습니다 (`dc7` 방향).
  * **`dc1` ($R_6 = R_7 = 120\,\text{k}\Omega$) 결과:**
    * 스윕 범위($-40\sim125^\circ\text{C}$) 전체에서 $I_{total}$의 변화량이 단 **$20\,\text{nA}$** ($3.00\,\text{µA} \sim 3.02\,\text{µA}$)에 불과하여 **가장 평탄한 최적의 온도 보상 파형**을 나타내었습니다.
    * 이는 온도 계수(TC) **$\approx 40\,\text{ppm}/^\circ\text{C}$** 수준의 매우 우수한 성능입니다.
* **최적 설계 결정:**
  * BGR Core의 CTAT 저항값은 **$R_6 = R_7 = 120\,\text{k}\Omega$** 부근에서 최적의 TC 특성을 갖습니다.
  * **추가 정밀 튜닝:** 추후 완벽한 포물선 형태의 극점(turnaround point) 매칭을 위해 $100\,\text{k}\Omega \sim 130\,\text{k}\Omega$ 구간에 대해 미세 스윕(Fine Sweep)을 수행하여 더 세밀한 값을 결정할 수 있습니다.

---

## 🛠️ 6. Banba Current-Mode BGR Self-Bias Loop Setup & Verification

* **테스트벤치 파일:** [sim/bgr_core_tb.sch](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/sim/bgr_core_tb.sch)
* **목표:** 이상 전류원이나 외부 강제 소자 없이, 실제 밴드갭처럼 루프 피드백을 형성하여 자율 바이어스(Self-bias) 상태에서 동작 전압 및 전류 매칭을 검증.

### 6.1. 자율 바이어스 이상적 피드백 구성
1. **단방향 PMOS 거울 모사 (Behavioral B-Source):**
   * 양방향 전류 싱크가 가능한 VCCS 대신, 단방향 동작 수식을 갖는 B-source (`B1`, `B2`, `bsource.sym`)을 배치하여 역방향 전류 유입(Degenerate point 고착 원인)을 원천 차단함.
   * `FUNC = "10u * V(V_ctrl) * u(V(V_ctrl))"`
2. **에러 증폭기 피드백 (VCVS):**
   * VCVS (`E1`, `vcvs.sym`)의 증폭도(Gain)를 `1e5`로 상향하여 미세 오차 제거.
   * 입력단으로 `VBE1` 노드와 `net1` 노드의 차전압을 감지하여 출력으로 `V_ctrl` 노드 전압을 자율 조율하게 결선.
3. **스타트업 초기치 설정:**
   * 시뮬레이터가 0V degenerate state(축퇴해)에 수렴하는 현상을 방지하기 위해 `.nodeset v(vbe1)=0.75 v(net1)=0.75 v(v_ctrl)=1.0`을 복원.

### 6.2. 27°C 단일 동작점 (op) 시뮬레이션 결과 검증
* **전압 및 전류 측정 결과:**
  * $V(VBE1) = 777.16\,\text{mV}$ (QA 에미터 전압)
  * $V(net1) = 777.15\,\text{mV}$ (QB 에미터 위 노드 전압)
  * $\Delta V = V(VBE1) - V(net1) = \mathbf{7.64\,\text{µV}}$ (Virtually 0V, 완벽한 전압 매칭 확인)
  * $V(V\_ctrl) = 763.91\,\text{mV}$ ➜ 총 브랜치 공급 전류는 **$7.639\,\text{µA}$**
* **내부 분지 전류 계산:**
  * $I(R_6)$ CTAT 전류: $777.16\,\text{mV} / 180\,\text{k}\Omega \approx \mathbf{4.32\,\text{µA}}$
  * $I(R_1)$ PTAT 전류: $(777.15\,\text{mV} - V_{BE8}(718.36\,\text{mV})) / 17.7\,\text{k}\Omega \approx \mathbf{3.32\,\text{µA}}$
  * 합산 전류: $I_{total} = I(R_1) + I(R_6) \approx \mathbf{7.64\,\text{µA}}$
* **결론:** 합산 전류와 피드백이 공급하는 전류가 완벽히 $7.64\,\text{µA}$로 일치하며, 0V 축퇴 상태를 탈출하여 정상적인 Banba current-mode 활성 영역 동작점에 완벽히 수렴하였습니다.

### 6.3. 자율 바이어스 루프 미세 튜닝 (Fine Sweep) 결과
* **스윕 조건:** $110\,\text{k}\Omega \sim 130\,\text{k}\Omega$ 범위에서 $3\,\text{k}\Omega$ 간격으로 미세 스윕 수행.
* **측정 결과:**
  * **`dc5` ($R_6 = R_7 = 122\,\text{k}\Omega$):** 전체 온도 영역($-40\sim125^\circ\text{C}$)에 걸쳐 합산 전류 $I_{total} \approx 9.68\,\text{µA}$ 선상에서 가장 완벽한 수평(Zero-TC) 곡선 형성.
  * `dc1`~`dc4` ($110\text{k}\sim119\text{k}$): 약한 CTAT 성분(우하향 곡선) 잔존.
  * `dc6`~`dc7` ($125\text{k}\sim128\text{k}$): 약한 PTAT 성분(우상향 곡선) 발현.
* **최종 설계 타겟 확정:**
  * 이상적인 자율 바이어스 루프 상태에서의 최적의 $R_6, R_7$ 값은 **$122\,\text{k}\Omega$** 입니다.
  * **설계 실무 반영:** 실제 Active Cascode PMOS Mirror 소자(`pfet_01v8_lvt`)의 채널 길이 변조 효과 및 레이아웃 상의 **단위 저항(Unit Resistor, e.g. $20\,\text{k}\Omega$ 단위)** 정수배 정합 제약을 고려하여, 이상 소자 상태의 미세 스윕은 본 단계에서 성공적으로 마무리하고 해당 값을 Typical Baseline으로 확정합니다.





