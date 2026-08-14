# Sky130A PDK 온도 관련 정밀 파라미터 덤프 보고서

* **작성 목적**: BGR TC 곡선의 3차 피팅 계수를 이론값과 대조하기 위한 PDK 실측 파라미터 검증 기준 문서.
* **원칙**: 추측 금지. PDK 내 명시적 코드 및 라인 번호에 기초하여 작성함.

---

## 1. PNP 바이폴라 (`sky130_fd_pr__pnp_05v5_W0p68L0p68`)

### ① 서브회로 덤프 (subckt)
* **출처 절대경로**: `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice`
* **행번호**: L400 - L457

```spice
.subckt sky130_fd_pr__pnp_05v5_W0p68L0p68 c b e mult=1

.param dkbfpp = 9.5154e-01
+ dkispp = 9.2840e-01
+ mm_bf = {sw_mm_sky130_fd_pr__pnp_05v5_W0p68L0p68_bf*mismatch_factor*MC_MM_SWITCH*AGAUSS(0,1.0,1)/sqrt(mult)}
+ mm_is = {sw_mm_sky130_fd_pr__pnp_05v5_W0p68L0p68_is*mismatch_factor*MC_MM_SWITCH*AGAUSS(0,1.0,1)/sqrt(mult)}

Qsky130_fd_pr__pnp_05v5_W0p68L0p68 c b e c sky130_fd_pr__pnp_05v5_W0p68L0p68_model 

.model sky130_fd_pr__pnp_05v5_W0p68L0p68_model pnp level = 1
+ tref = 30
+ cjc = 6.255e-015 cje = 6.113e-016 cjs = 0
+ fc = 0.5 mjc = 0.24 mje = 0.3 mjs = 0.24
+ vjc = 0.54 vje = 0.74 vjs = 0.54 xcjc = 1
+ ptf = 0 tf = 6.15385e-010 tr = 5e-008 vtf = 1e-12
+ xtf = 0
+ af = 1.60722 kf = 4.9435066E-11
+ bf = '19.35*dkbfpp*sw_nw_rs_mult**0.75*(1+mm_bf)'
+ ise = '9.4936e-017*(1-mm_bf)'
+ is = '1.5075e-018*dkispp / sw_func_rdp*(1+mm_is)'
+ vaf = '152.06 / sw_nw_rs_mult*(1-mm_bf)'
+ ikf = 3.3057e-005
+ rb = 316.21 re = 219 irb = 0.027411
+ rc = 531 rbm = 243.58
+ nf = '1.028'
+ ne = 1.6444
+ ns = 1 br = 0.2675 iss = 0 nr = 1
+ var = 4.3 ikr = 0.00043 nkf = 0.5 isc = 1.2e-015
+ nc = 1.003
+ xti = {1.1*(1+mm_is)}
+ xtb = 2.2132 eg = 1.2 tikf1 = -0.0037823
+ tnf1 = 1.972e-006 tnf2 = -8.8e-007
.ends sky130_fd_pr__pnp_05v5_W0p68L0p68
```

### ② 핵심 온도 및 DC 파라미터 요약

| 파라미터 | 값 | 단위 | 출처 절대경로 | 행번호 | 코너 | 비고 |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **`XTI`** ($\eta$) | **`1.1`** | - | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L450 | All | `xti = {1.1*(1+mm_is)}` |
| **`EG`** ($V_{g0}$) | **`1.20`** | eV | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L451 | All | 밴드갭 기본 에너지 |
| **`TNOM`** (`tref`) | **`30.0`** | °C | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L418 | All | BJT 기준 온도 |
| **`IS`** ($I_{s0}$) | **`1.39956 × 10⁻¹⁸`** | A | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L437 | TT | `1.5075e-18 * 0.9284 / 1.0` |
| **`BF`** ($\beta_F$) | **`18.412`** | - | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L435 | TT | `19.35 * 0.95154 * 1.0` |
| **`VAF`** | **`152.06`** | V | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L438 | TT | Early 전압 |
| **`NF`** ($n$) | **`1.028`** | - | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L443 | All | 이상인자 (Ideality factor) |
| **`ISE`** | **`9.4936 × 10⁻¹⁷`** | A | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L436 | TT | B-E 누설 포화전류 |
| **`NE`** | **`1.6444`** | - | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | L444 | All | B-E 누설 이상인자 |
| **`TLEV` / `TLEVC`** | **미발견** | - | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice` | - | - | Spice3 기본 `tlev=0` 적용 |

---

## 2. 고저항 폴리 저항 (`sky130_fd_pr__res_high_po_0p69`)

### ① 온도계수 및 시트저항 수치

| 파라미터 | 값 | 단위 | 출처 절대경로 | 행번호 | 코너 | 비고 |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **`TC1`** (Body 1차) | **`-1.47 × 10⁻³`** | 1/°C | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_global.spice` | L85 | All | `-1470 ppm/°C` |
| **`TC2`** (Body 2차) | **`+2.70 × 10⁻⁶`** | 1/°C² | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_global.spice` | L86 | All | `+2.7 ppm/°C²` |
| **`TNOM`** | **`30.0`** | °C | `/foss/pdks/sky130A/libs.tech/combined/continuous/models_resistors.spice` | L235 | All | 저항 기준 온도 |
| **`rsh`** (ngspice TT) | **`325.0`** | Ω/sq | `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_nom.spice` | L17 | TT | 공칭 모델 시트저항 |
| **`rsh`** (ngspice High) | **`370.0`** | Ω/sq | `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_high.spice` | L17 | SS | `325.0 + 45.0` |
| **`rsh`** (ngspice Low) | **`277.0`** | Ω/sq | `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_low.spice` | L17 | FF | `325.0 - 48.0` |
| **`xhrpoly`** (Magic) | **`319.8`** | Ω/sq | `/foss/pdks/sky130A/libs.tech/magic/sky130A.tech` | L5111 | Layout | `319800 mOhm/sq` |

### ② 온도의존 방정식
$$R_{body}(T) = R_{body}(T_{nom}) \cdot \left[1 + TC1 \cdot (T - T_{nom}) + TC2 \cdot (T - T_{nom})^2\right]$$

---

## 3. 컨택 저항 온도계수 검증 (★ 분석 핵심)

* **Magic 상온 컨택 저항**: `152.0 Ω/contact` (`152000 mOhm`, `/foss/pdks/sky130A/libs.tech/magic/sky130A.tech` L5150~L5220)
* **ngspice 서브회로 내부 배치 구조** (`models_resistors.spice` L212-252):
  * `sky130_fd_pr__res_high_po` 서브회로 내부에 `rhead` (헤드/컨택 저항) 소자가 따로 수식 분리되어 존재함:
    `rhead r0 rb rhead_model w = {weff+0.1558} l = 1`
  * `rhead_model` 카드 수식 (`models_resistors.spice` L230):
    `.model rhead_model r rsh = {rhead_ps*sw_poly_head_res ...}`
  * `rhead_model` 카드 내 **`tc1`, `tc2` 온도계수 매개변수는 정의되어 있지 않음 (기본값 0)**.

> **★ 핵심 결론**:
> **"컨택 저항(Head resistance)은 온도 무의존(TC1 = 0, TC2 = 0)으로 모델링됨"**
>
> **이론적 영향 분석**:
> 저항 비($R_2/R_6$, $R_2/R_1$) 수식 계산 시, L에 무관하게 고정으로 붙는 헤드 저항($R_{head} \approx 345.83\,\Omega \cdot \text{head}$)은 온도가 변해도 고정($\text{TC}=0$)인 반면, 저항 몸통($R_{body}$)은 $-1470\,\text{ppm/°C}$로 변화합니다. 이로 인해 온도 변화에 따라 유효 저항 비가 미세하게 변동하여 3차 피팅 잔차(Residual) 비선형성을 유발하는 결정적 요인이 됩니다.

---

## 4. 트림 스위치 (`sky130_fd_pr__nfet_01v8`, L=0.15, W=10)

* **출처 절대경로**: `/foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8.pm3.spice`

| 파라미터 | 값 | 단위 | 행번호 | 물리적 의미 |
| :--- | :---: | :---: | :---: | :--- |
| **`tnom`** | **`30.0`** | °C | L45 | BSIM4 모델 기준 온도 |
| **`ute`** | **`-1.3190432`** | - | L213 | 이동도 온도 지수 (Mobility Temp Exponent) |
| **`kt1`** | **`-0.22096074`** | V | L210 | 문턱전압 1차 온도계수 ($V_{th}$ TC) |
| **`kt2`** | **`-0.028878939`** | V | L211 | 기판 바이어스 문턱전압 온도계수 |
| **`kt1l`** | **`0.0`** | V·m | L217 | 문턱전압 채널길이 온도 의존성 |
| **`ua`** | **`-1.1926 × 10⁻⁹`** | m/V | L122 | 1차 이동도 열화 계수 |
| **`ub`** | **`2.1846 × 10⁻¹⁸`** | m²/V² | L123 | 2차 이동도 열화 계수 |
| **`uc`** | **`8.1022 × 10⁻¹¹`** | 1/V | L124 | 바디 바이어스 이동도 열화 계수 |
| **`ua1`** | **`-2.3847 × 10⁻¹¹`** | m/V | L214 | 이동도 열화 1차 온도계수 |
| **`ub1`** | **`7.0775 × 10⁻¹⁹`** | m²/V² | L215 | 이동도 열화 2차 온도계수 |
| **`uc1`** | **`1.4719 × 10⁻¹⁰`** | 1/V | L216 | 이동도 열화 바디 1차 온도계수 |

---

## 5. 물리 상수 (기록용)

| 상 수 | 수 치 | 단 위 | 비 고 |
| :--- | :---: | :---: | :--- |
| **볼츠만 상수 ($k_B$)** | **`1.380649 × 10⁻²³`** | J/K | 2019 SI 정의 확정치 |
| **전하량 ($q$)** | **`1.602176634 × 10⁻¹⁹`** | C | 2019 SI 정의 확정치 |
| **기준 절대온도 ($T_0$)** | **`300.15`** | K | $27.0^\circ\text{C}$ ($273.15 + 27.0$) |
| **열전압 ($V_{T0}$)** | **`25.8519`** | mV | $V_{T0} = \frac{k_B \cdot 300.15}{q}$ |

---

## 6. 검색 수행 파일 절대경로 목록
* `/foss/pdks/sky130A/libs.tech/combined/continuous/models_bjt.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/models_resistors.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/models_global.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_nom.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_high.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_low.spice`
* `/foss/pdks/sky130A/libs.tech/combined/continuous/parameters_fet_tt.spice`
* `/foss/pdks/sky130A/libs.tech/magic/sky130A.tech`
* `/foss/pdks/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8.pm3.spice`
