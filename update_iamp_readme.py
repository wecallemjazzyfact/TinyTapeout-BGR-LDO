# 04_iamp — Change Amplifier & PR-SF Interaction Analysis

본 디렉토리는 Photoreceptor와 Change Amplifier 간의 인터페이스 분석 및 Change Amplifier 챕터의 핵심 시뮬레이션 및 Monte Carlo 결과물을 보관합니다.

* **최종 갱신**: 2026-08-17 (Change Amplifier A2 re-freeze / MC 완료)

---

## 📁 파일 목록 및 상세 설명

### 1. Change Amplifier A2 Monte Carlo 결과물
* **`mc_change_amp_200_mm_A2.csv`**: MA/MSH W0.64/L1.0 (A2 sizing) 적용 mismatch-only Monte Carlo (199점 유효, Low-Discrepancy Sequence, mc section, tt/27°C) 원시 데이터.
  * $V_{DIFF,READY}$ mean $1083.03\text{ mV}$, $\sigma = \mathbf{8.15\text{ mV}}$
  * $V_{X,READY}$ mean $640.25\text{ mV}$, $\sigma = 6.04\text{ mV}$
  * $V_{RSTREF,EQ}$ mean $982.19\text{ mV}$, $\sigma = 11.69\text{ mV}$
* **`mc_change_amp_200_pm_A2.csv`**: A2 sizing 적용 Process + Mismatch Monte Carlo (197점 유효) 원시 데이터.
  * $V_{DIFF,READY}$ $\sigma = 63.45\text{ mV}$ (Global/process statistical spread).
* **`MC_mm_A2_distributions.png`**: A2 mismatch MC 199점 분포 히스토그램 ($V_{DIFF,READY}$, $V_{X,READY}$, $V_{RSTREF,EQ}$).
* **`MC_200_results.csv` / `MC_200_distributions.png`**: 초기 MC 실행 데이터.
  * ⚠️ **이전 sizing(W0.32/L0.5)의 MC 데이터는 A2 재검증 과정에서 덮어써져 디렉토리에 존재하지 않습니다.** 이전 sizing의 통계치($\sigma = 11.98\text{ mV}$, first-order 회귀 성분 등)는 마스터 문서(`PROJECT_MASTER_CONTEXT.md` PART 5.2) 및 `CHANGE_AMP_CHAPTER_REPORT.md`에 완전히 보존되어 있습니다.

### 2. PR-SF 상호작용 및 I_amp 스케일링 (PART K, L / TB-04)
* **`K1_pm_table.csv`**: $IB\_PR \times I_{PH}$ 44개 STB 런의 UGF 및 PM 전체 테이블.
* **`K2_scaling.png` / `K2_scaling.csv`**: $I_{cross}$ vs $I_{amp}$ 선형 비례 스케일링 검증 (기울기 $0.2435$, $R^2 = 0.8878$).
* **`K3_verdict.csv`**: $I_{PH}=1\text{ nA}$ 판정표 및 어레이 전력 산출표.
* **`K4_pm_curves.png` / `K5_apr_invariance.png`**: $PM$ vs $I_{PH}$ 및 $A_{PR}$ 불변성 그래프.
* **`L1_sf_sweep.csv`**: $IB\_PR \in \{8, 32\}\text{nA} \times IB\_SF \in \{3, 12, 48\}\text{nA} \times I_{PH}$ (36 STB 런) 데이터.
* **`L2_sf_vs_nosf.csv`**: SF 제거(04c) vs SF 포함(04b) 동일 조건 대조표.
* **`L3_pmmin_theory.csv`**: 2차 피드백 시스템 댐핑 이론치와 실측 PM 최소값 오차 검증표 (오차 $\le 0.4^\circ$).
* **`L4_pm_compare.png`**: $IB\_PR=8\text{ nA}$ 기준 SF 바이어스별 및 SF 제거 시 PM 비교 곡선.
* **`L5_verdict.csv`**: $I_{PH}=1\text{ nA}$ 기준 전 조합 판정표.
* **`L6_ugf_sfpole.txt`**: SF 극점 주파수($f_{p,sf}$)와 UGF 간의 위상 지연 상세 계산 리포트.

### 3. Change Amplifier D4 (A2 Sizing) 확정 결과
* **토폴로지**: D4 (Single-ended cascoded CS + feedback NMOS SF level shift + switched reset sink, 10T, MA/MSH W0.64/L1.0)
* **주요 성능**:
  * $A_{ol} = 921.6\text{ V/V (59.3 dB)}$
  * $A_{CL} = -19.40\text{ V/V}$
  * $V_{10\%,nom} = 56.9\text{ mV}$
  * $V_{DIFF,RST} = 1110.09\text{ mV}$ [tt], $V_{DIFF,READY} = 1093.78\text{ mV}$ [tt]
  * $\mu_{inj} = -16.31\text{ mV}$
  * $V_X = 650.58\text{ mV}$, $V_{SHIFT} = 459.53\text{ mV}$
  * $H_{down,READY} \approx 588\text{ mV}$, $H_{up,READY} \approx 405\text{ mV}$
  * $PM = 49.44^\circ, GM = 9.09\text{ dB} @ 4.66\text{ MHz}$
  * $I_{BIAS} = 13.91\text{ nA}$, $t_{RST,\min,nom} = 500\text{ ns}$
  * $\sigma(V_{DIFF,READY}) = \mathbf{8.15\text{ mV}}$, $\sigma_{cmp,\max} = \mathbf{7.94\text{ mV}}$
* **참조 문서**: `CHANGE_AMP_CHAPTER_REPORT.md`, `PROJECT_MASTER_CONTEXT.md` (PART 5.2), `FREEZE.md`
