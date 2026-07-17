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
* **5-bit 저항 트림 회로 내장:** 몬테카를로 실측 3-sigma 산포($\pm 6.6\%$)를 완벽 커버하고 8 ppm/°C 초정밀 성능에 걸맞은 미세 조정을 제공하기 위해, 5-bit 디지털 가변 저항 트림 링크(LSB 해상도 0.44%, 범위 $\pm 7.0\%$, 제어 핀 `ui_in[4:0]`)를 BGR 출력단 저항 사다리($R_2$)에 설계하여 $V_{ref}$ 절대값을 미세 튜닝함. 중앙 코드 `10000`에서 $1.20\text{V}$ 출력을 목표로 고정 저항 $R_2$의 baseline 유닛 길이를 보정함.


#### BGR 설계 목표 스펙
| 스펙 | 목표 | 근거/비고 |
| :--- | :--- | :--- |
| $V_{ref}$ | $1.2\,\text{V}$ | LDO 분압 $R_2=2R_1$ (→ $1.8\,\text{V}$)과 일관 |
| TC ($-40\sim125^\circ\text{C}$) | $< 50\,\text{ppm}/^\circ\text{C}$ (전 코너) | tt: 7.5 ppm/°C, ss: 8.6 ppm/°C, ff: 9.0 ppm/°C (전 코너 균일화 완료) |
| Line regulation | $< 0.5\,\%\text{/V}$ | 0.0840 %/V (실측치, 차폐 및 스케일링 완료) |
| PSRR @DC | $< -40\,\text{dB}$ | cascode + 후단 LDO |
| $I_Q$ (BGR only) | $< 60\,\text{µA}$ | 59.73 µA @tt (실측치) [1] |
| Startup time | $< \text{수 µs}$, 확정 기동 | 축퇴점 회피 |
| Area (BGR only) | $\le 3000\,\text{µm}^2$ | 1x2에 여유 (미스매치 감축을 위한 면적 4배 스케일링 반영) [2] |

`[1] 개정 사유: TC 최적화 분석 결과 브랜치당 ~10µA의 바이어스 전류가 요구됨에 따라 코어2+출력1+bias1 분기 합산 55µA 소모에, Line Reg 개선을 위한 cascode bias 신규 분기(+1.2µA) 및 core 면적 스케일링에 따른 기생 증가(+3.53µA)가 추가되어 총 59.73µA가 소모됨. 소비전력은 197.1µW.`
`[2] 개정 사유: 몬테카를로 분석 결과 로컬 미스매치(MM)의 분산 기여도가 91.5%로 지배적임을 판명하고, Pelgrom 법칙에 근거해 핵심 트랜지스터(XM_top*, XM3/XM4)들의 면적을 4배(W, L 각각 2배씩) 확장하여 약 +960 µm² 면적이 추가 가산됨.`

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
* **LDO 분압 저항비 구성:** 
  * 기준 전압 $V_{ref} = 1.2076\,\text{V}$ 대비 $V_{out} = 1.8\,\text{V}$ 출력을 얻기 위해 피드백 저항 분압기 $R_T$ 및 $R_B$ 결선.
  * $R_T = 40 \times R_u = 118\,\text{k}\Omega$, $R_B = 82 \times R_u = 241.9\,\text{k}\Omega$ 적용 시 $V_{out} = 1.2076 \times (1 + 40/82) \approx 1.7967\,\text{V}$ (약 $1.8\text{V}$, 저항 트림을 통해 정밀 조율).
* **최대 부하 전류 ($I_{load, max}$):** $4\,\text{mA}$ (하드웨어 제약 및 패드 와이어 한계 준수).
* **소모 전류 ($I_Q$, LDO 자체):** $\le 10\,\mu\text{A}$ 목표.

#### LDO 설계 목표 스펙 및 물리적 근거

| 파라미터 | 목표 스펙 | 설계 근거 / 비고 |
| :--- | :---: | :--- |
| **Dropout 전압 ($V_{drop}$)** | $\le 200\,\text{mV}$ | 실구동 조건은 $V_{SD} = 1.5\,\text{V}$로 충분한 Saturation 마진 확보 가능. |
| **Line Regulation** | $\le 2.0\,\text{mV/V}$ | $VAPWR = 3.0\text{V} \sim 3.6\text{V}$ 스윕 기준. EA의 높은 DC Gain으로 억제. |
| **Load Regulation** | $\le 2.0\,\text{mV/mA}$ | $I_{load} = 0 \sim 4\text{mA}$ 기준. 전체 전압 변동 $\Delta V_{out} \le 8\,\text{mV}$ 목표. |
| **PSRR @DC / 1kHz / 100kHz** | $\le -60\,\text{dB} / -50\,\text{dB} / -30\,\text{dB}$ | BGR 출력을 1차 필터링하고 EA 루프 이득 및 Compensation 대역 설계로 제거. |
| **위상 마진 (Phase Margin)** | $\ge 60^\circ$ | 무부하($I_{load}=0$)부터 최대 부하($4\,\text{mA}$) 전 구간 루프 안정성 보장. |
| **Transient Response** | Overshoot/Undershoot $\le 100\,\text{mV}$ | $0 \leftrightarrow 4\,\text{mA}$ Step (엣지 $100\,\text{ns}$), $C_L = 100\,\text{pF}$ 및 복구 시간 $< 5\,\mu\text{s}$. |

#### 2.3.1. Pass Device (PMOS) 사이징 및 기생 커패시턴스 분석
* **소자 종류:** Thick-oxide PMOS (`pfet_g5v0d10v5`)
* **사이징 확정:** **`W = 400 µm / L = 0.5 µm`** (Aspect Ratio $W/L = 800$, Multiplier $M = 20$, Finger $W_f = 20\,\mu\text{m}$)
* **물리적 계산 검증:**
  * Saturation 전류 수식: $I_D = \frac{1}{2} \mu_p C_{ox} \frac{W}{L} V_{ov}^2$
  * $\mu_p C_{ox} \approx 30\,\mu\text{A/V}^2$ 대입 시 $I_{load} = 4\,\text{mA}$ 구동에 필요한 Overdrive 전압:
    $$4000\,\mu\text{A} = \frac{1}{2} \times 30\,\mu\text{A/V}^2 \times 800 \times V_{ov}^2 \implies V_{ov} \approx \mathbf{0.577 V}$$
  * 따라서 최대 부하 시 필요한 게이트 바이어스 전압은 $V_G = V_{APWR} - |V_{thp}| - V_{ov} \approx 3.3 - 0.9 - 0.58 = \mathbf{1.82 V}$로, 3.3V 구동 오차 증폭기의 전압 출력 스윙 범위 내에 여유롭게 들어옵니다.
* **게이트 입력 커패시턴스 ($C_{gg}$) 추정:**
  * 산화막 커패시턴스 $C_{ox} \approx 2.3\,\text{fF/\mu m}^2$ (Gate oxide $t_{ox} \approx 15\,\text{nm}$)
  * 채널 면적 $A_g = W \times L = 400 \times 0.5 = 200\,\mu\text{m}^2$
  * 게이트 커패시턴스: $C_{gg, body} = A_g \times C_{ox} \approx 460\,\text{fF}$
  * 기생 오버랩 및 배선 커패시턴스 합산 시 실효 부하 커패시턴스 **$C_{gg, total} \approx \mathbf{0.5\sim0.6\,\text{pF}}$** (EA의 지배적 출력 극점을 형성).

### 2.4. 오차 증폭기 (Error Amplifier - EA) 설계 방침
* **급전 전압:** $VAPWR$ ($3.3\,\text{V}$).
* **구조 제안:** **PMOS 입력 Folded-Cascode 증폭기**
* **입력 공통모드 범위(ICMR) 검증:**
  * $V_{ref} = 1.2076\,\text{V}$에서 입력 PMOS의 소스 노드 전위는 $V_S = V_G + V_{SG} \approx 1.2 + 0.9 + 0.2 = 2.3\,\text{V}$로 바이어스됩니다.
  * 테일 전류원(Tail current source)에 걸리는 전압은 $V_{APWR} - V_S = 3.3 - 2.3 = 1.0\,\text{V}$로, 테일 소자가 포화 영역에 머물기 위한 전압($V_{ov,tail} \approx 0.2\text{V}$) 대비 5배의 전압 헤드룸을 가집니다. 따라서 PMOS 입력단 설계는 지극히 타당합니다.
* **필요 DC 이득 ($A_{EA}$) 계산:**
  * 목표 Load Regulation 사양인 $\le 2\,\Omega$ ($8\text{mV}/4\text{mA}$) 충족을 위해 필요한 Closed-loop 출력 저항 유도:
    $$R_{out, cl} = \frac{R_{out, ol}}{1 + T} \approx \frac{r_{ds, pass}}{T} \le 2\,\Omega$$
  * Pass 소자의 출력 저항 $r_{ds, pass} \approx 2.5\,\text{k}\Omega$ ($I_D = 4\text{mA}, \lambda \approx 0.1\text{V}^{-1}$) 대입 시 필요한 최소 루프 이득:
    $$T \ge \frac{2500\,\Omega}{2\,\Omega} = 1250\ (\approx \mathbf{62\,\text{dB}})$$
  * 루프 이득 수식 $T = A_{EA} \times A_{pass} \times \beta$ 에서 $A_{pass} = g_{m,pass} r_{ds,pass} \approx 14\text{mS} \times 2.5\text{k}\Omega = 35$ ($31\,\text{dB}$), 피드백 계수 $\beta \approx 0.67$ 대입:
    $$A_{EA} = \frac{1250}{35 \times 0.67} \approx 53.4\ (\approx \mathbf{35.6\,\text{dB}})$$
  * Folded-cascode 토폴로지는 통상 **$60\sim80\,\text{dB}$**의 이득을 제공하므로 스펙 마진을 매우 넉넉하게 만족합니다.

### 2.5. 안정도 및 주파수 보상 사전 분석 (Stability & Compensation)
* **극점 (Poles) 이동 분석 ($C_{load} = 100\,\text{pF}$ 기준):**
  1. **무부하 상태 ($I_{load} \rightarrow 0$):** 피드백 전류 $5\,\mu\text{A}$만 흐를 때, $r_{ds,pass} \approx 2\,\text{M}\Omega$.
     * 출력 저항 $R_{out} \approx 2\,\text{M}\Omega \parallel 360\,\text{k}\Omega \approx 305\,\text{k}\Omega$.
     * 출력 극점 $p_{out, noload} = \frac{1}{2\pi R_{out} C_{load}} \approx \mathbf{5.2\,\text{kHz}}$
  2. **최대 부하 상태 ($I_{load} = 4\,\text{mA}$):** 부하 저항 $R_{load} = 450\,\Omega$.
     * 출력 저항 $R_{out} \approx 450\,\Omega \parallel 2.5\,\text{k}\Omega \approx 380\,\Omega$.
     * 출력 극점 $p_{out, fullload} = \frac{1}{2\pi R_{out} C_{load}} \approx \mathbf{4.19\,\text{MHz}}$ (부하 변동에 의해 극점이 **800배 이상 이동**).
  3. **EA 출력 극점:** $p_{EA} = \frac{1}{2\pi R_{out,EA} C_{gg,pass}} \approx \mathbf{16\,\text{kHz}}$ ($R_{out,EA} \approx 20\,\text{M}\Omega, C_{gg} \approx 0.5\text{pF}$).
* **주파수 보상망 제안 (밀러 보상):**
  * 두 극점($p_{out}, p_{EA}$)이 모두 저주파 대역에 인접해 있어 무보상 시 발진이 불가피합니다.
  * Pass 소자의 게이트-드레인 사이에 밀러 커패시터 $C_c$ 및 우반평면 영점(RHP Zero) 제거용 직렬 영점 저항 $R_z$를 삽입합니다.
  * **밀러 캡 크기 ($C_c$):** **`Cc = 12.8 pF`** (대역폭 확보 및 상온 안정성 마진 극대화).
  * **영점 저항 ($R_z$):** 가벼운 부하 조건에서의 위상 지연을 방지하기 위해 $R_z \approx 1/g_{m,pass} \approx 1\sim5\,\text{k}\Omega$ 수준의 가변 또는 고정 Poly 저항을 배치하여 LHP(Left-Half-Plane)로 영점을 이동 및 보상합니다.

### 2.6. 제어 및 모니터링 인터페이스 (PG / EN)
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

### 6.4. 확정 회로 상태 (Confirmed Circuit State)
Milestone 09 완료 시점 기준, 검증을 통과한 Startup 회로 및 BGR 코어의 확정 소자 사양입니다.

* **BGR 코어 핵심 능동 소자 (미스매치 억제를 위한 4배 스케일링):**
  * `XM_top1/2/5` (PMOS 전류 거울): `pfet_g5v0d10v5` $W = 20.0\,\mu\text{m} / L = 4.0\,\mu\text{m}$ ($mult = 4$)
  * `XM3/XM4` (NMOS 등화쌍): `nfet_g5v0d10v5` $W = 20.0\,\mu\text{m} / L = 4.0\,\mu\text{m}$ ($mult = 2$)
* **BGR 코어 Active Mirror Cascode 및 Bias 회로:**
  * 등화쌍 차폐 Cascode (`XM3c/XM4c`): `nfet_g5v0d10v5` $W = 10.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ ($mult = 2$)
  * Cascode Gate Bias 브랜치:
    * `XM_cn_mir` (상단 PMOS 미러): `pfet_g5v0d10v5` $W = 10.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ ($mult = 1$, 게이트: `V_gate_top`)
    * `XM_cn_d2/d1` (NMOS diode 2단): `nfet_g5v0d10v5` $W = 2.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ ($mult = 1$)
    * `R_cn` (GND 기준 저항): `res_high_po_0p69` $L = 91.5\,\mu\text{m}$ (실효 저항값 $\approx 45.7\,\text{k}\Omega$)
* **Startup 회로 (4소자 최종 사이징):**
  * PMOS 감지단 (`XM_su1a/b/c`): `pfet_g5v0d10v5` $W = 0.42\,\mu\text{m} / L = 20.0\,\mu\text{m}$ 3개 직렬 스택 (게이트: `V_bias_n`, 소스/벌크: `VAPWR`)
  * NMOS 풀다운 (`XM_pd`): `nfet_g5v0d10v5` $W = 12.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ 단일 소자 (게이트: `VBE1` — 감지점)
  * 기동 NMOS 스위치 (`XM_su_n1`): `nfet_g5v0d10v5` $W = 1.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ (게이트: `sense_out`)
  * 전류 제한 NMOS 다이오드 (`XM_su_n2`): `nfet_g5v0d10v5` $W = 1.0\,\mu\text{m} / L = 2.0\,\mu\text{m}$ (다이오드 결선)
* **스키매틱-레이아웃 이원화 설계 방침:**
  * **방침:** "스키매틱 = 단일 심볼(보정 L), 레이아웃 = 2.95k 유닛 (W0.69/L2.79) 어레이, LVS 는 저항값 매칭"
  * **보정 L 계산 수식:**
    * $W = 0.69\,\mu\text{m}$ 기준 ($R_{sheet} = 491.36\,\Omega/\mu\text{m}$, $R_{con} = 389.90\,\Omega$, $L_{unit} = 4.416\,\mu\text{m}$):
      $$L_{total} = N \times 4.416 + (2N - 2) \times 0.79351\,\text{[µm]}$$
    * **$R_1$** (PTAT, 6 유닛): $L_{total} = \mathbf{34.431\,\mu\text{m}}$ ($17.70\,\text{k}\Omega$)
    * **$R_6, R_7$** (CTAT, 41 유닛 - **N=41 최적화**): $L_{total} = \mathbf{244.537\,\mu\text{m}}$ ($120.95\,\text{k}\Omega$)
    * **$R_2$** (Output, 41 유닛): $L_{total} = \mathbf{244.537\,\mu\text{m}}$ ($120.95\,\text{k}\Omega$)
  * **스위치 단락 제약:** 직렬 트림 스택 단락 오차 1% 미만 조건 충족을 위해 스위치 $\frac{W}{L} \ge 860$ ($W = 430\,\mu\text{m} / L = 0.5\,\mu\text{m}$) 설계 적용.

### 6.5. 몬테카를로 분석 및 면적 스케일링 결과 (Monte Carlo & Area Scaling)
* **목표:** 기준 전압 $V_{ref}$의 절대값 3-sigma 산포를 감축하기 위해 오프셋의 지배 성분을 정밀 분석하고 소자 면적 스케일링을 수행.
* **진단 요약 (20 samples):**
  * 로컬 미스매치(MM)의 단독 산포가 $\sigma = 4.58\%$ (분산 기여율 $91.5\%$)로 가장 지배적임을 파악.
  * 글로벌 공정 변이(PR) 단독 산포는 $\sigma = 1.38\%$ (기여율 $8.5\%$)로 매우 작아 Banba 저항비 구조의 대칭성 강점이 재입증됨.
* **면적 스케일링 처방:**
  * Pelgrom 법칙($\sigma_{Vth} \propto 1/\sqrt{WL}$)에 근거하여 전류 정확도를 결정하는 `XM_top*` (PMOS 미러) 및 `XM3/XM4` (NMOS 등화쌍)의 면적($W \cdot L$)을 4배로 확장하여 미스매치를 절반 수준으로 억제.
  * $W/L$ 종횡비를 유지함으로써 $V_{ov}$, 바이어스 전류 및 동작점을 보존하면서 오프셋 산포 성능만 안전하게 개선함. (스케일링 후 3-sigma 산포 재측정 중).

---

## 📝 7. To-Do / Open Issues (확인필요 사항)

* [x] **[Step 2.7] 실저항 소자 교체 및 특성 재스윕:**
  * 실물 저항 교체 및 $N=41$ 최적화로 $6.1\,\text{ppm}/^\circ\text{C}$ 확보 완료.
* [x] **[Step 2.8] BGR 몬테카를로 재실행 및 트림 설계 확정:**
  * 면적 스케일업 회로에 대한 몬테카를로 산포 재실측 완료 ($\sigma = 2.21\%$).
  * 3-sigma 산포 $\pm 6.6\%$ 수렴을 위한 5-bit 디지털 트림(LSB 스텝 0.44%, 범위 $\pm 7.0\%$, 제어 핀 `ui_in[4:0]`) 규격 확정.
  * Typical 중심점 오프셋 보상을 위해 고정 저항 $R_2$의 baseline 크기 미세 보정 (41 유닛 $\rightarrow$ 41.3 유닛 등가 길이 보정) 사양 확정 완료.
* [ ] **[Step 2.9] LDO 오차 증폭기(EA) 연동 및 보상망 설계:**
  * PMOS 입력 Folded-Cascode 증폭기 및 Miller 보상 커패시터($C_c = 12.8\,\text{pF}$), 영점 제거 저항($R_z$) 상세 설계.

---

## LDO (v7~)
LDO 레귤레이터 설계 및 통합 단계에 대한 사양과 결정 사항을 이 섹션 이하에 기록합니다.




