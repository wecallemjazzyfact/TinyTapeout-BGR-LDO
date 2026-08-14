# TinyTapeout Analog (BGR + LDO) Workspace & Agent Runbook

본 문서는 **TinyTapeout Analog Shuttle (BGR + LDO 통합 IP 프로젝트)**의 최신 시스템 구조, 문서 체계, 완료된 설계 명세 및 엔지니어링 가이드라인을 수록한 종합 워크스페이스 런북입니다.

---

## 📌 1. 프로젝트 개요 (Project Summary)

| 항목 | 규격 및 설정값 | 비고 |
| :--- | :--- | :--- |
| **Top Module** | `tt_um_bgr_ldo` | GDS/LEF 파일명 정합 필수 |
| **전원 공급 (Power Rails)** | $V_{APWR} = 3.3\,\text{V}$ (Analog), $V_{DPWR} = 1.8\,\text{V}$ (Digital Core), `VGND` | `uses_vapwr: true` configured in `info.yaml` |
| **BGR 기준 전압 ($V_{ref}$)** | $1.200\,\text{V}$ (공칭/트림 후) | $R_2 = 2 R_1$ 저항비 정합, 탭 전류 $I_{B,EA} = 2.564\,\mu\text{A}$ |
| **LDO 목표 출력 ($V_{out}$)** | $1.800\,\text{V}$ (공칭/트림 후) | 분압비 $\beta = 2/3$ (5:10 유닛 정밀 포스트 매칭) |
| **총 부하 전류 ($I_{load}$)** | $50.8\,\mu\text{A} \sim 2.13\,\text{mA}$ | 최소부하 $50.8\,\mu\text{A}$ (분압기 $46\,\mu\text{A}$ + EA 바이어스) |
| **디지털 트림 회로** | **4-bit 이진 병렬 단락 방식** | $V_{out}$ 기준 트림시 잔여 오차 $\pm 8.6\,\text{mV}$ ($\pm 0.48\%$, 마진 76%) |
| **부하 데모 블록** | 11단 RO ($110.89\,\text{MHz}, 95.07\,\mu\text{A}$) + ÷16 분주기 ($6.931\,\text{MHz}$) | RO는 VDDC(LDO), 분주기는 VDPWR, 싱크 버퍼는 VDDC 급전 |

---

## 📂 2. 파일 및 디렉토리 구조 (Directory Architecture)

```
TinyTapeout/
├─ info.yaml                       # TinyTapeout 셔틀 설정 (top_module, pinouts, uses_vapwr)
├─ tapeout-guardrails.md           # 레이아웃/전기적 하드 제약 조건
├─ WORKSPACE.md                    # ★ 본 워크스페이스 안내서 (최신화 유지)
├─ RESTART_GUIDE.md                # 세션 재개 및 인계 가이드
├─ SOURCES.md                      # 상위 레포지토리 및 레퍼런스 링크
│
├─ 00_인계_통합.md                  # 시스템 통합 인계서 (부하/핀배정/전원도메인/Task현황)
├─ 01_BGR_최종스펙.md               # BGR 코어 및 4-bit 디지털 트림 확정 스펙
├─ 02_LUT_앵커.md                  # gm/Id LUT 앵커 및 소자 파라미터 정밀 검증 데이터
├─ 03_PDK_환경.md                  # Sky130 PDK 소자 규칙 및 넷리스트 서브서킷 정의
├─ 04_LDO_스펙.md                  # LDO 루프, EA, Pass 소자, 슬루드라이버, 부하블록, 트림절차
│
├─ .agents/
│  └─ AGENTS.md                    # 프로젝트 가드레일, 시뮬레이션 권한, 문서 관리 규칙
│
└─ designs/bgr_ldo/
   ├─ bgr/                         # BGR 스키매틱 (.sch, .sym), 넷리스트, TB
   ├─ ldo/                         # LDO 회로, 부하블록, TB, python 분석 스크립트
   │  ├─ BOOKKEEPING.md            # ★ 예측 ↔ 실측 장부 (Section 1.1~1.4, 2.1~2.9 MC)
   │  ├─ OPEN_ITEMS.md             # ★ 라벨 관리 레지스터 (A/B/C/D/E 이슈 관리)
   │  └─ DECISIONS.md              # 주요 설계 의사결정 이력 (D-001 ~ D-021)
   ├─ lut/                         # gm/Id LUT 데이터, 스윕 덱, pygmid 라이브러리
   │  └─ README.md                 # LUT 사용 수치 규율 (접선 vs 할선 Ron, intrinsic cap)
   ├─ DESIGN_JOURNEY.md            # 설계 과정 상세 기록 (Ch.LDO-1 ~ Ch.LDO-12)
   ├─ LOGBOOK.md                   # 엔지니어링 타임라인 로그북
   └─ NOTES.md                     # 인터페이스 핀 배정 및 레이아웃 사전 검토 메모
```

---

## 📊 3. 확정 블록별 설계 및 검증 상태 (Design Status)

### 3.1. Bandgap Reference (BGR Core & 4-bit Trim)
- **코어 토폴로지**: Banba current-mode BGR ($R_1 = 34.4\,\mu\text{m}, R_6=R_7=244.5\,\mu\text{m}, R_2=125.4\,\text{k}\Omega$)
- **온도 특성**: $TC = 7.5 \sim 9.0\,\text{ppm}/^\circ\text{C}$ (전 코너 및 트림 코드 스케일 불변)
- **트림 회로**: 4-bit 이진 병렬 단락 ($XR2fix = 108.6\,\text{k}\Omega$, 세그먼트 $1.1 / 2.2 / 4.5 / 9.0\,\text{k}\Omega$, `trim_sw` `nfet_01v8` $m=22 \times 4$)
- **트림 성능**: $V_{out}$ 범위 $1.671 \sim 1.929\,\text{V}$ (16코드 완전 단조성, DNL $0.012\,\text{LSB}$, LSB $17.25\,\text{mV}$, 잔여 오차 $\pm 8.6\,\text{mV}$)
- **핀 배정**: `TRIM[3:0]` ↔ `ui_in[3:0]`, `ua[1]` ($V_{out}$) 기준 트림으로 BGR+LDO+EA 오프셋 통합 흡수.

### 3.2. LDO Regulator & Compensation
- **Pass Device**: `pfet_g5v0d10v5` ($W = 400\,\mu\text{m}, L = 0.5\,\mu\text{m}, M = 20$)
- **Error Amplifier**: PMOS 입력 Folded-Cascode ($V_{APWR}=3.3\,\text{V}$ 급전, $A_{v,EA} = 72.05\,\text{dB}$, $\text{UGF}_{EA} = 4.52\,\text{MHz}$)
- **보상망 (Compensation)**:
  - $C_c = 2.727\,\text{pF}$ (MiM $m=4$), $C_{out} = 30.000\,\text{pF}$ (MiM $m=44$), $R_z = 3\text{유닛}$ ($15.48\,\mu\text{m}$)
  - $C_{byp} = 2.045\,\text{pF}$ (MiM $m=3$, VREF_LOW-GND): 기준 노드 AC 임피던스 억제 ($163 \rightarrow 31.2\,\text{k}\Omega$), 통합 무부하 위상마진 $41.4^\circ \rightarrow 63.5^\circ$ 복구.
- **안정도**: 전 부하($50.8\,\mu\text{A} \sim 2.10\,\text{mA}$) $\times$ 전 코너/온도(24점) 무부하 PM $\ge 59.3^\circ$, GM $\ge 10.1\,\text{dB}$ 확보.

### 3.3. Transient & On-chip Load Block (Task 5 & 6)
- **슬루 드라이버 (Task 5)**: $R_{slew} = 295\,\text{k}\Omega, C_{slew} = 2.727\,\text{pF}$ ($\tau = 1.85\,\mu\text{s}$), 싱크 부하 오버슈트 억제. fail-safe 불채택 (E6 CLOSED).
- **부하 블록 (Task 6)**:
  - 링 발진기(RO): 11단 인버터/NAND 링, $f_{osc} = 110.89\,\text{MHz}, I_{RO} = 95.07\,\mu\text{A}$ (VDDC 급전).
  - 분주기: 4단 표준셀 DFF (`sky130_fd_sc_hd__dfxbp_1` ÷16 리플 카운터, $f_{DIV\_OUT} = 6.931\,\text{MHz}$, VDPWR 급전, `uo_out[0]` 출력).
  - 싱크 스위치: `nfet_01v8` W10/L0.15 m4 (VDDC 급전, $R_{on} = 23.04\,\Omega$).
  - Power-Good (PG): 불채택 (E8 CLOSED), `uo_out[0]` RO 토글 파형으로 고해상도 아날로그 진단 대체. `uo_out[1]` GND 타이오프.

### 3.4. Monte Carlo Verification (Task 9 선행분)
- **MC-A (LDO 자체 오프셋)**: 이상 $V_{ref}$ 치환, $V_{out}$ 3σ $= 20.21\,\text{mV}$ ($1.122\%$). 지배항은 분압 저항 미스매치($16.08\,\text{mV}$)가 EA 오프셋($10.84\,\text{mV}$)보다 1.48배 큼. 트림 양자화 합성 후 $\pm 21.73\,\text{mV}$로 스펙 $\pm 36\,\text{mV}$ 대비 마진 40% PASS. (별도 오프셋 트림 회로 불채택)
- **MC-B (루프 안정도)**: 실제 BGR 유지, 100/100 전원 통과. 최악 PM $61.23^\circ$, 최악 GM $23.25\,\text{dB}$. 공정 코너가 MC 미스매치보다 26배 지배적임을 증명.
- **MC-C (트림 전 범주)**: 실제 BGR 유지, 100/100 창 안 수용 ($V_{out}$ 3σ $101.5\,\text{mV}, 5.64\%$). ±3σ 외삽 상단 여유 $0.31\%$로 얇음 $\rightarrow$ D22/E9 이슈로 BGR 이관.

---

## 🛠 4. 필수 작업 수칙 및 가드레일 (Agent Guardrails)

1. **Schematic-First & Golden Netlist 원칙**
   - 회로 시뮬레이션 및 분석의 정본은 항상 **xschem schematic (`.sch`)**입니다.
   - `.spice` 넷리스트를 임의로 직접 수동 편집하는 행위는 엄격히 금지됩니다. (Schematic 수정 $\rightarrow$ 넷리스트 재추출 $\rightarrow$ 시뮬레이션).

2. **시뮬레이션 실행 및 보고 규칙**
   - 모든 시뮬레이션 실행은 사용자의 명시적 지시가 있을 때만 동기(blocking) 1회 실행합니다.
   - 보고 시 (1) `.spice` 지문 (Checksum), (2) ngspice 실행 타임스탬프, (3) raw 측정 텍스트 원문 3종 세트를 반드시 원문 그대로 포함해야 합니다.

3. **장부 및 레지스터 관리 규율 (BOOKKEEPING & OPEN_ITEMS)**
   - `BOOKKEEPING.md`: 원칙적 **Append-Only** (기존 행 수정/삭제/순서변경 금지). 커밋 첫 줄에 기록 내역 명시.
   - `OPEN_ITEMS.md`: 단일 정본 레지스터. 상태 변경 및 이슈 신설/폐기는 규칙 준수. 커밋 첫 줄에 영향받은 ID 명시 (예: `A6 CLOSED, E8 CLOSED`).

4. **Sky130A 레이아웃 및 핀 규칙**
   - **Metal 5 Prohibition**: `metal 5` (met5) 레이어는 설계 내부 라우팅에 사용 절대 금지 (TT 글로벌 파워 그릿 전용).
   - **Power Pin Stripes**: `VGND`, `VDPWR`, `VAPWR` 핀은 `met4` (metal 4) 수직 스트라이프로 작성 (최소 너비 $1.2\,\mu\text{m}$, 상/하단 $10\,\mu\text{m}$ 이내 연장).
   - **미사용 핀**: 미사용 아날로그 핀(`ua[]`) 및 미사용 디지털 출력(`uo_out[]`, `uio_out[]`, `uio_oe[]`)은 `VGND`에 타이트하게 연결.
