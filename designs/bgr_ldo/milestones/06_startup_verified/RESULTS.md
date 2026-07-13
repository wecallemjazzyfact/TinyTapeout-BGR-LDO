# Startup Circuit Verification Results (Milestone 06)

This document summarizes the verification results for the 4-transistor active startup circuit. All simulations were performed with the startup circuit enabled and without any `.nodeset` helper statements.

## Verification Summary Table

| 관문 | 조건 | 핵심 결과 | 판정 |
| :--- | :--- | :--- | :---: |
| **tt op** | 27°C, nodeset 없음 | v(vref_low) = `1.216690 V` / v(sense_out) = `14.2 mV` / 킥 잔류 전류 = `33 fA` | **PASS** |
| **tt 계단 고문** | 1.5V에 20µs 정차 | vref_final = `1.21669 V` (가짜 평형 진입 실패 및 정상 상태 도달 확인) | **PASS** |
| **ss/-40 op** | 최악 기동 코너 | v(vref_low) = `1.216273 V` / v(sense_out) = `18.2 mV` / 킥 잔류 전류 = `0.026 fA` | **PASS** |
| **ss/-40 계단 고문** | 최악 코너 + 정차 | vref_final = `1.21627 V` (정상 안착 완료) | **PASS** |
| **ff/125 op** | 최악 잔류 코너 | v(vref_low) = `1.276 V` / v(sense_out) = `15.9 mV` / 킥 잔류 전류 = `9 pA` | **PASS** |

---

## Snapshot File Descriptions

* [bgr_core_tb.spice](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/milestones/06_startup_verified/bgr_core_tb.spice): 정본 넷리스트 (startup 4소자 최종 사이징 포함)
* **fig1_tt_staircase.png**: TT 코너 계단 입력 전원(Staircase) 전원 투입 과도 해석 파형
* **fig2_ss40_staircase.png**: SS/-40°C 코너 계단 입력 전원 과도 해석 파형 (최악 기동 코너 검증)
* **fig3_tt_ramp5us.png**: TT 코너 5µs 고속 램프 업 파형
* **fig4_tc_corners.png**: 스타터 장착 후 전 온도 범위($-40\sim125^\circ\text{C}$) 출력 특성
* **w1_tt_stair.csv ~ w6_tc_ff.csv**: 시뮬레이션 원본 파형 데이터 (6개 파일 백업 완료)
