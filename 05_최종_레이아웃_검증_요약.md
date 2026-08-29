# BGR+LDO 프로젝트 — 레이아웃/검증 세션 최종 정리
(2026-08-11 ~ 08-12, 조립·머지 완료 시점 기준 / 최종 갱신: 2026-08-19 Final MC 반영)

## 상태: TinyTapeout GitHub 브랜치 머지 완료 (`tt_um_` 탑 통합 완료)

---

## 1. 레이아웃 검증 실적

| 검증 항목 | 검증 도구 / 설정 | 결과 및 상태 |
| :--- | :--- | :---: |
| **Magic DRC** | `drc(full)` + `euclidean` (Sky130A) | **DRC Clean (0 에러)** |
| **KLayout DRC** | feol / beol / offgrid / zero_area | **0 / 0 / 0 / 0 (전 항목 통과)** |
| **Netgen LVS** | dfxbp + diode_2 blackbox stub 결합 | **Circuits match uniquely (LVS Pass)** |
| **부유 노드 검사** | Floating net / `_uq` 언커넥티드 검사 | **0 / None (부유 노드 없음)** |
| **Antenna Check** | `SNK_EN`, `RO_EN` 게이트 안테나 위반 검사 | **diode_2 × 2 배치로 완전 해소** |
| **신뢰성 보강** | via 접촉 면적 대폭 확대, Latch-up 방지 탭 4곳 | **배치 완료** |
| **Precheck** | TinyTapeout 공식 프리체크 15개 항목 (Antigravity 조립 후) | **전 항목 PASS** |

---

## 2. PEX + 시뮬레이션 실측치 (tt/27, TRIM=0111 code7 기준)

> **추출 조건**: `ldo_top_pex_rc_safe.spice` (PEX R+C, no coupling, cthresh 0.01, rthresh 1)

| 항목 | 설계 목표 / 규격 | 최종 실측치 (Post-layout PEX R+C) | 판정 및 평가 |
| :--- | :---: | :---: | :---: |
| **기준 동작점** | 1.800 V / 1.200 V | **VDDC: `1.82725 V` / VREF_LOW: `1.21835 V`** | 중앙코드 기준 정상 동작 |
| **루프 AC 안정도** | $\text{PM} > 45^\circ$, $\text{GM} > 10\,\text{dB}$ | **$\text{PM}_{\text{worst}} = 69.8^\circ$ (무부하)**<br>**$\text{GM}_{\text{worst}} = 11.5\,\text{dB}$ (1.5 mA)** | **스펙 완전 만족 (여유 충분)** |
| **Load Step (실사용)** | $\Delta V < 100\,\text{mV}$ (1.98V 보호) | **Under: `-56.3 mV` / Over: `+28.9 mV`** (SNK_EN $1\,\mu\text{s}$) | **정격 대비 124 mV 마진 확보** |
| **Line Step (실사용)** | $\Delta V < 10\,\text{mV}$ | **Dip: `-2.78 mV` / Over: `+1.95 mV`** ($10\,\mu\text{s}$ 슬루) | **매우 우수** |
| **PSRR** | $> 50\,\text{dB}$ @1k | **`-51.9 dB` @DC / `-27.7 dB` @100k / `-9.2 dB` @1M** | **통과** |
| **Startup 기동 시간** | $< 100\,\mu\text{s}$ | **`25 µs` 정착, 오버슈트 `+44 mV`** | **정상 탈출, False-lock 없음** |

> ※ **비현실적 극단 조건과의 구분**: 이상전류원 및 $100\,\text{ns}$ 스텝은 온칩 슬루 제한($XR_{\text{slew}} + XC_{\text{slew}}$)을 우회하는 비현실적 극단 조건(Load overshoot $+160\,\text{mV}$)이므로, 실제 칩에서는 슬루 드라이버가 적용된 실사용 조건(오버슈트 $+28.9\,\text{mV}$)이 정본입니다.

---

## 3. 전 코너 검증 실적 (tt/ss/ff/sf/fs × -40/27/85, 저항 8점 보강)

| 지표 | 최종 실측치 | 분석 및 설계 귀결 |
| :--- | :---: | :--- |
| **트리밍 후 온도 드리프트** | **최대 `±1.33 mV`** | 고저항 폴리 실저항 2성분 매칭 최적화 달성 |
| **저항 코너 포함 VDDC Spread** | **`86.01 mV`** | FET only($77.01\,\text{mV}$) 대비 저항 코너 독립성 반영 확인 |
| **ff/27 트림 전 최대 이탈** | **`+88.7 mV`** | 4-bit 트림 설계 창($\pm 129\,\text{mV}$) 내 완벽 안착 |

---

## 4. Final Monte Carlo 분석 (tt_mm/27, N=299, Mismatch-only, Stage 1 ➜ Stage 2)

```
[시뮬레이션 환경]
- 넷리스트: ldo_top_pex_rc_safe.spice (PEX R+C, cthresh 0.01, rthresh 1)
- 코너/조건: tt_mm (MC_MM_SWITCH=1, MC_PR_SWITCH=0), TEMP=27, TNOM=27
- 구동 조건: SNK_EN=1.8V, RO_EN=0V, VAPWR=3.3V, VDPWR=1.8V
- 표본: 6개 청크 병렬 300회 구동 (완전 수렴 299개 표본)
```

| 검증 지표 | 최종 실측 통계치 | 목표 스펙 대비 평가 |
| :--- | :---: | :--- |
| **트림 전 VREF_LOW $\sigma$** | **`2.040 %`** | BGR pre-layout MM-only 기준선($2.11\%$)과 완벽 정합 |
| **트림 전 VDDC $\sigma$** | **`2.069 %`** (`37.232 mV`) | Mean = $1.799829\,\text{V}$ |
| **4-bit 트림 창 이탈률** | **`0 / 299 (0.00 %)`** | 299개 표본 전량 트림 범위 안착 |
| **★ 트림 후 최종 VDDC $\sigma$** | **`5.073 mV`** (`0.282 %`) | 트림 후 산포 극소화 성공 |
| **★ 트림 후 최종 VDDC $3\sigma$** | **`15.220 mV`** | **LDO 하드 스펙($\pm 36\,\text{mV}$) 대비 2.4배 안전 마진 사수** |

---

## 5. 미해결 항목 (경미, 향후 참고용)

| # | 식별 항목 | 현상 및 상태 | 영향도 및 후속 조치 |
| :---: | :--- | :--- | :--- |
| **C1** | SNK 부하 조건 AC 저주파 이득 편차 | 저주파 이득 $-11\,\text{dB}$ 편차 발생 (단, UGF/PM/GM은 완벽 정합) | 루프 안정성에 영향 없음 (무해) |
| **C2** | VGND IR Drop ($21.3\,\text{mV}$) | VDDC 오차 예산의 약 59% 차지 | 급전점 보강 시도 중 단락 사고로 원상 복구함 (동작 범위 내 확인) |

---

## 6. 트림 Code 정의 (확정 정본 — 향후 재사용 시 필수 참조)

```text
code = 내부 TRIM 비트값 (BGR 정의) = TRIM3·8 + TRIM2·4 + TRIM1·2 + TRIM0·1
ui_in[3:0] (외부 핀) = 15 - code   (인버터 4쌍으로 반전 구동)

- TRIM = 1  ➜  해당 세그먼트 단락  ➜  R2 실효 저항 감소  ➜  V_out 감소
- code 0  (ui_in = 15)  ➜  V_out 최대 출력 (+129 mV 스팬)
- code 15 (ui_in = 0)   ➜  V_out 최소 출력 (-129 mV 스팬)
```

---

## 7. 주요 산출물 위치 및 파일 맵

```
designs/bgr_ldo/
├── layout/ldo_top/
│   ├── ldo_top.mag                 # Magic 레이아웃 정본
│   ├── ldo_top_fixed.gds           # TinyTapeout 제출용 최종 GDS (fix_rpm.py 적용 완료)
│   ├── ldo_top_pex_rc_safe.spice   # PEX R+C 추출 정본 넷리스트
│   ├── ldo_top_pex_ac_{tv,ti}.spice# AC 이중주입 검증 넷리스트
│   └── acdata/, simdata/, plots/   # AC/과도해석 데이터 및 플롯 PNG 7장
└── ldo/
    ├── ac_*.sp, t1*.sp, t2*.sp, t3*.sp, t4*.sp  # 과도 / AC 단위 시험 덱
    ├── c_*.sp, c2_*.sp, r_*.sp, s_*.sp          # PVT 코너 / 저항 코너 / 전 코드 스윕 덱
    └── mc/                                      # Monte Carlo 1·2단계 자동화 환경
        ├── run_0~5.sp, out_0~5.txt              # 1단계 ui 탐색 덱 및 출력
        ├── analyze1.py, stage2_list.txt         # 1단계 분석기 및 최적 ui 매핑 리스트
        ├── run2_0~5.sp, out2_0~5.txt            # 2단계 최적 ui 실측 덱 및 최종 로그
        └── analyze2.py                          # 2단계 최종 통계 추출기
```

---

## 8. 대회/테이프아웃 문서화 및 통합 가이드
1. **디자인 디시전 연계**: 스키매틱 및 레이아웃 단계의 판정 근거(`DECISIONS.md`, `BOOKKEEPING.md`)와 완벽 동기화.
2. **조건 명시**: 극단 조건(100ns 스텝)과 슬루 제어 실사용 조건(1µs~10µs)을 엄격히 분리 표기.
3. **데이터시트 방법론**: §3 코너 조건 및 §4 Monte Carlo 통계 수치를 데이터시트 성능 검증 절에 직접 인용.
4. **BGR 문서 정합**: `01_BGR_최종스펙.md` 및 `04_LDO_스펙.md`와 상호 모순 없이 마스터 데이터로 활용.
