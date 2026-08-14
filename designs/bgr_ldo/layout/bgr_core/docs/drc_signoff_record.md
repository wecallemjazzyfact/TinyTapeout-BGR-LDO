# TinyTapeout BGR+LDO — Layout DRC 사인오프 기록 문서 (`drc_signoff_record.md`)

이 문서는 TinyTapeout BGR+LDO 레이아웃의 최종 DRC(Design Rule Check) 사인오프 검증 결과, 룰 분석 기전, 세션 수정 이력, KLayout 검증 절차 및 PEX 포트 순서 규율을 기록한 공식 문서입니다.

---

## 1. 최종 사인오프 상태 (Final Status — 전 항목 0)

* **Magic DRC (`drc style drc(full)` + `drc euclidean on`)**: **`0 errors` (DRC CLEAN)**
* **Magic Antenna Check**: **`0 violations`**
* **KLayout Sky130A MR (`sky130A_mr.drc` — `feol` + `beol` + `offgrid`)**: **`0 violations` (CLEAN)**
* **KLayout Zero Area Check (`zeroarea.rb.drc`)**: **`0 violations`**
* **KLayout Pin Label Purposes Check (`pin_label_purposes_overlapping_drawing.rb.drc`)**: **`0 violations`**
* **KLayout `urpm/nwell` Check (`nwell_urpm.drc`)**: **`0 violations`**
* **Netgen LVS (계층 및 Flatten 양쪽)**: **`Circuits match uniquely`**, **`property error 0`**
* **PEX (R+C Extraction)**: 소자 **186개**, R **4,942개**, C **31개**
* **사인오프 백업 파일**: `bgr_mos_DRCCLEAN.mag`, `bgr_mos_DRCCLEAN.spice`, `bgr_mos_DRCCLEAN.gds`

---

## 2. ★ `drc style`은 세션 설정이다 (가장 중요)

> [!IMPORTANT]
> Magic에서 `drc style`은 영구 저장이 아닌 **세션 단위 설정**입니다. Magic을 재시작하면 기본값인 `drc(fast)` 모드로 자동 리셋됩니다. `fast` 모드에는 Latch-up (`LU.2`, `LU.3`) 검사 등이 제외되어 있습니다.

### 2.1 세션 필수 시작 명령
Magic 실행 직후 매 세션 시작 시 가장 먼저 아래 명령을 실행해야 합니다.
```tcl
drc style drc(full)
drc euclidean on
```

### 2.2 실측 검증 이력
* 본 세션 이전의 모든 "DRC clean" 표기는 `fast` 모드 기준이었습니다.
* `drc(full)` 모드로 전환하자 무려 **120건 이상의 감춰져 있던 DRC 오류**가 새로 검출되었습니다:
  * **`LU.2`**: 88건
  * **`LU.3`**: 32건
  * **`diff/tap.18,20`**: 1건
  * **`rpm.1a`**: 6건
* **KLayout 전용 추가 검출**: **`psdm.1` 9건** (Magic은 `psdm` 레이어를 기본 검사하지 않음).
* **TinyTapeout Precheck 기준**: TT 공식 Precheck는 **`drc(full)`** 기준을 적용하므로 반드시 `full` 모드에서 검증을 마쳐야 합니다.

---

## 3. ★ `error_p` 마커에 의한 셀 BBox 팽창 현상 및 방지 규율

### 3.1 팽창 사고 기전
Magic에서 `drc check`가 실행될 때 자식 셀(Child Cell) 내부에 에러 표시 마커인 `error_p` 타일을 생성합니다. 이 상태에서 `writeall force` 시 해당 마커가 세이브되면서 자식 셀의 BBox(Bounding Box)가 실제 소자 영역보다 부풀어 오르게 됩니다.

### 3.2 실측 사고 사례
* `res_high_po_0p69` 마이크로셀의 BBox `y` 범위가 정상 `±2.715 µm`에서 `±2.915 µm`로 **`0.200 µm` 팽창**.
* 이 상태에서 `getcell` 수행 시 BBox 좌하단(LL) 기준으로 위치가 잡히므로 트림 4개 셀이 0.2 µm 위로 밀려 배치됨.
* 트림 패드가 `n_b0` 바와 접촉하여 **`n_b0` / `n_b2` / `VGND` 3중 물리적 단락** 발생 (DRC는 통과하였으나 SPICE 추출에서 발각).

### 3.3 작업 규율
1. `getcell` 수행 전 반드시 `.mag` 파일의 `box` 수치를 확인합니다.
2. 셀 배치 완료 후 원점(Origin) 및 배치 좌표를 실측 검증합니다.
3. 마커를 지워도 다음 `drc check`에서 재생성되므로, 부풀어 오른 BBox를 감안한 좌표 보정이 실용적인 방안입니다.

---

## 4. RPM 생성 기전 (`sky130A.tech` 1745행)

### 4.1 생성 연산 코드
```magic
templayer rpm_generate
  bloat-all xhrpoly,uhrpoly xpc      # 폴리 + 터미널 패드
  grow 620 ; shrink 420
```

### 4.2 연산 동작 방식 및 수치
* `xhrpoly`, `uhrpoly`, `xpc` 레이어를 `620` (0.31 µm) 확장(grow) 후 `420` (0.21 µm) 축소(shrink)합니다.
* 결과적으로 **순확장 +0.200 µm** 및 **개별 도형 간 갭 1.24 µm (2 × 0.620 µm) 이내인 경우 사각형 병합(Merge)**을 수행합니다.
* **단일 폴리**: 폭 `0.69 µm` 단독 폴리는 양쪽 확장 시 RPM 폭 `1.09 µm` < `rpm.1a` (`1.27 µm`)로 **DRC 위반**.
* **다중 컬럼 배열**: 피치 `1.17 µm` (갭 `0.48 µm`) 및 인접 저항 간 갭 `0.08 µm` 구조는 RPM 영역이 상호 병합되어 정상 통과.

### 4.3 핵심 법칙
* ★ **위반 발생 조건**: `rpm.1a` 위반은 "이웃 소자/컬럼 없이 외부에 독립 노출된 탭/단독 구간"에서만 발생함.
* ★ **병합 범위**: 병합은 좌우 어느 쪽이든 성립하며, 병합된 어레이에서는 양 끝의 최대 높이 탭 1개만 외부로 노출됩니다.
* ★ **부분 교체 불가**: 저항 슬롯 1칸을 건너뛰면 갭이 `1.25 µm` (> `1.24 µm`)로 넓어져 RPM 병합이 끊깁니다.
* ★ **PDK pcell 단독 배치 시 위반은 정상**: PDK pcell 단독 배치 시 `rpm.1a` 위반이 뜨는 것은 정상 동작이며, 어레이 배열을 통해 병합시키는 것이 표준 전제입니다.

---

## 5. PSDM 생성 기전 (실측 역산)

### 5.1 생성 연산 원리
$$\text{psdm} = \text{확산}(\texttt{psubdiff} / \texttt{psubdiffcont}) + 0.125\ \mu\text{m}$$

### 5.2 이설 작업 시 주의 사항
* `locali` 및 `metal1`은 `psdm`을 생성하지 않습니다. 이설 시 이 레이어들을 함부로 이동시키면 안 됩니다.
* **실측 사고 사례**: PNP 링 좌측 밴드 이설 시 `locali`까지 함께 옮겨 PNP base 브리지를 절단, `li.3` 위반 10건 발생.
* **정답 방안**: 확산(`psubdiff`) 레이어만 옮기고 `locali`는 넓게 두는 것이 올바른 처리 방식입니다.

---

## 6. 수정 이력 (실측 좌표, µm)

| 수정 항목 | 레이어 및 실측 좌표 영역 (µm) | 해소된 DRC 에러 내용 |
| :--- | :--- | :--- |
| **Trim P-Tap 스트립 연장** | `psubdiff+locali`: `x 85.00–143.40`, `y -19.90..-18.90`<br>`cont` 인셋 `0.12`, `viali` 인셋 `0.16`, `metal1`: `x 84.20–143.40` | `LU.2` (88건 해소) |
| **채널 N-Tap 추가** | `mvnsubdiff+locali`: `x 0.15–63.65`, `y 54.60..55.50` | `LU.3` (26건 해소) |
| **행 B 하부 N-Tap 전폭 연장** | 전폭 연장: `x 0.30–63.50`, `y 39.80..40.50` | `LU.3` (6건 해소) |
| **컬럼 1 N-Well 동단 조정** | `x 65.600` ➔ `x 65.370` | `diff/tap.18,20` (1건 해소) |
| **링 좌변 확산 위치 이동** | `x 89.800` ➔ `x 89.900` (`locali`는 `89.800` 유지) | `psdm.1` (9건 해소) |
| **트림 R2b0~b3 미러링** | 좌우 미러, 높이 내림차순 수평 재배치<br>`5VVEC7` (113.70) / `QCK2SQ` (114.87) / `T8D7K5` (116.04) / `F6JLQ4` (117.21) | `rpm.1a` (1건 해소) |
| **R1 (`Y74LVQ`) 위치 이동** | LL `y 45.455` ➔ `y 39.800` (5.455 µm 하강) | `rpm.1a` (3건 해소) |
| **`XR_cn` ↔ `UKBC2Qa` 셀 교환 및 미러** | 셀 교환 + `XR_cn` 수평 반전<br>`UKBC2Qa` ppolyres: `91.000–92.860`<br>`XR_cn`: `93.340–101.050` | `rpm.1a` (2건 해소) |

---

## 7. KLayout 사인오프 절차

### 7.1 GDS 내보내기 규약
* `PDK_ROOT`, `PDK`, `PDKPATH` 환경변수 export 및 `-T sky130A` 명시 필수.
* 누락 시 다른 tech가 로드되거나 `$PDKPATH`가 문자 그대로 남아 GDS 추출에 실패합니다.

```bash
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c 'export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A && cd /foss/designs/designs/bgr_ldo/layout/bgr_core && $HOME/.local/bin/magic -dnull -noconsole -T sky130A <<EOF
load bgr_mos
gds write bgr_mos.gds
quit -noprompt
EOF'
```

### 7.2 KLayout DRC 실행 명령 규약
* **Rule Deck**: `/foss/pdks/sky130A/libs.tech/klayout/drc/sky130A_mr.drc`
* **인자**: `input`, `report`, **`top_cell`** (밑줄 표기 필수), `feol`, `beol`, `offgrid`, `thr`
  * ★ `topcell` (밑줄 없음)로 인자를 전달하면 셀을 잡지 못해 결과가 비어 나옵니다.

```bash
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c 'export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A && cd /foss/designs/designs/bgr_ldo/layout/bgr_core && klayout -b -r /foss/pdks/sky130A/libs.tech/klayout/drc/sky130A_mr.drc -rd input=bgr_mos.gds -rd report=drc_kl.xml -rd top_cell=bgr_mos -rd feol=true -rd beol=true -rd offgrid=true -rd thr=1 2>&1 | tail -20'
```

### 7.3 TinyTapeout Precheck 검증 규칙
* TT 공식 Precheck(`/foss/designs/tt/precheck/precheck.py`)는 `feol`, `beol`, `offgrid`를 각각 활성화하여 실행하며, **단 1건이라도 위반 시 `PrecheckFailure`로 바로 탈락**합니다 (웨이버 없음).

---

## 8. ★ PEX 래퍼 포트 순서 함정 및 작업 규율

### 8.1 포트 순서 변경 사고 기전
Magic에서 PEX 재추출 시 `.subckt` 포트 순서가 자동으로 변경될 수 있습니다:
* **1차 추출 순서**: `VGND VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3`
* **2차 추출 순서**: `VGND VAPWR VREF_LOW TRIM0 TRIM1 TRIM2 TRIM3 IB_EA`

### 8.2 실제 사고 사례
* 래퍼(Wrapper) 스파이스가 1차 순서(옛 순서)로 유지된 상태에서 2차 extraction 넷리스트를 연동하여 시뮬레이션 수행.
* 핀 순서 밀림 현상 발생 ➔ `TRIM0`에 0.95V가 인가되고 `IB_EA`에 0V가 들어감.
* 오류 메시지 없이 동작하여 `V_ref = 1.112V`, `i(vload) = 0`으로 오동작 결과가 산출됨.

### 8.3 작업 규율
* 재추출 시 `.subckt` 핀 목록 줄과 래퍼 파일의 핀 순서를 **매번 수동/자동 대조**합니다.
* 래퍼 파일 주석에 추출 시점의 핀 순서를 명시적으로 기록 관리합니다.
