# sky130A 코너 구조 정본 — 저항·FET·캡 독립성

**작성 근거**: `sky130.lib.spice` 및 `continuous/parameters_*.spice` 직접 grep (전 섹션 전수)
**대체 대상**: `03_PDK_환경.md` §저항 코너 구조 (`corner_factor` 메커니즘) — 해당 절 폐기

---

# 0. 요약 — 기존 서술의 오류 2건

| # | 기존 서술 (`03_PDK_환경`) | 실제 |
| ---: | :--- | :--- |
| 1 | `res_high_po_rs = {325.0 + corner_factor × 45.0}` | **`res_nom`은 `× 0.0`.** `× 45.0`은 `res_high` 파일 |
| 2 | "저항 코너는 독립 설정되지 않고 **트랜지스터 코너에 종속**" | **완전히 독립.** `ss_ll`·`ff_hh` 같은 조합 섹션이 명시적으로 존재 |

**`corner_factor`는 전 섹션에서 `1`로 고정**입니다. 코너를 결정하는 것은 **어느 `parameters_*.spice`를 include하는가**입니다.

---

# 1. 저항 파라미터 파일 3종 (실측)

`sw_sky130_fd_pr__res_high_po_rs`와 `sw_poly_head_res` 기준:

| 파일 | 시트 수식 | 시트 값 | head 배율 수식 | head 배율 |
| :--- | :--- | ---: | :--- | ---: |
| `parameters_res_nom.spice` | `{325.0 + cf*0.0}` | **325.0** Ω/□ | `{1.0 + cf*0.0}` | **1.000** |
| `parameters_res_low.spice` | `{325.0 + cf*(-48.0)}` | **277.0** | `{1.0 + cf*(-0.125)}` | **0.875** |
| `parameters_res_high.spice` | `{325.0 + cf*45.0}` | **370.0** | `{1.0 + cf*0.125}` | **1.125** |

*(`cf` = `corner_factor` = 1)*

**★ body와 head의 변동률이 다릅니다.**

| | body | head |
| :--- | ---: | ---: |
| `low` / `nom` | **−14.77 %** | **−12.5 %** |
| `high` / `nom` | **+13.85 %** | **+12.5 %** |

이 차이가 §4의 2차 효과를 만듭니다.

## 1.1 MC 항

세 파일 모두 동일한 형태로 PR 항을 갖습니다:

```
+ process_mc_factor * MC_PR_SWITCH * GAUSS(0, 0.035, 1)    ← 시트, σ 3.5 %
+ process_mc_factor * MC_PR_SWITCH * GAUSS(0, 0.025, 1)    ← head, σ 2.5 %
```

`MC_PR_SWITCH = 0`이면 항이 사라집니다. 즉 **`_mm` 섹션(PR=0)에서는 저항 산포가 전혀 없습니다.**

---

# 2. 섹션 → 파일 매핑 (전수)

## 2.1 규칙

| 섹션 접미사 | 저항 파일 | 캡 파일 |
| :--- | :--- | :--- |
| 없음 | `res_nom` | `cap_nom` |
| `_ll` · `_lh` | **`res_low`** | `cap_low` |
| `_hh` · `_hl` | **`res_high`** | `cap_high` |

FET 코너는 별도 접두사(`tt`/`ss`/`ff`/`sf`/`fs`)로 정해집니다.

## 2.2 실측 목록

```
tt  sf  ff  ss  fs                      → res_nom
ll  lh                                  → res_low
hh  hl                                  → res_high
ss_ll  ss_lh  sf_ll  fs_ll  fs_lh
ff_ll  ff_lh                            → res_low
ss_hl  ss_hh  sf_hl  sf_hh  fs_hl
fs_hh  ff_hl  ff_hh                     → res_high
mc                                      → res_nom
```

각 섹션에 `_mm` 변형이 존재하며 매핑은 동일합니다(`tt_mm` → `res_nom`, `ll_mm` → `res_low` 등).

## 2.3 MC 스위치

| 섹션 | `MC_MM_SWITCH` | `MC_PR_SWITCH` |
| :--- | ---: | ---: |
| 기본 (`tt`, `ss`, `ff`, `ll`, `hh`, …) | **0** | **0** |
| `_mm` 변형 (`tt_mm`, `ll_mm`, …) | **1** | **0** |

**`_mm`은 mismatch만 켭니다. PR은 어느 섹션도 자동으로 켜지지 않습니다.**

PR을 켜려면 `.lib` 뒤에 직접 주입해야 합니다:

```spice
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.param MC_MM_SWITCH=1
.param MC_PR_SWITCH=1
```

---

# 3. ★ FET 코너 스윕만으로는 저항 산포가 안 잡힙니다

$$\texttt{tt} \cdot \texttt{ss} \cdot \texttt{ff} \;\Rightarrow\; \text{전부 } \texttt{res\_nom} \;\Rightarrow\; \text{폴리 시트 } 325.0\ \Omega/\square \text{ 동일}$$

FET 코너만 돌리면 **저항은 전혀 변하지 않습니다.**

저항 산포를 보려면 두 방법 중 하나입니다:

| 방법 | 예 |
| :--- | :--- |
| 조합 섹션 사용 | `ff_hh`, `ss_ll`, `sf_hl` … |
| PR MC 켜기 | `.lib tt` + `MC_PR_SWITCH=1` (σ 3.5 % 시트, 2.5 % head) |

---

# 4. BGR에 대한 함의

## 4.1 1차 — 비 상쇄

$$V_{\text{ref}} = \frac{R_2}{R_7}V_{BE1} + \frac{R_2}{R_1}\Delta V_{BE}$$

시트가 모든 저항에 동일하게 곱해지므로 **비에서 1차 상쇄**됩니다. 이것이 비율계량 구조의 강인성입니다.

**FET 코너 간에는 시트가 아예 불변**이므로(§3) 상쇄를 논할 필요조차 없습니다.

## 4.2 ★ 2차 — head/body 변동률 차이

$$R = K\ell \cdot f_{\text{body}} + H \cdot f_{\text{head}}, \qquad f_{\text{body}} \neq f_{\text{head}}$$

| | body | head | 차이 |
| :--- | ---: | ---: | ---: |
| `low` | 0.8523 | 0.875 | **+2.7 %p** |
| `high` | 1.1385 | 1.125 | **−1.4 %p** |

head 분율이 저항마다 다르므로 유효 저항비가 코너에 따라 드리프트합니다.

**head 분율** (30 °C, `res_nom` 기준, $K = 471.698$ Ω/µm, $H = 525.88$ Ω)

| 저항 | $\ell$ (µm) | head 분율 |
| :--- | ---: | ---: |
| $R_1$ | 34.29 | **3.149 %** |
| $R_7$ (×2 직렬) | 121.73 | 0.908 % |
| $R_2$ | 247.37 | 0.449 % |

$k_2 = R_2/R_1$이 가장 민감합니다($R_1$의 head 분율이 7배 큼).

**추정 크기** (`low` 기준, 1차 근사)

$$\frac{\Delta k_2}{k_2} \approx (0.03149 - 0.00449)\times\left(\frac{0.875}{0.8523}-1\right) = 2.70\times10^{-2} \times 2.66\times10^{-2} \approx 7.2\times10^{-4}$$

**약 0.07 %.** 트림 LSB(0.89 %)의 8 %라 트림 창 위치에는 영향이 작습니다.

**★ 다만 TC에는 별개로 작용합니다.** head와 body의 온도계수가 다르고(§5), 코너에 따라 그 비중이 바뀌므로 TC가 달라집니다.

## 4.3 `ll` 코너에서 측정한 TC를 인용하면 안 됩니다

`ll_mm`은 저항 −14.8 % + head 배율 0.875입니다. head/body 비가 바뀌어 TC가 달라집니다. startup 판정에는 무관하나, **TC 수치를 `ll`에서 가져오면 안 됩니다.**

---

# 5. head/body 온도계수 (별도 실측)

시트와 무관하게, head와 body는 **온도계수 자체가 다릅니다.**

6점 실측(L = 1, 10, 34.29, 50, 121.73, 243.46, `tt`, −40…125 °C):

| L (µm) | R (−37.5 °C) | 국소 tc |
| ---: | ---: | ---: |
| 1 | 980 | **209.6** ppm/°C |
| 10 | 5,102 | 330.9 |
| 34.29 | 16,226 | 350.7 |
| 50 | 23,420 | 353.5 |
| 121.73 | 56,270 | 357.2 |
| 243.46 | 112,017 | **358.5** |

**1.71배 변동.** 2성분 피팅 RMS **0.000 ppm/°C**.

$$\text{tc}_{\text{eff}}(R) = \text{TC}_{\text{body}} - \frac{(\text{TC}_{\text{body}}-\text{TC}_{\text{head}})R_{\text{head}}}{R}$$

| 기준 | $\text{TC}_{\text{body}}$ | $\text{TC}_{\text{head}}$ | 비 |
| :--- | ---: | ---: | ---: |
| −37.5 °C 국소 (본 측정) | 359.8 | 79.7 | **4.51** |
| 30 °C (기존 문서) | 545.3 | 120.6 | **4.52** |

기준 온도가 달라 절대값 비교는 불가하나 **비가 일치**하여 구조가 확인됩니다.

**★ `tc1sky130_fd_pr__res_generic_pobody = −1.47e−3`(`models_global.spice` L85)은 `res_high_po`에 적용되지 않습니다.** 실측은 양수이고 부호부터 반대입니다. 이름이 유사한 다른 저항용입니다.

---

# 6. 기존 문서 정정 항목

## 6.1 `03_PDK_환경` §저항 코너 구조 — 폐기

```
[폐기] sw_sky130_fd_pr__res_high_po_rs = {325.0 + corner_factor × 45.0}
[폐기] 저항 코너는 독립 설정되지 않고 트랜지스터 코너에 종속
[재측정] ff 122.18 kΩ / tt 115.75 / ss 113.93 (스프레드 +6.8%)
```

**마지막 항목이 중요합니다.** `tt`·`ss`·`ff`가 모두 `res_nom`을 include하므로 **폴리 저항은 세 코너에서 동일**합니다. 6.8 % 스프레드는 저항 변동이 아닙니다.

회로 내 $V/I$로 유도한 값이라면 저항이 아니라 동작점 변화를 반영한 것입니다. **재측정 필요.**

**단 "비율계량이 PDK 모델 레벨에서 구조적으로 보증된다"는 결론은 유효하며 오히려 강화됩니다.**

## 6.2 Antigravity `pdk_temp_params.md` 정정

```
[오류] rsh: 325.0 Ω/sq (TT) / 370.0 (SS) / 277.0 (FF)
[정정] res_nom 325.0 / res_high 370.0 / res_low 277.0
       — 코너 이름이 아니라 파일 이름. TT·SS·FF 는 전부 res_nom(325.0)
```

## 6.3 `01_BGR_최종스펙` §1 MC 행

조건 병기 추가:

```
코너 tt (FET typical + res_nom) / MC_MM_SWITCH=1 + MC_PR_SWITCH=1 (직접 주입)
N=100 / 27 °C (.temp 없음, ngspice 기본값) / seed: set rndseed = i×7919
```

---

# 부록 A. 확인 명령

## A.1 저항 파일 3종 대조

```bash
docker exec <컨테이너> bash -c 'for f in nom low high; do
  echo "=== res_$f"
  grep -n "res_high_po_rs\|poly_head_res" \
    /foss/pdks/sky130A/libs.tech/combined/continuous/parameters_res_$f.spice
done'
```

## A.2 섹션 → 파일 매핑 전수

```bash
docker exec <컨테이너> bash -c 'python3 - <<PYEOF
import re
lines = open("/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice", errors="replace").read().splitlines()
cur = None
for l in lines:
    m = re.match(r"^[ \t]*\.lib[ \t]+(\S+)[ \t]*$", l, re.I)
    if m: cur = m.group(1); continue
    if re.match(r"^[ \t]*\.endl", l, re.I): cur = None; continue
    if cur and "parameters_res_" in l:
        print("  %-10s %s" % (cur, l.strip().split("/")[-1]))
PYEOF'
```

★ `.endl`까지만 읽어야 합니다. `sed n+20` 방식은 인접 섹션을 긁어옵니다 — 실제로 이 오류로 `tt_mm`과 `ll_mm`이 동일하다는 잘못된 결론에 도달한 적이 있습니다.

## A.3 섹션의 MC 스위치

```bash
docker exec <컨테이너> bash -c 'python3 - <<PYEOF
import re
lines = open("/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice", errors="replace").read().splitlines()
for sec in ("tt", "tt_mm", "ll_mm"):
    print("===== .lib %s" % sec)
    on = False
    for l in lines:
        if re.match(r"^[ \t]*\.lib[ \t]+%s[ \t]*$" % re.escape(sec), l, re.I):
            on = True; continue
        if on and re.match(r"^[ \t]*\.endl", l, re.I): break
        if on and re.search(r"\.param|\.include", l, re.I):
            print("   " + l.strip())
PYEOF'
```

## A.4 저항 $R(T)$ 다점 실측 (§5 근거)

```spice
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
V1 a1 0 1
XR1 a1 0 0 sky130_fd_pr__res_high_po_0p69 L=1 mult=1
... (L = 1, 10, 34.29, 50, 121.73, 243.46)
.dc temp -40 125 5
.control
run
wrdata res6.dat i(v1) i(v2) i(v3) i(v4) i(v5) i(v6)
.endc
```

$R = 1/|I|$ 환산 후 $\text{tc}_{\text{eff}}$를 $1/R$에 선형 회귀 → head/body 분리.

**★ 2점으로는 검증 불가.** 파라미터가 2개이므로 자유도 0. 최소 4점, 권장 6점.

---

# 부록 B. 이 문서가 나오게 된 경위 — 오류 연쇄

| # | 오류 | 발견 경로 |
| ---: | :--- | :--- |
| 1 | 저항 2점 tc를 "0.2 % 일치"로 **계산 없이 단정** | 기존 2성분 모델과 충돌 지적 |
| 2 | 그 위에서 "폴리 TC 기여 정확히 0 %" 결론 → 작업 가설 **오기각** | 〃 |
| 3 | `sed n+20`으로 섹션 덤프 → 인접 섹션 혼입 → `tt_mm`·`ll_mm` 동일 오판 | `corner_factor` 값이 전 섹션 동일해 의심 |
| 4 | `03_PDK_환경`의 `× 45.0` 수식을 그대로 신뢰 | `res_nom` 직접 grep |
| 5 | Antigravity의 `370(SS)/277(FF)` 라벨 오류 | 파일별 대조 |

**공통 교훈**

- "일치/불일치" 판정은 **반드시 수치를 출력**한다
- 기존 결론과 충돌하면 **양쪽을 같은 방법으로 재측정**한다
- PDK 파라미터를 **이름으로 추정하지 않는다** — 소자를 직접 시뮬해 실측한다
- 섹션 덤프는 **`.endl` 경계를 지킨다**
