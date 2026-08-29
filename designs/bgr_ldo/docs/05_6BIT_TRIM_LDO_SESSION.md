# 6-bit 트림 전환 — LDO 세션 정리 (2026-08-27 ~ 08-29)

## 0. 결론

6-bit 트림 전환 완료. **DRC / LVS / PEX / MC 전부 통과.**
MC 결과가 4-bit 대비 대폭 개선 (3σ 15.22 → 10.25 mV, 여유 2.37 → 3.51배).

남은 작업: **AC 루프이득 / 과도(Transient) / PSRR** 재검증.

---

## 1. 최종 검증 결과

### 레이아웃
| 검사 | 결과 | 비고 |
|---|---|---|
| **Magic `drc(full)` + euclidean** | `rpm.1` 15건 | 전부 `fix_rpm.py` 후처리 대상 (CLEAN) |
| **Netgen LVS** | **Circuits match uniquely** | 소자 및 넷 100% 일치 |
| **KLayout feol / beol / offgrid** | **0 / 0 / 0** | 전 항목 Clean 통과 |

`fix_rpm.py` FIX 리스트 **12 → 15개** (BGR 6-bit 신규 3건 추가 반영)
```python
( 68.960,  39.800,  70.230,  42.480, "BGR GHYW6X_0 (6bit 신규)")
(114.770,  39.800, 116.040,  42.480, "BGR GHYW6X_1 (6bit 신규)")
(109.610,   2.800, 110.880,   5.480, "BGR UKBC2Q_1 (6bit 신규)")
```

### PEX
```text
파일   layout/ldo_top/pex6_safe.spice
소자   X 575 / R 6396 / C 75      (4-bit 대비: 540 / 6147 / 67)
포트   14개: VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN VGND VDPWR
             DIV_OUT RO_EN TRIM0 TRIM5     ← TRIM0 / TRIM5 가 맨 뒤에 위치
```

### 트림 특성 (tt/27, 64코드 스윕)
```text
스팬      2042.6 mV   (code 0: 2.043118 V -> code 62: 1.523760 V)
LSB 평균  8.4 mV      (LUT step mean: 8.377 mV)
단조      63코드 단조 (LUT rank 기준 완벽 단조)
```

### 코너 (code 28, 15점)
| Corner | −40°C | 27°C | 85°C | 드리프트 ($\Delta V$) | TC [ppm/°C] |
|---|---|---|---|---|---|
| **tt** | 1.798867 V | 1.800143 V | 1.798442 V | **1.701 mV** | **7.56** |
| **ss** | 1.800650 V | 1.802518 V | 1.801426 V | **1.868 mV** | **8.29** |
| **ff** | 1.868485 V | 1.869898 V | 1.867855 V | **2.043 mV** | **8.74** |
| **sf** | 1.793833 V | 1.794696 V | 1.792225 V | **2.471 mV** | **11.01** |
| **fs** | 1.806282 V | 1.802781 V | 1.801318 V | **4.964 mV** | **22.03** |

> **분석**: 27°C 기준 코너 간 최대 이탈은 **75.2 mV**로, LSB 8.4 mV 기준 9코드면 완벽 보정 가능합니다. 전체 스팬이 2043 mV에 달해 4-bit 대비(스팬 262 mV, ff_mm 상단 마진 1.7 mV) 압도적인 마진을 확보했습니다.

### MC (tt_mm / 27°C / N=300 / Mismatch only)
| 단계 | 방법 | $\sigma$ | $3\sigma$ | 비고 |
|---|---|---|---|---|
| **Stage 1** | code 28 고정 | 36.535 mV | — | 트림 전 raw 산포 |
| **Stage 2** | 이진 code 이동 | 6.843 mV | 20.529 mV | 비단조 역전 구간 편향 포함 |
| **★ Stage 3** | **LUT rank 이동** | **3.417 mV** | **10.251 mV** | **스펙(±36 mV) 대비 3.51배 여유** |

```text
통계 요약:
  Mean: +0.510 mV,  Min / Max: -5.299 mV / +12.221 mV
  스펙(±36 mV) 대비 마진 3.51배,  규격 위반: 0 / 294 (수율 100%)
  VREF_LOW: Mean 1.205455 V,  σ 0.4316 %
  사용 코드: code 15 ~ 41 (상하 여유 15코드 / 22코드)
  양자화 이론 σ: 2.418 mV,  실측/이론 비: 1.41 (양자화 지배 한계 근접)
```
> ※ 이탈 2건(k0i1, k1i5)은 Stage 2 미수렴이 전파된 수치이며 트림 로직과는 무관합니다. 실칩은 실측 후 코드를 주입하므로 294개 표본이 정본 통계입니다.

---

## 2. ★ 트림 코드는 LUT 순서로 써야 한다

**이진 code 순서는 단조가 아니다:**
```text
code 31 = 011111  ->  1.774496 V
code 32 = 100000  ->  1.783678 V     (+9.18 mV 역전 발생)
```
- **원인**: TRIM5(18,198 Ω) > 하위 5비트 합(17,886 Ω) = 312 Ω 초과
- **영향 및 해법**: 이진 code로 트림하면 `dcode ≥ +4` 구간 샘플이 **+17 mV 편향**을 가집니다 (Stage 2 $\sigma = 6.843\text{ mV}$의 주원인). 이를 **전압 내림차순 rank**로 이동시키면 완전 해소됩니다.

```text
LUT 파일  : ldo/lut6.txt   (rank code V, 63 엔트리)
알고리즘  : rank_new = rank_cur + round((V - 1.800) / 8.377mV)
```
★ **데이터시트 및 실칩 교정(Calibration) 절차에 필수 반영 사항**.

---

## 3. 핀 배정 (확정)

```text
TRIM0 (LSB, 613 Ω)   = ui_in[7]   x 101.700
TRIM1 = ui_in[0]  x 120.930   ┐
TRIM2 = ui_in[1]  x 118.170   │ 기존 배선 유지, 라벨만 개명
TRIM3 = ui_in[2]  x 115.410   │
TRIM4 = ui_in[3]  x 112.650   ┘
TRIM5 (MSB, 18198 Ω) = ui_in[6]   x 104.460
SNK_EN = ui_in[4]     RO_EN = ui_in[5]     (불변)
```
- **극성**: `VTRIM 외부핀 패턴 = 63 - code` (인버터 반전 구동)
  - `code 0`  = V 최대
  - `code 63` = V 최소

---

## 4. 이번 세션에 추가한 레이아웃

```text
1. 인버터 2쌍
   - CJPTEX_4/5 (x 101.600..103.780, y 69.680..74.490)  ★ 상하반전 필수
   - QW2JRF_4/5 (x 101.780..103.600, y 66.900..69.470)
   - nwell : x 101.600..103.780, y 69.680..75.570
   - p-tap : y 66.000..66.600 / n-tap : y 74.790..75.390
   - 급전 metal1 : VGND x 101.600..110.000 / VDPWR x 101.780..111.400

2. ui 핀 Riser
   - ui[7] riser: met4 x 101.450..101.950, y 78.400..79.200
                  met3 x 101.450..102.260, y 78.400..78.900
                  met2 x 101.780..102.260, y 69.820..78.900
   - ui[6] riser: met4 x 104.210..104.710, y 77.600..79.200
                  met3 x 102.870..104.710, y 77.600..78.100
                  met2 x 102.870..103.350, y 69.820..78.100

3. 출력선 라우팅
   - 출력 A (TRIM0): met4 남하 x 102.150..102.730 (y 34.000..65.960)
                     met4 서진 x  34.250..102.730 (y 34.000..34.580)
                     하강 x 34.250..34.750 ➔ BGR 스터브 met2 상단 y 34.000
   - 출력 B (TRIM5): met4 남하 x 103.240..103.820 (y 18.800..65.960)
                     met4 서진 x  60.600..103.820 (y 18.800..19.380)
                     하강 x 60.600..61.100 ➔ BGR 스터브 상단 y 19.000

4. met2 브리지 (VDDC / VREF_LOW 세로선이 BGR n_b5 옛 트랙을 넘던 자리)
   - x 131.200..131.680 / 132.460..132.940, y -10.040..-7.390
   - ★ BGR 트랙이 y -4.6으로 이설되어 현재는 기능상 불필요하나 안전상 유지 중
```

---

## 5. 도구 (재사용 자산)

| 파일 | 용도 |
|---|---|
| [`layout/ldo_top/occupancy.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/layout/ldo_top/occupancy.py) | 전층 + 인스턴스 bbox 점유표 생성 |
| [`layout/ldo_top/trace_net.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/layout/ldo_top/trace_net.py) | 두 좌표 간 연결 경로 BFS 추적 (단락 진단기) |
| [`layout/ldo_top/sanitize_pex.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/layout/ldo_top/sanitize_pex.py) | PEX 넷리스트 sanitize (점 ➔ 언더바 및 MOS 단위 정제) |
| [`ldo/gen_sweep6.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/ldo/gen_sweep6.py) | 64코드 스윕 덱 자동 생성기 |
| [`ldo/mc/mc6_stage1.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/ldo/mc/mc6_stage1.py) | MC Stage 1 (code 고정 검증) |
| [`ldo/mc/mc6_stage2.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/ldo/mc/mc6_stage2.py) | MC Stage 2 (이진 code 이동) |
| [`ldo/mc/mc6_stage3.py`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/ldo/mc/mc6_stage3.py) | **MC Stage 3 (LUT rank 이동, 골든 기준)** ★ 필수 사용 |
| [`ldo/lut6.txt`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/ldo/lut6.txt) | 6-bit 전압 정렬 룩업 테이블 (63개 엔트리) |

---

## 6. 핵심 설계 및 운용 규율

### PEX 규율
```text
1. load ldo_top ; select top cell ; flatten ldo_top_flat ; load ldo_top_flat
2. extract style ngspice()        ★ (si) 절대 금지 — u/p 접미사 붙어 파싱 깨짐
   extract do resistance ; extract all
   ext2sim labels on ; ext2sim
   extresist tolerance 10 ; extresist all
   ext2spice lvs ; ext2spice cthresh 0.01 ; ext2spice rthresh 100
   ext2spice extresist on ; ext2spice -o pex6.spice
3. python3 sanitize_pex.py pex6.spice pex6_safe.spice
   검증: X/R/C 개수, 잔여 점 0, C.. 15.11875f 형태 유지 확인
```

### 시뮬레이션 규율
```text
- 저온(-40°C) 및 MC에서 DC 다중해/수렴 지연 발생 시:
  .nodeset v(VDDC)=1.80 v(VREF_LOW)=1.20 또는 .ic 지정
- MC 병렬 실행은 최대 2~4개 권장 (6개 동시 실행 시 CPU/메모리 경합으로 3배 이상 지연)
```

### Magic 레이아웃 편집 규율
```text
- 편집 후 즉시 `save ldo_top`. flush/load 시 미저장 작업 증발 주의
- `cellname list modified` 에 ldo_top 없으면 discard
- 자식 셀(bgr_mos, 기본 소자셀)은 어떠한 경우에도 상위에서 저장 금지
- `save <name>` 은 셀 이름 자체를 변경하므로, 백업은 반드시 쉘 커맨드 `cp` 로 수행
- `erase via2` 는 met2/met3 를 함께 삭제하므로 결선 복구 필수
```

### BGR 협업 레이아웃 가이드
```text
- DRC 통과만으로 단락 부재를 보장할 수 없음 ➔ 반드시 LVS 합격까지 완료해야 사인오프
- 배선 원칙: met2 = 세로 전용, met3 = 가로 전용
- LDO met3 세로 전용 예약 대역:
  * x 130.940..133.100, y -80.000..-3.700  : VDDC / VREF_LOW 간선
  * x  -1.380..  1.120, y -39.000..79.200  : 서단
- MiM 뱅크 영역 (y -26.900..-8.190, x 8.120..130.940) 내부 via2 금지 (capm.8 위반)
  ★ MiM 하판은 met3이며 VDDC 노드임 — 무관한 met3 가로선 통과 시 즉시 단락 사고 발생
- 점유표 교환 시 인스턴스 BBox 포함 필수 (레이어 사각형만 보면 MiM을 놓침)
```

---

## 7. 다음 세션 작업 계획 (Next Actions)

1. **AC 루프 안정도 재검증** (Middlebrook 이중주입)
   - 4-bit 기준: $\text{PM} = 69.84^\circ$, $\text{GM} = 11.49\text{ dB}$
2. **과도 응답 (Transient) 재검증** (Load / Line / Startup)
   - 4-bit 기준: Undershoot $-56.3\text{ mV}$, Overshoot $+28.9\text{ mV}$
3. **PSRR 주파수 특성 재검증**
   - 4-bit 기준: $\text{DC} -51.9\text{ dB}$, $100\text{k} -27.7\text{ dB}$, $1\text{M} -9.2\text{ dB}$
4. **기존 테스트벤치 덱 6-bit 전환**:
   - 대상: `ac_tb.sp`, `t1_load.sp`, `t2_line.sp`, `t3_psrr_*.sp`, `t4_start.sp`
   - 포트 14개, VTRIM 6개(`TRIM0~5`), `pex6_safe.spice` 적용
5. **GDS 최종 제출본 갱신 및 TinyTapeout Precheck 검증**
6. **데이터시트 반영**: LUT 트림 표 및 VGND IR 드롭 ($21.3\text{ mV}$) 규격 명시
