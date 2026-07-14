# BGR Core active mirror NMOS Cascode Verification Results (Milestone 08)

This document summarizes the verification results for the BGR core using the real poly resistor model `sky130_fd_pr__res_high_po_0p69` after adding the NMOS cascode stage (`XM3c/XM4c`) to shield the active mirror and resolve the VAPWR-dependent drain voltage asymmetry.

## 1. 전/후 성능 비교표 (Before vs After Cascode)

| 항목 | cascode 적용 전 | cascode 적용 후 ($N=41$) | 개선 비율 | 비고 |
| :--- | :---: | :---: | :---: | :--- |
| **Line Regulation** | `0.6405 %/V` | **`0.1412 %/V`** | **4.5배 개선** | 스펙 ($<0.5\,\%/V$) 완벽 통과 |
| **등화 오차 VAPWR 의존성** | $-724.8\,\mu\text{V}$ | **$-51.1 \mu\text{V}$** | **14배 개선** | VAPWR 스윕 시 변동량 감소 |
| **등화 오차 (@27°C)** | $-131\,\mu\text{V}$ | **$-8.4 \mu\text{V}$** | **15배 개선** | 드레인 전압 비대칭성 제거 효과 |
| **TC (tt 코너)** | `8.6 ppm/°C` | **`6.1 ppm/°C`** | **개선** | $N=41$ 재최적화 반영 |
| **TC (ss/ff 코너)** | `6.6 / 42.7 ppm/°C` | **`11.2 / 48.5 ppm/°C`** | 전 코너 통과 | 전 코너에서 규격 ($<50$) 유지 |
| **소모 전류 ($I_Q$)** | `55.25 µA` | **`56.41 µA`** | $+1.16\,\mu\text{A}$ 가산 | 신규 bias 분기 추가 소모 |
| **출력 전압 $V_{ref}$ (@27°C, tt)** | `1.20756 V` | **`1.18698 V`** | - | 4-bit 트림 범위 내 위치 |

---

## 2. N 재최적화 (N Re-optimization) 스윕 비교표

등화쌍의 대칭성이 개선되어 오차가 격감함에 따라, PTAT/CTAT의 실효 균형점이 이동하여 최적의 $N$ 유닛 저항 개수를 재탐색하였습니다 (tt 코너 기준).

| 유닛 개수 ($N$) | 실효 저항값 ($R_6, R_7$) | 스키매틱 $L_{total}$ | 온도 계수 (TC) | 판정 |
| :---: | :---: | :---: | :---: | :---: |
| $38$ | $112.10\,\text{k}\Omega$ | $226.526\,\mu\text{m}$ | `90.4 ppm/°C` | FAIL |
| $39$ | $115.05\,\text{k}\Omega$ | $232.531\,\mu\text{m}$ | `58.2 ppm/°C` | FAIL |
| $40$ | $118.00\,\text{k}\Omega$ | $238.534\,\mu\text{m}$ | `27.8 ppm/°C` | PASS |
| **`41` (최적)** | **`120.95 kΩ`** | **`244.537 µm`** | **`6.0 ppm/°C`** | **PASS (최적)** |
| $42$ | $123.90\,\text{k}\Omega$ | $250.540\,\mu\text{m}$ | `35.2 ppm/°C` | PASS |

* **결론:** $N=41$에서 최종 **`6.0 ppm/°C`** (Tcl 수식 교정 반영 시 `6.1 ppm/°C`)의 최적 온도 안정도를 얻었으며, 이를 통해 BGR 코어 사양을 확정하였습니다.

---

## 3. 백업 파일 목록
* [bgr_core_tb.spice](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/08_eqpair_cascode/bgr_core_tb.spice): cascode 추가 및 $N=41$ 최적화 완료 정본 넷리스트
* **fig10_tc_final.png**: $N=41$ 조건에서의 전 코너(tt, ss, ff) 온도 스윕 결과 파형
* **fig11_staircase_final.png**: 최악 기동 코너(ss/-40°C) 및 Typical 기동 과도 해석 파형
* **f_lr.csv**: VAPWR 스윕에 따른 Line Regulation 데이터
* **f_tc_*.csv** 및 **nc38.csv ~ nc42.csv**: 스윕 원본 데이터 아카이브
