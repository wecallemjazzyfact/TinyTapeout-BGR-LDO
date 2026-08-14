# Real Resistor Sizing and N Sweep Verification Results (Milestone 07)

This document summarizes the verification results for the BGR core using the real poly resistor model `sky130_fd_pr__res_high_po_0p69` with $W = 0.69\,\mu\text{m}$.

## 1. 확정 설계 파라미터 (Final Sizing)
* **단위 저항 ($R_u$):** $W = 0.69\,\mu\text{m}$, $L = 4.416\,\mu\text{m}$ ($R_u \approx 2.95\,\text{k}\Omega$)
* **$R_1$** (PTAT): $34.431\,\mu\text{m}$ (6 units 직렬 등가)
* **$R_6, R_7$** (CTAT): $238.534\,\mu\text{m}$ (40 units 직렬 등가, $118.0\,\text{k}\Omega$)
* **$R_2$** (Output): $244.537\,\mu\text{m}$ (41 units 직렬 등가, $120.95\,\text{k}\Omega$)

---

## 2. 시뮬레이션 결과 요약 (N=40 기준)

| 코너 | 출력 전압 $V_{ref}$ (@27°C) | 소모 전류 $I_Q$ (@27°C) | 브랜치 전류 $I_{branch}$ | 온도 계수 (TC, $-40\sim125^\circ\text{C}$) | 판정 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **tt** | `1.2076 V` (목표 대비 +0.63%) | `55.25 µA` | `10.43 µA` | **`8.6 ppm/°C`** | **PASS** |
| **ss** | `1.2086 V` | `48.24 µA` | `8.96 µA` | **`6.6 ppm/°C`** | **PASS** |
| **ff** | `1.2576 V` | `71.21 µA` | `13.56 µA` | **`42.7 ppm/°C`** | **PASS** |

> [!NOTE]
> **비대칭 코너 스프레드 분석:**
> ss와 tt 코너는 상온 기준 `1.208V` 근처에 매우 가깝게 정렬되어 있으나, ff 코너는 `1.2576V`로 약 **`+50 mV` (+4.1%)** 위로 튀는 강한 비대칭 분포를 보입니다. 
> 이에 따라 트림 범위는 대칭형 $\pm 5\%$가 아닌, **아래쪽으로 큰 폭($-5\%$)**을 흡수할 수 있는 비대칭 트림 설계($-50\,\text{mV} \sim +10\,\text{mV}$)가 요구됩니다. (ff 코너를 $1.2\text{V}$로 끌어내리는 것이 주요 임무가 됩니다.)

---

## 3. N 스윕 온도 계수 (TC) 비교표

CTAT 저항 $R_6, R_7$의 직렬 유닛 개수 $N$을 39부터 43까지 스윕한 결과입니다 (tt 코너 기준).

| 유닛 개수 ($N$) | 실효 저항값 ($R_6, R_7$) | 스키매틱 $L_{total}$ | 온도 계수 (TC) | 판정 |
| :---: | :---: | :---: | :---: | :---: |
| $39$ | $115.05\,\text{k}\Omega$ | $232.531\,\mu\text{m}$ | `33.1 ppm/°C` | PASS |
| **`40` (최적)** | **`118.00 kΩ`** | **`238.534 µm`** | **`8.6 ppm/°C`** | **PASS (최적)** |
| $41$ | $120.95\,\text{k}\Omega$ | $244.537\,\mu\text{m}$ | `31.2 ppm/°C` | PASS |
| $42$ | $123.90\,\text{k}\Omega$ | $250.540\,\mu\text{m}$ | `62.1 ppm/°C` | FAIL (TC > 50) |
| $43$ | $126.85\,\text{k}\Omega$ | $256.543\,\mu\text{m}$ | `92.5 ppm/°C` | FAIL |

* **분석:** $N=40$을 중심으로 양방향으로 대칭적으로 오차가 급격히 벌어지는 포물선 형태의 수렴 특성을 나타냅니다. 따라서 최적의 온도 계수 지점으로 **$N=40$**을 확정하였습니다.

---

## 4. 백업 파일 목록
* [bgr_core_tb.spice](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/07_real_resistors/bgr_core_tb.spice): 실물 저항 교체 정본 넷리스트
* **fig5_nsweep_realres.png**: N 스윕에 따른 전압 특성 파형
* **fig6_tc_N40_tt.png**: N=40 최적 조건 tt 코너 상세 파형
* **fig7_tc_corners_real.png**: N=40 기준 전 코너(tt, ss, ff) Vref vs 온도 파형
* **final_tc_*.csv** 및 **n39_tc.csv ~ n43_tc.csv**: 스윕 데이터 추출 파일
