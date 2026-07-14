# BGR Core active mirror & equalizing pair Area Scaling (Milestone 09)

This document summarizes the final verification results of the BGR core after the selective transistor area scaling (v6) under real poly resistors and active NMOS cascode shielding.

## 1. BGR 코어 최종 확정 스펙 비교표

| 항목 | 설계 목표 | 최종 실측치 (v6) | 동작 조건 | 결과 및 평가 |
| :--- | :---: | :---: | :---: | :--- |
| **기준 출력 전압 ($V_{ref}$)** | `1.2 V` (트림 후) | **`1.18659 V`** | tt 코너, 상온, 트림 전 | **PASS** (4-bit 디지털 트림으로 1.2V 보정 예정) |
| **온도 안정도 (TC)** | `< 50 ppm/°C` | **`7.5 / 8.6 / 9.0 ppm/°C`** | tt / ss / ff 코너 ($-40\sim125^\circ\text{C}$) | **PASS** (전 코너에서 극도로 균일한 TC 달성) |
| **Line Regulation** | `< 0.5 %/V` | **`0.0840 %/V`** | tt 코너, VAPWR $3.0\text{V} \sim 3.6\text{V}$ | **PASS** (스펙 대비 6배 이상 우수한 감도 달성) |
| **소모 전류 ($I_Q$)** | `< 60 µA` | **`59.73 µA`** | tt 코너, 상온 | **PASS** (소비전력: `197 µW` @3.3V) |
| **몬테카를로 산포 ($\sigma$)** | — | **`2.21 %`** (3-sigma: $\pm 6.6\%$) | 100 samples (MM+PR 동시 적용) | **1.8배 개선** (스케일링 전 $\sigma = 4.0\%$) |
| **스타트업 기동** | 전 코너 정상 기동 | **PASS** | tt, ss/-40°C 및 staircase/slow-ramp 테스트 | **PASS** (누설 전류: tt `33 fA`, ss-40 `0.026 fA`) |

> **[핵심 특기 사항] ff 코너 온도 안정도 극적 개선**
> 면적 스케일링을 통해 채널 길이 $L$이 $2\,\mu\text{m} \rightarrow 4\,\mu\text{m}$로 늘어나면서, 빠른 소자 코너(ff)의 채널 길이 변조 효과 취약성이 해소되었습니다. 그 결과 ff 코너의 TC가 기존 **`48.5 ppm/°C`에서 `9.0 ppm/°C`로 격감**하였으며, 전 코너 TC가 **`7.5 ~ 9.0 ppm/°C`** 범위 내에서 균일하게 정렬되었습니다 (코너 편차 소멸).

---

## 2. 설계 여정 단계별 핵심 검증 그래프 매핑

본 프로젝트에서 확보된 주요 시뮬레이션 그래프들은 BGR 코어의 각 진화 단계(v1 ~ v6)를 입증하는 강력한 근거입니다.

### [그림 1] [N Sweep 온도 정합 (fig5_nsweep_realres.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig5_nsweep_realres.png)
* **증거 단계:** **v4 (실물 저항 최적화)**
* **설명:** 실물 poly 저항 교체 상태에서 CTAT 저항 유닛 수 $N$을 스윕하여 PTAT/CTAT 전류 균형 지점(최적 turnaround point)을 튜닝하는 곡선군입니다. 이 결과를 토대로 최적의 보상점인 $N=41$을 확정하였습니다.

### [그림 2] [Line Regulation 특성 개선 (fig9_power_linereg.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig9_power_linereg.png)
* **증거 단계:** **v5 (등화쌍 cascode 차폐) & v6 (면적 스케일링)**
* **설명:** VAPWR 공급 전압을 3.0V에서 3.6V까지 스윕할 때 BGR 출력 $V_{ref}$의 변동이 차폐 cascode 구조와 채널 길이 $L=4\,\mu\text{m}$ 스케일러블 조합에 의해 **`0.0840 %/V`** 수준으로 견고하게 억제되는 거동을 나타냅니다.

### [그림 3] [최종 전 코너 온도 안정도 (fig12_tc_area.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig12_tc_area.png)
* **증거 단계:** **v6 (면적 스케일링 최종)**
* **설명:** 면적 4배 스케일링 및 $N=41$ 튜닝이 최종 완료된 상태에서의 전 코너(tt, ss, ff) 온도 스윕($-40\sim125^\circ\text{C}$) 파형입니다. 빠른 코너(ff)의 $r_o$ 개선 효과로 인해 세 코너의 S자 곡선 개형이 균일화되어 전 코너 $\le 9.0\,\text{ppm}/^\circ\text{C}$ 성능을 유지하는 최고의 온도 안정성을 증명합니다.

### [그림 4] [최종 몬테카를로 히스토그램 (fig13_mc_final.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig13_mc_final.png)
* **증거 단계:** **v6 (면적 스케일링 최종)**
* **설명:** 핵심 능동 소자 면적 4배 확장 이후 MM+PR을 동시에 가하여 실측한 100회 Monte Carlo $V_{ref}$ 히스토그램 분포입니다. 표준편차 $\sigma = 2.21\%$ (3-sigma = $\pm 6.6\%$)로 좁혀져 칩 양산 수율 안정성을 확보하였습니다.

### [그림 5] [MM / PR 미스매치 분해 분석 (fig14_mc_decomp.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig14_mc_decomp.png)
* **증거 단계:** **v6 (몬테카를로 오프셋 진단)**
* **설명:** 로컬 미스매치(MM) 단독 시뮬레이션분과 글로벌 공정 산포(PR) 단독 시뮬레이션분을 독립적으로 실행하여 MM이 분산의 $91.5\%$를 차지하는 주범임을 특정해낸 통계 진단 그래프입니다.

### [그림 6] [스타트업 계단 고문 테스트 (fig11_staircase_final.png)](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/09_area_scaling/fig11_staircase_final.png)
* **증거 단계:** **v3 (스타트업 3라운드 개선 완료)**
* **설명:** 최악 기동 조건(ss/-40°C) 및 Typical 조건에서 전원에 계단파(staircase) 노이즈를 인가하였을 때, 오동작이나 원치 않는 가짜 평형 상태에 고착되지 않고 항상 정상 동작점($V_{ref} \approx 1.2\text{V}$)으로 안전하게 수렴하는 강인한 기동 성능을 입증합니다.

---

## 4. 아카이브 파일 안내
* **bgr_core_tb.spice**: 최종 완료된 BGR Core Spice Netlist
* **DESIGN_JOURNEY.md**: BGR Core 6세대 진화 여정 기록 문서
