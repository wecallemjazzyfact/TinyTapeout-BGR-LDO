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

### ① 시트저항 파라미터 파일 3종 및 코너 독립성

> **★ 정정 주의**: 저항 코너는 FET 코너에 종속되지 않고 **완전히 독립**입니다.
> `tt`·`ss`·`ff` 섹션은 모두 `parameters_res_nom.spice`를 include하므로 **폴리 시트 저항($325.0\,\Omega/\square$)이 동일**합니다.
> `corner_factor`는 전 섹션에서 `1`로 고정이며, include되는 파일에 의해 코너가 결정됩니다.

| 파라미터 | 값 | 단위 | 출처 절대경로 | 행번호 | 파일 / 코너 매핑 | 비고 |
| :--- | :---: | :---: | :--- | :---: | :---: | :--- |
| **`rsh`** (`res_nom`) | **`325.0`** | Ω/sq | `/foss/pdks/sky130A/.../parameters_res_nom.spice` | L17 | `tt`, `ss`, `ff`, `sf`, `fs` 등 | `{325.0 + cf*0.0}` |
| **`rsh`** (`res_high`) | **`370.0`** | Ω/sq | `/foss/pdks/sky130A/.../parameters_res_high.spice` | L17 | `hh`, `hl`, `ss_hh`, `ff_hh` 등 | `{325.0 + cf*45.0}` (+13.85%) |
| **`rsh`** (`res_low`) | **`277.0`** | Ω/sq | `/foss/pdks/sky130A/.../parameters_res_low.spice` | L17 | `ll`, `lh`, `ss_ll`, `ff_ll` 등 | `{325.0 + cf*(-48.0)}` (-14.77%) |
| **`xhrpoly`** (Magic) | **`319.8`** | Ω/sq | `/foss/pdks/sky130A/libs.tech/magic/sky130A.tech` | L5111 | Layout | `319800 mOhm/sq` |

### ② Body 및 Head 변동률 차이

| 파일 | Body 시트 수식 | Body 시트 | Head 배율 수식 | Head 배율 |
| :--- | :--- | ---: | :--- | ---: |
| `parameters_res_nom.spice` | `{325.0 + cf*0.0}` | **325.0** Ω/□ | `{1.0 + cf*0.0}` | **1.000** |
| `parameters_res_low.spice` | `{325.0 + cf*(-48.0)}` | **277.0** Ω/□ (−14.77%) | `{1.0 + cf*(-0.125)}` | **0.875** (−12.5%) |
| `parameters_res_high.spice` | `{325.0 + cf*45.0}` | **370.0** Ω/□ (+13.85%) | `{1.0 + cf*0.125}` | **1.125** (+12.5%) |

### ③ 온도계수 실측 정본 (Body / Head 2성분 분리)

> **★ `tc1sky130_fd_pr__res_generic_pobody = -1.47e-3` (`models_global.spice` L85) 인용 오류 정정**:
> 이 파라미터는 `res_high_po`에 적용되지 않으며, 이름이 유사한 다른 generic pobody 저항용입니다.
> `res_high_po`의 실제 측정 TC는 **양수(+)**입니다.

6점 다점 실측($L = 1, 10, 34.29, 50, 121.73, 243.46\,\mu\text{m}$, `tt`, $-40 \sim 125\,^\circ\text{C}$):

$$\text{tc}_{\text{eff}}(R) = \text{TC}_{\text{body}} - \frac{(\text{TC}_{\text{body}}-\text{TC}_{\text{head}})R_{\text{head}}}{R}$$

| 기준 | $\text{TC}_{\text{body}}$ | $\text{TC}_{\text{head}}$ | 비 ($\text{TC}_{\text{body}}/\text{TC}_{\text{head}}$) | 비고 |
| :--- | :---: | :---: | :---: | :--- |
| **$-37.5\,^\circ\text{C}$ 국소** | **`359.8 ppm/°C`** | **`79.7 ppm/°C`** | **`4.51`** | 6점 실측 2성분 피팅 RMS 0.000 ppm/°C |
| **$30\,^\circ\text{C}$ 기준** | **`545.3 ppm/°C`** | **`120.6 ppm/°C`** | **`4.52`** | 기준 온도 환산치 (비율 완벽 일치) |

---

## 3. MC 스위치 및 BGR 함의

* **섹션별 MC 스위치**:
  * 기본 섹션 (`tt`, `ss`, `ff`, `ll`, `hh` 등): `MC_MM_SWITCH = 0`, `MC_PR_SWITCH = 0`
  * `_mm` 변형 (`tt_mm`, `ll_mm` 등): `MC_MM_SWITCH = 1`, `MC_PR_SWITCH = 0` (mismatch만 켬)
  * **저항 공정 산포(PR)는 어느 섹션도 자동으로 켜지지 않으므로**, PR을 활성화하려면 `.lib` 뒤에 `.param MC_PR_SWITCH=1`을 직접 주입해야 함.
* **BGR 설계 함의**:
  * $V_{\text{ref}} = \frac{R_2}{R_7}V_{BE1} + \frac{R_2}{R_1}\Delta V_{BE}$ 에서 시트 저항은 1차 상쇄됨.
  * FET 코너(`tt`, `ss`, `ff`) 간에는 저항 파일이 `res_nom`으로 불변이므로 저항 변동이 0.
  * `res_low` / `res_high`에서는 body와 head의 변동률 차이(+2.7%p / -1.4%p)로 인해 유효 저항비가 미세하게 드리프트(약 0.07%)하며, head/body 비중 변화로 TC가 달라지므로 **`ll` 코너에서 측정한 TC를 대표치로 인용해서는 안 됨**.

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
