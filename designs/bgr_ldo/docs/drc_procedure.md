# TinyTapeout BGR+LDO — Layout DRC 절차 및 규약 문서 (`drc_procedure.md`)

이 문서는 TinyTapeout BGR+LDO 프로젝트의 레이아웃 DRC(Design Rule Check) 검증 절차, 툴 설정 규약, 주요 룰 기전 및 실측 수정 이력을 관리하는 공식 문서입니다.

---

## 1. Magic DRC 세션 설정 규약 (Session Configuration)

> [!IMPORTANT]
> Magic에서 `drc style`은 영구 저장되는 설정이 아니라 **세션 단위 설정**입니다. Magic을 재시작하면 기본값인 `drc(fast)` 모드로 자동 초기화됩니다.

### 1.1 필수 세션 시작 명령
Magic을 실행할 때마다 대화형 창 또는 Tcl CLI에서 매 세션 시작 시 가장 먼저 아래 명령을 실행해야 합니다.

```tcl
drc style drc(full)
drc euclidean on
```

### 1.2 `fast` 대 `full` 모드 차이점
* **`drc(fast)`**: 래치업(Latch-up) 검사 규칙(`LU.2`, `LU.3`) 등이 비활성화되어 있습니다.
* **`drc(full)`**: 래치업 및 정밀 이격/오버랩 규칙을 포함한 전면 DRC 검사를 수행합니다.
* **TinyTapeout Precheck 기준**: TT 공식 Precheck는 **`drc(full)`** 기준을 적용하므로, `fast` 모드에서의 "DRC clean"은 유효하지 않으며 반드시 `full` 모드에서 검증해야 합니다.

---

## 2. Magic 파일 락 (File Lock) 및 쓰기 권한 관리

> [!WARNING]
> 다른 Magic 인스턴스가 동일 파일/셀을 열고 있거나 락이 걸려 있으면 Read-Only 상태로 로드되어 `save` 명령이 무시됩니다.

### 2.1 파일 락 발생 증상
* 레이아웃 수정 후 DRC 에러 수가 감소했으나, Magic을 재시작하면 수정 내역이 저장되지 않고 이전 상태로 원복됨.

### 2.2 방지 및 해제 절차
1. 작업 시작 전 실행 중인 Magic 프로세스 수 확인:
   ```bash
   ps aux | grep magic
   ```
2. 필요 시 세션 내부에서 강제 쓰기 권한 부여:
   ```tcl
   cellname writeable <cell> true
   ```

---

## 3. KLayout DRC 사인오프 (Sign-off) 절차

Magic DRC와 별개로, 셔틀 최종 제출(TT Precheck) 검증을 위한 KLayout 사인오프 절차입니다.

### 3.1 GDS 내보내기 환경 변수 규약
Magic에서 GDS를 내보낼 때 반드시 `PDK_ROOT`, `PDK`, `PDKPATH` 환경 변수가 export 되어야 하며, `-T sky130A`를 명시해야 합니다. 명시하지 않을 경우 다른 테크 파일이 로드되거나 `$PDKPATH` 문자열이 그대로 남아 GDS 생성/DRC에 실패합니다.

```bash
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c 'export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A && cd /foss/designs/designs/bgr_ldo/layout/bgr_core && $HOME/.local/bin/magic -dnull -noconsole -T sky130A <<EOF
load bgr_mos
gds write bgr_mos.gds
quit -noprompt
EOF'
```

### 3.2 KLayout DRC 실행 명령 규약
* **Rule Deck 경로**: `/foss/pdks/sky130A/libs.tech/klayout/drc/sky130A_mr.drc`
* **필수 인자**: `input`, `report`, **`top_cell`** (밑줄 표기 필수), `feol`, `beol`, `offgrid`, `thr`
  * ⚠️ `topcell` (밑줄 없음)로 인자를 전달하면 셀을 인지하지 못하여 빈 검사 결과가 생성됩니다.
  * `feol=true`, `beol=true`, `offgrid=true` 인자를 각각 켜야 전체 DRC 검사가 활성화됩니다.

```bash
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c 'export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A && cd /foss/designs/designs/bgr_ldo/layout/bgr_core && klayout -b -r /foss/pdks/sky130A/libs.tech/klayout/drc/sky130A_mr.drc -rd input=bgr_mos.gds -rd report=drc_kl.xml -rd top_cell=bgr_mos -rd feol=true -rd beol=true -rd offgrid=true 2>&1 | tail -20'
```

### 3.3 TT Precheck 검증 규칙
* TinyTapeout Precheck는 `feol`, `beol`, `offgrid`를 각각 켜서 수행하며, **단 1건의 DRC 위반이라도 발견될 경우 `PrecheckFailure`로 바로 탈락**합니다 (웨이버 예외 처리 없음).

---

## 4. RPM 레이어 생성 기전 및 `rpm.1a` 위반 분석

### 4.1 `sky130A.tech` (1745행) RPM 생성 매커니즘
```magic
templayer rpm_generate
  bloat-all xhrpoly,uhrpoly xpc
  grow 620
  shrink 420
  mask-hints RPM
  mask-hints URPM
```

### 4.2 연산 동작 방식
1. `xhrpoly`, `uhrpoly`, `xpc` 레이어를 사방으로 `620` (0.31 µm) 확장(grow) 후 `420` (0.21 µm) 축소(shrink)합니다.
2. 이 연산은 결과적으로 **순확장 +0.200 µm** 및 **개별 도형 간 갭 1.24 µm (2 × 0.620 µm) 이내인 경우 병합(Merge)**을 수행합니다.

### 4.3 위반 및 병합 조건 (실측값 기준)
* **단일 폴리 구간**: 폭 `0.69 µm` 단독 폴리는 RPM 생성 시 양쪽으로 `0.200 µm`씩 확장되어 최종 RPM 폭이 `1.09 µm`가 됨 → 최소 요구 폭인 `rpm.1a` (`1.27 µm`) 미달로 **DRC 위반 발생**.
* **다중 컬럼 배열**: 피치 `1.17 µm` (갭 `0.48 µm`) 구조에서는 RPM 영역이 상호 병합되어 `1.27 µm` 이상이 되므로 정상 통과.
* **인접 저항 갭**: 인접한 저항 간 갭이 `0.08 µm` 이내인 경우에도 RPM이 하나의 영역으로 병합됨.
* ★ **핵심 결론**: `rpm.1a` 위반은 "이웃 소자/컬럼 없이 외부에 독립 노출된 탭 단독 구간"에서만 선택적으로 발생합니다.

---

## 5. 세션 DRC 수정 이력 (실측 좌표 포함)

| 수정 항목 | 실측 좌표 영역 (µm) | 해소된 DRC 에러 내용 |
| :--- | :--- | :--- |
| **Trim P-Tap 스트립 연장** | `y -19.90 .. -18.90`, `x 85.00 .. 143.40` | `LU.2` (P-diff to P-tap distance < 15.0um) **88건 해소** |
| **채널 N-Tap 추가** | `y 54.60 .. 55.50`, `x 0.15 .. 63.65` | `LU.3` (P-diff to N-tap distance < 15.0um) **26건 해소** |
| **행 B 하부 N-Tap 전폭 연장** | `x 0.30 .. 63.50` | `LU.3` **6건 해소** |
| **N-Well 동쪽 경계 위치 조정** | `x 65.600` → `x 65.370` | `diff/tap.18`, `diff/tap.20` 위반 해소 |
| **XR_cn 마이크로셀 수평 반전** | 해당 셀 미러링 적용 | `rpm.1a` 노출 탭 위반 **2건 해소** |

---

## 6. 현재 미해결 DRC 항목 (Open Items)

1. **`rpm.1a` 3건 (R7a / R7b 하단 탭 노출)**
   * **원인**: R7a/R7b 하단 탭 영역이 이웃 저항 없이 외부 노출됨.
   * **대응 계획**: R1 저항 배치 결정 대기 (R1 배치 완료 시 이웃 RPM 병합으로 자동 해소 예정).
2. **`rpm.1a` 1건 (`5VVEC7` 트림)**
   * **원인**: `5VVEC7` 트림 셀 단독 탭 노출.
   * **대응 계획**: 트림 셀 재배치 작업 대기.
3. **`psdm.1` 9건 (KLayout 검사 전용)**
   * **원인**: PNP 센서 `psdm` 레이어 (`x 89.380`) ↔ 링 `psdm` 레이어 (`x 89.675`) 간격 = **`0.295 µm`** (최소 요구 간격 **`0.380 µm`** 미달).
   * **상황**: PNP 링 좌측 밴드가 `psubdiff/cont/li/viali/met1` 얇은 스택 구조라 국소 이설이 어려움.
   * **대응 계획**: `rpm.1a` 대응으로 레이아웃 배치가 변경될 때 함께 수율 조정 예정.

---

## 7. 작업 규약 및 실행 가이드라인

1. **파일 및 디렉토리 제어 작업**: `bash -c` 환경에서 실행.
2. **Layout 및 EDA 툴 실행 (Magic, KLayout 등)**: `bash -l -c` 환경에서 실행 (로그인 셸 환경변수 적용 필수).
3. **수치 기록 원칙**: 추정치나 임의 수치를 배제하고 **실측된 좌표 및 측정 데이터**만 표기.
