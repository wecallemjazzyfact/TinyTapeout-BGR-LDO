# BGR 레이아웃 완료 핸드오프 — LDO 존 착수용

**상태**: BGR 코어 물리 레이아웃 **DRC full CLEAN (Magic 0 / KLayout 0) & LVS 통과 (Circuits match uniquely, 186개 소자, property error 0)**  
**백업**: `bgr_mos_DRCCLEAN.mag`, `bgr_mos_DRCCLEAN.spice`, `bgr_mos_DRCCLEAN.gds`  
**작성 시점**: 트림 스위치·포트·전역 트렁크·트림 균등화 재배선·PEX(R+C 4942R/31C) 및 DRC full 사인오프 완료.  
**개정**: rev5 — DRC full 사인오프(Magic 0 / KLayout 0), error_p 팽창·RPM·PSDM 기전 반영, PEX 2차 결과 반영  
**마감**: 2026-09-07  

---

# 0. 이 문서의 사용법

새 채팅에서 LDO 존 작업을 시작할 때 이 문서를 근거로 삼는다. 우선순위:

1. **§1 환경·경로** — 명령 형식이 틀리면 아무것도 안 된다
2. **§2 magic 함정** — 이 세션에서 실제로 발생한 사고 목록. 반복하지 말 것
3. **§3 작업 규율** — 검증 루틴. 이걸 지켰기 때문에 LVS가 닫혔다
4. **§4 셀 기하** — 좌표 계산의 유일한 정본
5. **§5~7** — 현 레이아웃 좌표·플로어플랜
6. **§8~10** — 다음 작업

**최우선 원칙**: 소자 수치·좌표는 **당세션 실측만 인용**한다. 기억·추정 금지. 모든 수치에 조건(층/좌표계/추출법) 병기.

---

# 1. 환경 · 경로 · 명령 형식

## 1.1 도커 · 툴

```text
컨테이너: iic-osic-tools_xvnc_uid_1000
PDK:      export PDK=sky130A; export PDKPATH=/foss/pdks/sky130A
magic:    8.3.664
```

**명령 형식 — 이것을 틀리면 command not found가 난다:**

| 용도 | 형식 |
| :--- | :--- |
| 파일 작업 (python, cp, grep, ls) | `docker exec <컨테이너> bash -c '...'` 또는 `python3 -c` |
| 툴 실행 (magic, ngspice, netgen) | `docker exec <컨테이너> bash -l -c '...'` |

`bash -c`는 PATH를 로드하지 않는다. docker는 한 번에 하나만 실행.

## 1.2 경로 정본

```text
designs/bgr_ldo/
  bgr/          BGR 정본 (동결) — bgr_core_lvs.spice = LVS 골든
  ldo/          LDO 작업 — OPEN_ITEMS.md (A/B/C/D/E 라벨 정본)
  lut/          소자 LUT 공용 — lookup.py
  top/          top 조립
  milestones/
  layout/bgr_core/   ← 레이아웃 작업 디렉터리
```

구 `sim/` 참조는 전부 `bgr/`로 읽는다.

## 1.3 주요 파일

| 파일 | 내용 |
| :--- | :--- |
| `layout/bgr_core/bgr_mos.mag` | **작업 셀 (정본)** |
| `layout/bgr_core/bgr_mos_LVSCLEAN.mag` | LVS 통과 시점 백업 |
| `bgr/bgr_core_lvs.spice` | LVS 골든 넷리스트 (더미 반영 완료) |
| `/foss/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl` | netgen setup |

## 1.4 참조 문서 (이미 작성됨)

| 문서 | 내용 |
| :--- | :--- |
| `/mnt/user-data/outputs/bgr_cell_catalog.md` | 셀 해시·bbox·중심오프셋·DRC룰·함정 |
| `/mnt/user-data/outputs/sky130A_drc_reference.md` | DRC 룰 전문 |
| `/mnt/user-data/outputs/magic_cheatsheet.md` | magic 명령 |

## 1.5 역할 분담

- **시뮬 실행 · xschem 수정**: 사용자
- **Claude**: 설계판단 · 계산 · 해석 · 프롬프트 · 문서
- **Antigravity**: 스크립트 · 문서만, **시뮬 실행 금지**

---

# 2. ★ magic 함정 — 실제 사고 이력

이 세션에서 **실제로 발생해 디버깅에 시간을 쓴** 것들. 전부 재발 가능.

## 2.1 contact 타입 erase → 상하 금속이 함께 파인다 (5회 이상 발생)

`via1` / `via2` / `viali` / `*cont`는 **금속 성분을 포함한 단일 타일 타입**이다.

```tcl
erase via2   ;# met2 + met3 + 컷이 전부 사라진다
```

**증상**: erase 직후 DRC가 폭·감쌈·간격 위반 10~20건 폭발. 좁고 긴 슬리버(0.03~0.09) 형태.

**규칙**: contact를 지운 뒤에는 **반드시 해당 영역의 금속을 전부 재도포**하고 DRC를 다시 돌린다.

```tcl
box <영역>
erase via2
erase metal2
erase metal3
box <영역>
paint metal2      ;# 재도포
paint metal3
box <via 좌표>
paint via2        ;# 필요한 via만 다시
```

## 2.2 `erase`는 겹치는 도형을 관통한다 (다수 발생)

erase 박스가 지나가는 **모든** 도형이 잘린다. 의도한 대상만 지워지지 않는다.

**실제 사고**:
- `erase metal2` 박스가 `n_b0` 세로(x 83.30–83.70)를 관통 → 래더 절단, LVS 넷 불일치
- `erase metal3` 박스가 `XM_bias` met3 세로(136.80–137.40)를 절단 → `V_bias` 분리
- `erase metal2` 박스가 `V_bias_n` 트렁크·`sense_out` 세로를 동시 절단
- `erase metal3` 박스가 `VBE1` met3 세로 y −1.20…10.99 구간을 삭제 → **VBE1이 남북 두 섬으로 분리**, 추적에 수 턴 소모

**규칙**: erase 전에 그 박스에 걸치는 도형을 **덤프로 확인**한다. 지운 뒤 복구 목록을 명시적으로 관리한다.

## 2.3 층 겹침 paint → magic이 contact로 해석

met2 위에 met3를 칠하거나 그 반대일 때, 겹친 영역이 via로 해석되어 **층이 연결된 사례가 다수**.

**실제 사고**: `VBE1` met2 스트랩(y −2.30…−1.90) 동진 시 래더 met2 세로 3개를 관통 → `VBE1` = 167(래더 전체 흡수)

**규칙**: 다른 넷과의 교차는 **반드시 다른 층**으로. 같은 층 교차는 무조건 단락.

## 2.4 ★ 라벨이 다른 넷 위에 얹히면 "명명 단락" (최종 보스)

같은 이름의 라벨이 **서로 다른 노드 두 곳**에 붙으면 SPICE 추출에서 **하나의 노드로 합쳐진다**.

**실제 사고**: `VGND` 포트 라벨을 (60.00, −1.95)에 찍었는데, 그 좌표에 VGND 레일 met1(−2.90…−1.00)과 **VBE1 트렁크 met3(−2.40…−1.80)가 겹쳐** 있었다. 라벨이 met3 쪽에 붙어 `VBE1`이 `VGND`로 병합. 물리 단락이 아니라 명명 단락이라 DRC는 침묵하고, select도 라벨을 따라 전체로 퍼져 추적이 극도로 어려웠다.

**규칙**:
```tcl
label VGND metal1    ;# 층을 명시한다
```
라벨 좌표는 **그 넷의 도형만 있는 자리**를 고른다. 층이 겹치는 자리는 피한다.

## 2.5 `space` 층 유령 라벨 → `_uq0` 발생

도형이 없는 자리에 붙은 라벨은 노드를 만들지 못하고, 같은 이름의 진짜 노드를 `_uq0`로 밀어낸다.

**확인**:
```bash
docker exec <컨테이너> python3 -c "
import re
for l in open('.../bgr_mos.mag'):
    if re.match(r'\s*(r?label|flabel|port)\b', l): print(l.strip())
"
```
`rlabel space ...`가 유령. `erase labels`로 제거.

## 2.6 `feedback` 잔상 = 흰 해칭

`drc why` / `drc find`가 남기는 **주석 레이어**. 마스크가 아니므로 `see no *`로 안 지워지고 `select`로도 안 잡힌다.

```tcl
feedback clear
```

흰 해칭이 보이면 이것부터 의심.

## 2.7 같은 넷인데 애매하게 떨어짐 → `met1.2` 위반 (반복 발생)

0.02~0.08 간격은 "붙지도 떨어지지도 않은" 상태로 `met1.2`(0.14) 위반. **붙이거나 확실히 띄우거나** 둘 중 하나.

## 2.8 `met1.3b` — 넓은 met1 옆은 0.28

폭 또는 높이가 **3 µm 초과**인 met1은 무관 met1과 **0.28** 필요(기본 0.14의 2배).

**실제 사고**: 더미 tie를 통짜로 덮었더니 높이 10.88이 되어 이웃 riser와 0.12로 위반. **D 바 / S 바로 쪼개** 해결.

## 2.9 via 크기 · 모서리 감쌈

| 룰 | 값 |
| :--- | ---: |
| `via.1a` (via1 최소) | 0.26 |
| `via2.1a` (via2 최소) | 0.28 |
| `via2.2` (via2 간격) | 0.12 |
| met1/met2 감쌈 (`via.5a`, `met2.5`) | 0.03 |
| met3 감쌈 (`met3.4`) | 0.025 |

**모서리는 방향별 0.03으로 부족할 수 있다** — 0.05 이상 확보 권장. 단자 폭 0.23인 스트립에는 via1(0.26)이 안 들어가므로 **foot + riser로 넓힌 뒤** via를 얹는다.

## 2.10 3중 구조 탭 (p-tap / n-tap)

`psubdiffcont`를 직접 칠하면 컨택이 확산·li 경계까지 차서 `licon.7`·`li.5` 위반.

```tcl
box <외곽>
paint psubdiff
paint locali
box <외곽 −0.12 인셋>
paint psubdiffcont
box <외곽 −0.16 인셋>
paint viali
box <외곽>
paint metal1
```

## 2.11 `getcell` 배치 기준 = bbox 좌하단

`box <점>` 후 `getcell`하면 **셀 bbox의 LL이 그 점**에 놓인다. 셀 내부 rect는 중심 원점이지만 배치는 LL 기준.

**주의**: 셀 배치가 조용히 실패하는 경우가 있었다(매칭행 더미 `GHYW6X` 2개). 배치 후 반드시 인스턴스 수를 확인한다.

## 2.12 `save`는 최상위만 저장

`getcell`로 불러온 자식 셀(gencell 산물)은 미저장 상태로 남는다. magic 종료 시 "22 cells are modified" 메시지의 정체.

```tcl
writeall force
```

## 2.13 `select`의 동작

- **1회**: 커서 아래 폴리곤(타일) 하나
- **2회**: 동일 층 연결 영역
- **3회**: **전기적으로 연결된 넷 전체**

넷 추적에는 3회가 필요하다. magic이 긴 사각형을 수평 스트립 여러 개로 쪼개 저장하므로, 1회 선택 결과가 작다고 단절을 뜻하지 않는다.

## 2.14 `drc` 명령 범위

| 명령 | 범위 |
| :--- | :--- |
| `drc check`, `drc why` | **커서 박스 안** |
| `drc count`, `drc find` | **셀 전체** |

이분 탐색으로 위치를 좁힐 때 유용:
```tcl
box <절반 영역>
drc check
drc why
```

## 2.15 `error_p` 마커가 bbox를 부풀린다

`pfet_g5v0d10v5`, `nfet_01v8`에는 마커가 붙고 `nfet_g5v0d10v5`에는 안 붙는다. 마커 포함 bbox로 중심을 계산하면 실확산 기준과 어긋난다.

**실제 사고**: 행 B 중심을 마커 없는 값으로 계산해 배선 → 13개 소자 전부 G-S 단락. **DRC는 침묵**(touching = 병합).

## 2.16 `extract` 옵션은 세션에 잔류한다

`extract do resistance`·`no coupling` 등은 한번 켜면 이후 모든 `extract all`에 적용된다. 검증용 추출 전에는 **매번 명시적으로 설정**한다.

```tcl
extract style ngspice(si)
extract no coupling
extract no resistance     ;# 크래시 회피. 명시 필수
extract all
```

`do resistance`·`cthresh`·`rthresh`는 **기생 소자 출력에만** 영향을 주고 넷 연결성 판정에는 영향이 없다. 즉 재배선 후 넷 카운트·4포트 대조는 위 설정으로 하면 된다.

## 2.17 ★ `extract do resistance` 크래시 — magic 8.3.678에서 해결됨

**증상 (8.3.664)**: `extract all` 중 프로세스 사망, **exit code 139**. 마지막 출력 `Extracting R1`. 에러 메시지 없음.

**격리**: 빈 셀에 `sky130_fd_pr__res_high_po_0p69` (W=0.69, **L=3.650**) 하나만 놓아도 재현. 같은 pcell의 L=1.27 / 31.49 / 91.2 / 229.4는 통과. snake 유무 무관.

**원인** (magic 개발자 R. T. Edwards 확인): 특정 extraction style이 `xpolycontact`의 contact residue mask에 `xpolycontact` 자신을 포함시켜 `FindStartTile()`이 동일 인자로 자기 자신을 호출 → 무한 재귀 → 스택 오버플로.

**해결**: **magic 8.3.678에서 수정.** HEAD 빌드 필요.

```bash
cd /tmp && git clone --depth 1 https://github.com/RTimothyEdwards/magic.git
cd magic && ./configure --prefix=$HOME/.local && make -j4 && make install
```

★ PATH 우선순위상 `magic`을 그냥 치면 구버전(`/foss/tools/bin/magic`)이 잡힌다. **`$HOME/.local/bin/magic` 전체 경로로 호출할 것.**

★ 아울러 **R-C 추출에는 flatten이 필수**라는 지적을 받았다. 계층 상태의 R-C 추출은 의미 있는 결과를 보장하지 않는다. §10.2 참조.

## 2.18 중간 파일 오염 → `Nets output: 0`

**증상**: 재추출 시 `No device of type nmos found at ...`, `Couldn't find wire at ...`, `Nets output: 0`. 넷리스트가 생성되지 않는데 exit code는 0이다.

**원인**: `extresist`는 `.ext` / `.sim` / `.nodes`를 함께 읽는다. 이전 run이 **다른 `extract style`**(스케일이 다름)로 만든 파일이 남아 좌표가 어긋난다.

**대응**: 매 run 전 삭제.

```bash
rm -f <cell>_flat.ext <cell>_flat.sim <cell>_flat.nodes <cell>_flat.res.ext
```

## 2.19 ★ 넷리스트 후처리는 값 필드를 파괴할 수 있다

추출 넷리스트에는 `VGND.t12`, `sky130_..._JS995W_21.S` 같은 **점 포함 노드**가 나온다. ngspice가 점을 계층 구분자로 해석할 수 있어 밑줄 치환이 필요하다.

**실제 사고**: 치환 스크립트가 `=`를 포함하지 않은 토큰을 무조건 치환하도록 작성되어 **저항·용량 값의 소수점까지** 밑줄이 됐다.

```text
0.79685f → 0_79685f
10079.4  → 10079_4
```

post-layout `.op`에서 I_Q가 190.5 µA (정상 62.25의 **3.06배**), TC 170.7 ppm/°C (20배)로 나와 발각됐다. 행수·소자 개수는 맞았기 때문에 통과했었다.

**치환 제외 조건** (셋 중 하나라도 해당하면 원본 유지)

1. `=` 포함 토큰 (소자 파라미터)
2. 숫자 토큰: `^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?$`
3. `sky130_fd_pr__`로 시작하고 점이 없음 (모델명)

**검증 필수**: 원본 대비 **값 필드가 완전히 동일**한지 전수 대조. 개수만 보면 놓친다.

## 2.20 ★ `error_p` 마커가 셀 bbox를 부풀린다 (실제 사고)

`drc check` 실행 시 Magic이 자식 셀 내부에 에러 마커인 `error_p` 타일을 칠하고 `writeall force` 시 이 상태가 저장된다.
- **증상**: 자식 셀 box가 커짐 ➔ `getcell`은 bbox LL(좌하단) 기준 배치이므로 소자 배치가 어긋남.
- **실제 사고**: `res_high_po_0p69` 셀 box y가 `±2.715` ➔ `±2.915` (0.2 µm 팽창) ➔ 트림 4개가 0.2 µm 위로 배치 ➔ 패드가 `n_b0` 바와 접촉하여 `n_b0` / `n_b2` / `VGND` 단락 발생.
- **규율**: `getcell` 수행 전 `.mag` 파일의 `box` 수치를 확인하고, 배치 후 origin(원점) 좌표를 실측 검증한다. (마커를 지워도 다음 `drc check` 시 다시 생기므로 보정이 실용적이다.)

## 2.21 RPM 생성 기전 (`sky130A.tech` 1745행)

```magic
templayer rpm_generate
  bloat-all xhrpoly,uhrpoly xpc
  grow 620 ; shrink 420
```
- **연산**: 순확장 +0.200 µm, 갭 1.24 µm 이내 도형 병합(Merge).
- **단일 폴리**: 폭 0.69 µm 단독 폴리는 RPM 폭 1.09 µm < `rpm.1a` (1.27 µm)로 **위반**.
- **다중 컬럼**: 피치 1.17 µm (갭 0.48 µm)는 상호 병합되어 통과. 인접 저항끼리도 갭 0.08 µm 이면 병합.
- ★ **핵심 룰**: 위반은 "이웃 없이 노출된 탭/단독 구간"에서만 발생한다. 병합은 양 끝의 최대 높이 하나만 외부로 노출된다. 슬롯 1칸을 건너뛰면 갭 1.25 µm > 1.24 µm 로 끊긴다.

## 2.22 PSDM 생성 기전 및 locali/metal1 분리

$$\text{psdm} = \text{확산}(\texttt{psubdiff}/\texttt{psubdiffcont}) + 0.125\ \mu\text{m}$$
- `locali` / `metal1`은 `psdm`을 만들지 않는다 ➔ 이설 작업 시 이 레이어들을 함부로 건드려서는 안 된다.
- **실제 사고**: 링 좌측 밴드 이설 시 `locali`까지 함께 옮겨 PNP base 브리지를 절단, `li.3` 위반 10건 발생. 확산만 옮기고 `locali`는 넓게 두는 것이 정답.

---

# 3. 작업 규율 (LVS를 닫은 방법)

## 3.1 워크플로우

```text
정본 → cp run_* 사본 → 사본으로 시뮬
정본 .control 직접 수정 금지
시뮬 전 grep으로 소자값 대조
```

## 3.2 매 단계 검증 루틴

```tcl
save bgr_mos
extract all
ext2spice lvs
ext2spice -o chk_XX.spice
```

```bash
docker exec <컨테이너> python3 -c "
import re
from collections import Counter
s=re.sub(r'\n\+\s*',' ',open('.../chk_XX.spice').read())   # 연속행 병합 필수
print('uq:', sorted(set(re.findall(r'[\w]+_uq\d+', s))))
for l in s.splitlines():
    t=l.split()
    if t and '<셀해시>' in t[0]: print(' ', t[0].split('_')[-1],'|',t[1],t[2],t[3],t[4])
for n in ('넷1','넷2',...): print(f'  {n:12s}',len(re.findall(r'\b'+n+r'\b',s)))
"
```

**핵심**:
- `re.sub(r'\n\+\s*',' ',s)`로 SPICE 연속행을 병합하지 않으면 파싱이 깨진다
- **4포트 전부 출력**(D S G B) — 하나만 봐서는 단락을 못 잡는다
- **`_uq` 목록을 매번 확인** — 중복 라벨·분리 노드의 조기 경보

## 3.3 넷 카운트 해석

추출 넷리스트의 카운트는 **소자 단자 수**이며 라벨은 포함하지 않는다. `.subckt` 핀 줄에 나오는 이름은 +1 된다.

예: `VREF_LOW` 4 = `XM_bot5` m=4의 드레인 4개. (핀 줄 포함 시 6)

## 3.4 DRC 루틴 및 세션 설정 규약

> [!IMPORTANT]
> Magic 재시작 시 `drc(fast)`로 돌아갑니다. 매 세션 시작 시 가장 먼저 아래 명령을 실행해야 합니다:
> ```tcl
> drc style drc(full)
> drc euclidean on
> ```
> `fast` 모드에는 Latch-up(`LU.2`/`LU.3`) 검사 등이 비활성화되어 있어 유효하지 않으며, TT precheck는 `full` 모드를 씁니다.

```tcl
drc style drc(full) ;# 세션 시작 시 필수
drc euclidean on
drc off             ;# 편집 중 비활성화 (속도)
... 편집 ...
drc on
box <영역>
drc check
drc catchup
drc count           ;# 셀 전체
drc why             ;# 박스 내 룰명
drc find            ;# 위치 순회 → box로 좌표 확인
```

## 3.5 `met1.6` (최소 면적 0.083 µm²)의 활용

배치 직후 다수 발생하고 배선하면 사라진다. **배선 완료 후에도 남는 `met1.6` = 미연결 단자**라는 신호로 쓸 수 있다. 최종 0이 목표.

## 3.6 단락 추적 절차 (VBE1 사건에서 확립)

1. `_uq` 확인 → 분리인지 병합인지 판정
2. 넷 카운트로 어느 넷이 흡수됐는지 역산 (예: 167 = 5 + 24 + 46×3)
3. **소자 유형별 Counter**로 어떤 그룹이 딸려왔는지 확인
4. **이분 절단** — 넷의 목을 자르고 `select`×3으로 어느 쪽이 오염됐는지 판정
5. 좁혀진 구역 **전층 덤프**로 접점 특정
6. 절단 복구 목록을 명시적으로 관리 (복구 누락이 새 버그를 만든다)

**교훈**: 넷이 여러 경로로 이어져 있으면 한 곳을 잘라도 분리되지 않는다. `VBE1`은 남측 트렁크와 met3 가로 두 경로가 있어 첫 절단이 무효였다.

## 3.7 라벨 규율

- **A/B/C/D/E 식별자의 정본은 `designs/bgr_ldo/ldo/OPEN_ITEMS.md`**. 인용 전 확인, 신설 시 등록 먼저
- 정의 없는 라벨을 근거로 쓴 문장은 무효 (rule 5의 "조건 없는 수치는 무효"와 같은 취지)

---

# 4. 셀 기하 — 좌표 계산 정본

## 4.1 MOS 셀 (전 셀 공통 구조)

**셀 원점 = 중심.** rect 좌표가 대칭(±)으로 나온다.

| 요소 | 상대 좌표 (hx = 실폭/2, hy = 실높이/2) |
| :--- | :--- |
| D 스트립 (좌) | x −(hx−0.03) … −(hx−0.26) |
| S 스트립 (우) | x +(hx−0.26) … +(hx−0.03) |
| 스트립 y | ±(W/2) 부근 — **셀마다 실측 필요** |
| G 스트랩 | x ±(hx−0.31), y ±(hy−0.235) … ±(hy−0.005) |

**게이트 컨택은 상·하 양쪽 또는 한쪽만** 선택 가능(gencell 옵션). 양쪽이면 D/S가 상하 어디로도 못 빠져나간다.

## 4.2 셀 실측 방법

```bash
docker exec <컨테이너> python3 -c "
f='<셀>.mag'
lay=None
for l in open(f):
    if l.startswith('<< '): lay=l.strip()[3:-3]
    elif l.startswith('rect ') and lay in ('metal1','poly','locali','viali'):
        v=[int(x)/200 for x in l.split()[1:5]]
        print('%-8s x %7.3f..%7.3f  y %7.3f..%7.3f'%(lay,v[0],v[2],v[1],v[3]))
"
```

**`.mag` 좌표는 ÷200** (internal → µm).

**주의**: `save aux`는 부모만 저장한다. 자식 셀 덤프 전에 `writeall force` 필수 — 안 하면 이전 파라미터의 잔재를 읽는다(실제로 11배 차이가 난 적 있음).

## 4.3 셀 배치 후 확인

```tcl
select clear
select cell <인스턴스명>
box
```

**`.mag`의 `transform` 값은 판독 착오가 반복 발생**했다. `select cell` + `box` 실측만 신뢰한다.

## 4.4 저항 셀 (`res_high_po_0p69`, W=0.69 고정)

**셀 원점 = 중심.** 패드 구조:

| 요소 | 값 |
| :--- | :--- |
| 패드 폭 | 0.59 (컬럼 중심 ±0.295) |
| 패드 높이 | 2.105 |
| 컬럼 피치 | 1.17 |
| N 짝수 | 양단자 **모두 하단** |
| N 홀수 | 좌단자 하단, 우단자 **상단** |

**서펜타인 굴곡 보정은 N에 대해 단조가 아니다:**

| N | 굴곡당 증분 (µm) |
| ---: | ---: |
| 2 | **+1.26** |
| 4 | +0.1927 |
| 7 | +0.1438 |
| 8 | **−0.0386** |

**단일 N의 계수를 다른 N에 외삽하면 부호까지 틀린다. N별 2점 실측이 정본.**

저항 모델: `R = 471.0·l + 525.7` (l = 환산 길이). 모델은 유효하고 어긋나는 것은 l 값(레이아웃 치수 환산)이다.

## 4.5 다중 핑거(`nf`) 셀은 결선 불가

`nfet_01v8` W=10 L=0.15 `nf=22`(`G5UXWG`)를 검토한 결과:

- 확산 스트립 폭 0.23 < via1 최소 0.26 → 스트립 위 via 불가
- A 스트립 중심과 최근접 게이트 컨택 중심 간격 0.24 → 핑거 0.14 + 게이트 0.29 빼면 **여유 0.025** → `met1.2`(0.14) 미달
- li 레벨에도 콤이 없고 0.010 겹침 발생

**결론: `nf ≥ 2`는 met1/li 어느 층으로도 결선 불가.** `nf=1` 유닛 다수 배치가 유일한 해.

**`nf=1` 유닛 결선 패턴** (`JS995W`, 0.730 × 10.570, 게이트 상단만):

```text
피치 1.30  (riser 간 0.40 확보: P − 0.90 ≥ 0.14)

y Yb+10.29…10.69  게이트 바 (met1, 전 유닛 관통)  → TRIMn
y Yb …  +10.13    확산 스트립
y Yb−0.70 … Yb    S 핑거 (met1, 0.34 확폭)  ┐ via1
y Yb−0.75…−0.25   S 콤 (met2)              ┘
y Yb−1.20 … Yb    D 핑거 (met1, 0.23)      ┐
y Yb−1.60…−1.20   D 콤 (met1)              ┘
```

D는 met1, S는 met2로 층을 나눠 교차 해소. Yb = 셀 LL_y + 0.13.

---

# 5. 더미 배치 절차 (확립된 방법)

1. 셀 `.mag`에서 **metal1 rect 실측** → 단자 rel 좌표 확정 (원점이 중심인지 LL인지도 여기서 판정)
2. 실소자와 **간격 0.30**으로 배치
3. tie는 **D 바 / S 바 두 개**로 나눠 G 스트랩과 겹쳐 병합 — 통짜로 덮으면 `met1.3b` 발동
4. 이웃 riser와 **0.14** (넓은 met1이면 0.28)
5. 전원은 로컬 탭 또는 레일 직결
6. 검증: 4포트가 전부 같은 넷인지 확인

**확산 스트립(`mvnsubdiff` 등)은 더미의 절반만 커버한다** — LOD/STI 응력과 WPE는 잡지만 poly 피치·식각 밀도로 인한 게이트 CD 변동은 못 잡는다. 실소자 더미가 정답.

**행별 필요성 판단**: 배정이 대칭이면 스트립으로 충분, **비대칭이면 더미 필수**(예: 행 C/D는 슬롯 0·3이 둘 다 XM3라 XM3만 가장자리를 2번 겪음).

---

# 6. 현 레이아웃 좌표 정본

## 6.1 존 외곽

```text
BGR 존:  x −1.80 … 143.40  (145.20 ≤ 타일 145.36, 여유 0.16)
         y −36.70 … 79.20  (115.90)
trim_sw: y −34.30 … −6.31  (BGR 존 내부, LDO 존 상단에 해당)
```

## 6.2 컬럼 1 코어 (x −1.80 … 65.37)

| 행 | 셀 | 개수 | LL |
| :--- | :--- | ---: | :--- |
| A | `9KY2DD` | 13 | (0 + 4.88i, 56.26) |
| B | `3XTGEW` | 13 + 더미 2 | (13.00 + 2.88i, 40.76) |
| D | `YKUQM3` | 4 + 더미 2 | (13.94 + 2.88i, 23.88) |
| C | `FV4ZM9` | 4 + 더미 2 | (9.94 + 4.88i, 0.00) |

- 13슬롯 공통중심: top1/bot1={0,5,8,11}, top2/bot2={2,3,7,12}, top5/bot5={1,4,9,10}, tap=6
- 채널 A↔B 4트랙: net3 52.10 / net6 53.00 / net2 53.90 / net_tap 54.80 (채널 N-tap y 54.60..55.50, x 0.15–63.65 추가로 LU.3 26건 해소)
- 행B 하부 N-tap 전폭 연장: x 0.30–63.50 (LU.3 6건 해소)
- 채널 B↔D 5트랙: V_mid1 35.95 / V_gate_top 36.85 / VREF_LOW 37.75 / IB_EA 38.65 / V_bias 39.55
- nwell: −1.80 … **65.37** (동단 65.600 ➔ 65.370 수정으로 diff/tap.18,20 해소) × **39.40** … 78.60
- VAPWR 레일 met1: y 77.60–79.20
- VGND 레일 met1: y −2.90 … −1.00 (동쪽 x 143.00까지)
- `V_mid1` 세로 링크: **met3 x 12.30–12.70** (met1에서 이설)

**더미**: 행B `3XTGEW_13/14` (LL 10.91/50.44), 행C `FV4ZM9_4/5` (LL 5.06/29.46), 행D `YKUQM3_4/5` (LL 10.91/25.49, 로컬 p-tap x 10.01–10.61 / 28.37–28.97), 행A는 `mvnsubdiff` 스트립(좌 −1.47…0.03, 우 63.77…64.95)

## 6.3 컬럼 2 (x 65.80 … 120.50)

- **PNP 5×5** LL (67.0 + 4.6i, 4.6j). QA = `_12` (중심 78.19, 11.19), QB = 3×3 테두리 8개, 더미 16
- base li 스텁 + 버스 met1 4줄 (71.29 / 75.89 / 80.49 / 85.09), 4열은 링 직결
- VBE8 링 met2 (73.40–82.98 × 6.40–15.98)
- **매칭 행 y 40**: 더미`GHYW6X_0`(67.00) / R6b(69.34) / R7a(78.70) / R1(`Y74LVQ`, LL y **39.800**로 이동하여 rpm.1a 3건 해소) / R7b(97.42) / R6a(106.78) / 더미`GHYW6X_1`(116.14). 중심 92.50
- **남쪽 y 3**: XR_cn(`UKBC2Qa`와 셀 교체 및 수평 반전 적용, rpm.1a 2건 해소) / 더미 / R2fix`YJEXGM`(102.00) / 더미 / 트림 R2b0~b3 = `F6JLQ4` / `T8D7K5` / `QCK2SQ` / `5VVEC7` (좌우 미러링 적용으로 rpm.1a 1건 해소)
- p-tap 링 2개: 매칭 65.80–119.20 × 38.80–59.13, 남쪽 89.80–119.10 × 1.80–35.59 (링 좌변 확산 x **89.900**로 0.100µm 외측 이동, locali는 89.800 유지하여 psdm.1 9건 해소)

**저항 단자 절대좌표 (실측)**

| 저항 | 컬럼 중심 x | 하단 패드 y | 상단 패드 y |
| :--- | ---: | :--- | :--- |
| R2b0 `F6JLQ4` | 114.045 | 3.030 – 5.135 | 6.295 – 8.400 |
| R2b1 `T8D7K5` | 115.215 | 3.030 – 5.135 | 8.675 – 10.780 |
| R2b2 `QCK2SQ` | 116.385 | 3.030 – 5.135 | 13.445 – 15.550 |
| R2b3 `5VVEC7` | 117.555 | 3.030 – 5.135 | 22.985 – 25.090 |
| R2fix `YJEXGM` | 좌 102.050–102.640 / 우 110.240–110.830 | 3.030 – 5.135 | (양단 하단) |
| XR_cn `G8MLLQ` | 좌하 91.050–91.640 (y 3.03–5.135) / 우상 98.070–98.660 (y 19.135–21.240) | | |

## 6.4 컬럼 3 (x 119.40 … 143.40)

| 밴드 | y | 내용 |
| :--- | :--- | :--- |
| P1 | 0 – 11 | bias_mir 4 + cn_mir 1 (`3XTGEW_15~19`, LL 120.70 + 2.88i, 중심 122.32 + 2.88i) │ XM_bias `AVQM49_0` (LL 136.50) |
| P2 | 12.5 – 17.3 | su1c/b/a = `LESTS2_0/1/2` (LL 120.70, y 12.50/14.22/15.94, 중심 x 131.32) |
| N1 | 22 – 34.9 | bias_n `YKUQM3_6~9` (LL 120.70 + 2.88i, 중심 121.99 + 2.88i, y중심 27.44) │ pd `BHYBL9_0` (LL 133.00, 중심 134.29/28.44) │ cn_d1/d2 `HZW5KE` (LL 136.50, y 22.00/25.50) │ su_n1 `K9TBKL` (LL 136.50, y 29.50) |
| N2 | 36 – 37.9 | su_n2 `4H6C7W` (LL 120.70, y 36.00, 중심 130.99/36.94) |

- nwell: 120.20 – 142.30 × −0.50 – 17.90
- n-tap + VAPWR 레일 met1: y 11.15 – 12.05, x 120.60 – 142.00
- NMOS p-tap met1: y 20.20 – 21.10, x 120.70 – 142.80
- trim p-tap met1: y 39.70 – 40.60, x 120.70 – 142.85
- VGND 세로 met1: x 142.40 – 142.80, y −1.20 … 40.60

**컬럼 3 met2 가로 트랙** (x 120–142를 가로막으므로 세로 통과 불가):

| y | 넷 |
| :--- | :--- |
| −0.90 … −0.50 | V_gate_top |
| −0.35 … 0.00 | V_bias_n (P1 D) |
| 13.01 – 13.41 | net7 |
| 15.30 – 15.60 | net8 |
| 16.42 – 16.88 | sense_out |
| 17.10 – 17.60 | V_bias_n (su1 G) |
| 23.40 – 23.80 | V_casc_n (cn_mir D) |
| 26.00 – 26.60 | net9 |
| 30.20 – 30.60 | V_gate_top (su_n1 D) |
| 32.95 – 33.45 | V_bias_n (N1 G) |
| 33.95 – 34.45 | V_bias_n (N1 D) |
| 34.95 – 35.45 | V_bias (N1 D) |

`V_bias_n` 트렁크 met2 세로: **x 119.40 – 119.80**, y −0.35 … 34.45

## 6.5 ★ met3 전역 트랙 (T 스택) — 순서 규칙

**규칙: 상위(높은 y) 트랙의 서편 riser는 하위 트랙 서단보다 서쪽, 동편 descent는 하위 트랙 동단보다 동쪽.**

이걸 어기면 met3끼리 교차해 단락. 실제로 여러 번 위반했다.

| 트랙 | y | x 범위 | 서편 riser | 동편 descent |
| :--- | :--- | :--- | :--- | :--- |
| T1 V_gate_top | 59.60 – 60.20 | 60.00 – 121.90 | 60.00 – 60.40 | 121.30 – 121.90 |
| T2 V_bias | 60.80 – 61.40 | 57.50 – 131.90 | 57.50 – 58.10 | 131.30 – 131.90 |
| T3 V_casc_n | 62.00 – 62.60 | 55.00 – 139.90 | 55.00 – 55.60 | 139.30 – 139.90 |
| T4 VAPWR (폭 2.0) | 63.20 – 65.20 | 49.60 – 143.00 | 49.60 – 53.00 | 141.00 – 143.00 |

**컬럼 3 met3 세로** (충돌 방지용 x 슬롯):

| x | 넷 | y 범위 |
| :--- | :--- | :--- |
| 121.30 – 121.90 | V_gate_top | −0.90 … 60.20 |
| 126.55 – 127.05 | V_casc_n (cn_mir D) | 0.10 … 23.80 |
| 131.30 – 131.90 | V_bias | 35.00 … 61.40 |
| 133.50 – 133.90 | VBE1 | −2.40 … 22.20 |
| 136.80 – 137.40 | XM_bias | 0.15 … 35.45 |
| 139.30 – 139.90 | V_casc_n | 23.30 … 62.60 |
| 141.00 – 143.00 | VAPWR | 11.25 … 65.20 |

## 6.6 `VBE1` 경로 (가장 복잡)

```text
QA 이미터 (78.19, 11.19) ─ via1/via2 ─ met3 가로 y 10.99–11.39 (x 15.30–78.44)
  ├─ met3 세로 x 69.30–69.70 (y 11.39 … 40.05) → R6b 좌단자
  └─ x 68 우회로 (층 교대):
       met3 스텁 68.10–68.70 (y −2.40 … −1.37)
       ↕ via2 (68.26–68.54, y −1.75…−1.47)
       met2 A 68.20–68.60 (y −1.85 … 3.36)      ← net1 met3 회피
       ↕ via2 (y 3.00–3.28)
       met3 홉 68.10–68.70 (y 2.90 … 4.50)      ← VREF_LOW met2 회피
       ↕ via2 (y 4.12–4.40)
       met2 B 68.20–68.60 (y 4.04 … 11.43)
       ↕ via2 (y 11.05–11.33) → met3 가로
  └─ 남측: met3 트렁크 30.00–133.96 (y −2.40 … −1.80)
       ├─ 서단 met3 패드 30.60–31.50 (y −2.40…−0.78) ─ via2 ─ met2 스트랩 13.00–31.60 (y −1.30…−0.70) → XM3 S ×2
       └─ 동단 → 컬럼3 met3 세로 133.50–133.90 → via2/via1 → pd 게이트
```

**x 68 대역이 met1/met2/met3 모두 점유**되어 층 교대가 불가피했다:
- met3: `net1` 가로 (y −0.48…−0.08, x 19.24–97.10)
- met2: `VREF_LOW` 바 (y 3.50–3.90)
- met1: PNP base 스텁 (x 69.30–71.49)

## 6.7 trim_sw (LDO 존)

`JS995W` × 88, 피치 1.30

| 스위치 | LL | D 콤 met1 | S 콤 met2 | 게이트 바 met1 |
| :--- | :--- | :--- | :--- | :--- |
| b0 | (86.00, −17.00) | 85.00–113.66, y −18.47…−18.07 | 86.35–114.10, y −17.62…−17.12 | 86.10–113.90, y −6.71…−6.31 |
| b1 | (115.00, −17.00) | 114.00–142.66, 동일 y | 115.35–143.15, 동일 y | 115.10–142.90, 동일 y |
| b2 | (86.00, −31.00) | 85.00–113.66, y −32.47…−32.07 | 86.35–**114.70**, y −31.62…−31.12 | 86.10–113.90, y −20.71…−20.31 |
| b3 | (115.00, −31.00) | 114.00–142.66, 동일 y | 115.35–143.15, 동일 y | 115.10–142.90, 동일 y |

- trim p-tap met1: y −34.30 … −33.40, x 85.00 – 143.40 (88유닛 바디 타이)
- VGND 세로 met1: x 84.20 – 84.60, y −34.30 … −1.20 (+ 점퍼 84.20–85.20, y −34.20…−33.60)
- **래더 자동 병합**: b0.S와 b1.D가 같은 `n_b1`이라 x 114.00–114.10에서 met1 브리지(113.90–114.55, y −18.55…−17.50)로 병합. b2.S↔b3.D(`n_b3`)도 동일

**래더 하강 경로** (y −17.4 / −31.4 대역은 S 콤이 x 86.35–114.10 및 115.35–143.15를 점유 → 자유 통로는 **x 114.29–115.21(0.92)** 뿐)

| 넷 | 경로 |
| :--- | :--- |
| n_b0 | met1 바(110.30–114.34, y 5.30–5.70) → via1(111.00–111.26) → met2 세로 110.95–111.35 → y −3.3 가로 서진 → x 83.30–83.70 세로 → y −18.27 가로 → via1(85.15–85.41) → b0 D 콤 |
| n_b1 | met1 L(R2b0↔R2b1) → via1(113.79–114.05, y 7.10–7.36) → met2 세로 113.70–114.10 (y −17.12 … 7.42) → b0 S 콤 |
| n_b2 | via1(115.68–115.94, y 3.62–3.88) → met2 세로 115.60–116.00 (y −24.60 … 3.88) → b1 S 콤 |
| n_b2 (b2.D 분기) | 위 세로 → 가로 114.86–116.00 (y −25.00…−24.60) → 세로 114.86–115.16 (y −32.70…−25.00) → 최하 가로 **112.80**–115.16 (y −33.10…−32.70) → met2 패드 112.80–113.46 → via1 **112.90–113.36** (y −32.40…−32.14) → b2 D 콤 |
| n_b3 | via1(116.24–116.50, y 13.97–14.23) → met2 가로 **114.24**–116.60 (y 13.90–14.30) → 세로 **114.24–114.72** (폭 0.48, y −31.12 … 14.30) → b2 S 콤 |

**★ 트림 균등화 재배선 (rev2에서 완료)**

DNL 기여를 줄이기 위해 두 분기를 고쳤다. 좌표는 위 표에 반영됨.

| 분기 | 조치 | R (typ) |
| :--- | :--- | ---: |
| P4 (n_b2 → b2.D) | 최하 가로 서단 99.90 → **112.80** 단축, via1 착지점 이동 | 26.71 → **22.37** |
| P5 (n_b3 → b2.S) | 세로 폭 0.30 → **0.48** (114.24–114.72) | 24.24 → **16.96** |

코리도 여유: 신 n_b3 세로 서변 114.24 ↔ b0 S 콤 met2(→114.10) **0.14** / 동변 114.72 ↔ n_b2 세로(114.86) **0.14**. 양쪽 최소치라 **더 이상 확장 불가**.

## 6.8 포트 (8핀)

```text
.subckt bgr_mos VGND VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3
```

| 포트 | 위치 | 라벨 좌표 |
| :--- | :--- | :--- |
| VREF_LOW | met2 세로 62.60–63.00 (y −36.70 … 38.25) + 남측 바 62.60–136.82 (y −36.70…−36.30) | (136.62, −36.50) |
| IB_EA | met2 세로 63.40–63.80 (y −35.90 … 39.15) + 남측 바 63.40–117.50 (y −35.90…−35.50) ※※ | (117.30, −35.70) |
| VAPWR | 컬럼1 레일 | (30.00, 78.40) |
| VGND | 컬럼1 레일 met1 | **x −0.50…−0.15, y −2.90…−1.50 (metal1)** ※ |
| TRIM0–3 | 게이트 바 | (100.00, −6.51) / (130.00, −6.51) / (100.00, −20.51) / (130.00, −20.51) |

※ `VGND` 라벨은 (60.00, −2.70)에 찍으려 했으나 `label` 명령이 안 먹고 **기존 라벨이 남았다.** `.mag` 실측 = `rlabel metal1 -100 -580 -30 -300 1 VGND` → x −0.50…−0.15, y −2.90…−1.50. 레일 서단이라 전기적으로 정상.

**★ 라벨 사고 이력**: (60.00, −1.95)에 찍었을 때 그 좌표에 VGND 레일 met1과 **VBE1 트렁크 met3가 겹쳐** 라벨이 met3에 붙어 `VBE1`이 `VGND`로 명명 단락됐다. §2.4 참조.

※※ **`IB_EA` 남측 바는 삭제 예정.** 핀 미인출 확정으로 목적지가 사라졌다(§7.1). 탭 → VNB1 다이오드 경로는 유지해야 하므로 **삭제 범위는 EA 배치 확정 후**에 정한다. 미리 지우지 말 것 — erase 관통 사고가 반복됐다(§2.2, 부록 B).

**핀 x 정합**: ua[0] = **VREF sense** (타일 x 136.62), ua[1] = **VDDC(VLDO) sense** (x 117.30). 둘 다 하단 met4 핀. `IB_EA`는 핀 아님.

## 6.9 넷 카운트 기준값 (LVS 통과 시점)

| 넷 | 값 | 넷 | 값 |
| :--- | ---: | :--- | ---: |
| VBE1 | 5 | V_gate_top | 25 |
| net1 | 4 | V_bias | 17 |
| net9 | 2 | V_bias_n | 13 |
| net2/net3/net6 | 8 | V_casc_n | 7 |
| net_tap | 2 | V_mid1 | 10 |
| net4/net5 | 4 | VAPWR | 64 |
| VREF_LOW | 4 | VGND | (다수) |
| IB_EA | 1 | n_b0 | 24 |
| cn_mid | 3 | n_b1/n_b2/n_b3 | 46 |
| V_su_mid | 3 | sense_out | 3 |

---

# 7. 플로어플랜

## 7.1 TinyTapeout 제약

```text
타일: tt_analog_1x2_3v3.def
DIEAREA: 145.36 × 225.76 µm
met5 금지
ua[0] = VREF sense      (x 136.62)  ← VREF_LOW
ua[1] = VDDC(VLDO) sense (x 117.30)  ← LDO 출력. 트림 측정 기준
하단 met4 핀
```

**★ `IB_EA`는 핀으로 인출하지 않는다 (확정)**

**820 MΩ 노드**라 패드 누설이 TC를 훼손한다. 핀 예산 문제가 아니라 **회로적 금지** 사항이다. `bgr_core` 서브회로 포트로는 남지만 타일 핀에는 나가지 않는다.

rev3까지 §7.1에 `ua[1] = VDDC (x 117.30) → IB_EA`로 적혀 있었는데 **전사 오류**다(자기모순: VDDC라 써놓고 IB_EA를 연결). 정본은 `00_인계_통합.md` §5.4.

**귀결**: 현 레이아웃의 `IB_EA` 남측 가로(x 63.40–117.50, y −35.90…−35.50)는 x 117.30 핀으로 가려던 것이라 **목적지가 사라졌다.** 삭제 대상이며, 비는 x 117.30 트랙은 VDDC 인출에 재사용한다. 단 탭 → VNB1 다이오드 경로는 유지해야 하므로 **삭제 범위는 EA 배치 확정 후**에 정한다. `IB_EA`는 배선 저항·용량에 둔감하므로 길어도 무방하다.

## 7.2 MiM (met3–met4) 배분

**총 캡 55개** (C_out 44 + Cc 4 + Cbyp 3 + C_slew 4), 각 18.31□

| 영역 | 슬롯 | 조건 |
| :--- | ---: | :--- |
| LDO 존 뱅크 7×7 | 49 | LDO 회로는 met1/met2만 사용 |
| 컬럼 2 상공 | 6 | **컬럼 2는 met3 금지** (2열 × 3행, y 0–56.4) |

**컬럼 2 met3 제거 대상** (④c, 미완):
- VBE1: 세로 x 69.30–69.78, 가로 y 10.99–11.39 (x 15.30–78.44), 서측 세로 15.30–15.70
- VBE8: 세로 x 88.30–88.70
- net1: 가로 y −0.48…−0.08 (x 19.24–97.10), 세로 96.70–97.10

단, **VBE1 남측 간선(y −2.40…−1.80)과 T트랙은 컬럼2 상공을 통과**하므로 MiM 슬롯 배치와 좌표 조정 필요. 컬럼2 캡은 y 57.9 미만에 두면 T트랙(59.6↑)과 충돌하지 않는다.

## 7.3 LDO 존

```text
y < −36.70 (BGR 존 아래). li/m1/m2만 사용.
trim_sw는 이미 y −34.30 … −6.31 에 배치됨 (BGR 존 내부)
```

배치 예정: EA / pass / RO / div16 / snk·clamp·슬루 / 트림 버퍼 / 캡뱅크 7×7

**EA 입력 인터페이스**:
- `VREF_LOW` → EA Vinp. 그리고 ua[0] 핀(x 136.62)까지 인출 — **남측 바 유지**
- `IB_EA` → EA VNB1. **내부 넷, 핀 인출 없음** (§7.1)
- `TRIM0–3` → LDO 존 트림 버퍼(`XM_tip/tin`, VDPWR)와 게이트 바 직결. **같은 존이라 BGR로 끌어올릴 필요 없음**
- `VDDC` → ua[1] 핀(x 117.30). `IB_EA` 남측 바가 비우는 트랙 재사용

**VREF_LOW 주의**: DC 전류는 미러 1브랜치 ≈ 2.5 µA뿐이라 IR은 0.25 mV 수준으로 여유. 실제 위험은 **커플링**(RO·pass 게이트 라인)이므로 노출 구간에서 이격 확보. 폭 1.0 met2 권장.

**`Cbyp` 배치**: `VREF_LOW` 바이패스 MiM은 **`VREF_LOW`에 물리적으로 가깝게** 둔다. 멀면 바이패스 효과가 죽는다.

**경로 주의**: VREF_LOW 남하가 **trim 블록(x 86–143.6, y −32…−6)의 met2 콤을 관통**하지 않도록 핑거 갭(피치 1.30 중 0.56 빈 구간) 또는 블록 서편(x < 85) 우회 필요.

## 7.4 남서 포켓 — EA 입력단 후보지

```text
x −0.44 … 82.05,  y −35.24 … −4.18   (82.5 × 31.1 µm)
```

BGR 존 남서쪽 빈 공간. 안에 있는 기존 도형은 **두 줄뿐**이다.

| 도형 | x | 용도 |
| :--- | :--- | :--- |
| `VREF_LOW` met2 세로 | 62.60–63.00 | 포트 하강 |
| `IB_EA` met2 세로 | 63.40–63.80 | 포트 하강 |

**동쪽 경계 여유**: `n_b0` 서편 우회 met2(83.30–83.70)와 1.25 / `VGND` met1 세로(84.20)는 층 무관.

**상공(met3/met4)이 비어 있다** — `Cbyp` MiM 슬롯 후보. `VBE1` met3 트렁크(y −2.40…−1.80)는 포켓 북쪽 경계 밖이라 간섭 없음.

### ★ 채널 문제

위 두 세로가 포켓을 **서 62.2 / 동 18.25**로 가른다. `m=24` 유닛을 피치 2.88로 한 행에 놓으면 더미 포함 26 × 2.88 = **74.9 µm**라 서편만으로는 안 들어간다.

**제안 (미검증)**: `VREF_LOW`·`IB_EA`를 포켓 진입 직전(y −5 대역)에서 동쪽으로 꺾어 x 80.5 부근에서 하강 → x −0.44 … 80.3이 통짜로 열린다.

**검산 필요**: `VREF_LOW` 세로를 x 80 대역으로 올리면 y 6.4–16.0 구간에서 **`VBE8` met2 링(73.40–82.98)과 충돌**한다. 꺾는 지점은 반드시 포켓 상단 근처여야 한다.

### EA 분할 제약 (BGR 확인분)

**하드 제약 — 다이오드 ↔ 미러 쌍 분리 금지**

| 쌍 |
| :--- |
| `pb1_diode` ↔ `XM3` |
| `nb1_diode` ↔ `XM4`/`XM5` |
| `nb2_diode` ↔ `XM6`/`XM7` |

이 쌍이 갈리면 미러 정합이 깨진다.

**권고 경계**: 포켓에는 **`XM1`/`XM2` 입력 페어만**. 테일·바이어스·미러·출력단·보상저항(L303/242/87)은 LDO 존.

**경계 통과 넷 중 `net2`/`net3`만 대칭 라우팅 필수** — 길이·폭·via 개수를 좌우 동일하게. 여기서 비대칭이 나면 오프셋이 생긴다.

**대안**: 자신 없으면 **EA 통짜 배치 + `VREF_LOW` 실드 라우팅**이 안전하다. 분할의 이득(배선 단축)보다 대칭 라우팅 실패 위험이 크다고 판단되면 통짜로 가고 포켓은 MiM 슬롯 등으로 쓴다. **이 판단을 먼저 내리고 시작할 것.**

### 배치 제약

| 항목 | 내용 |
| :--- | :--- |
| 열 | BGR 자체는 205 µW라 무관. **`pass` FET(3 mW)을 포켓에서 멀리.** 열 구배가 입력 페어를 가로지르면 오프셋 드리프트 → **공통중심 축을 열 구배와 수직**으로 |
| 노이즈 | RO(링 110.89 MHz, 분주 출력 6.93 MHz)를 포켓·BGR에서 이격. **가드링 권장** |
| 층 | 포켓도 LDO 존 규칙 적용 — li/met1/met2만 |

---

# 8. LVS 절차

```bash
# 1. 추출
# magic 내에서:
#   save bgr_mos ; extract all ; ext2spice lvs ; ext2spice -o bgr_mos.spice

# 2. netgen
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c '
cd /foss/designs/designs/bgr_ldo/layout/bgr_core
netgen -batch lvs "bgr_mos.spice bgr_mos" \
  "/foss/designs/designs/bgr_ldo/bgr/bgr_core_lvs.spice bgr_core" \
  /foss/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl lvs_bgr.out 2>&1 | tail -35
'

# 3. 불일치 상세
docker exec iic-osic-tools_xvnc_uid_1000 bash -c '
cd /foss/designs/designs/bgr_ldo/layout/bgr_core
grep -n "no matching net" lvs_bgr.out
sed -n "/NET mismatches/,/^-----/p" lvs_bgr.out | head -60
'
```

**골든 넷리스트 재생성 규약** (BGR 채팅):
```bash
sed 's/\(res_high_po_[0-9]*p[0-9]* L=[0-9.]*\) mult=1/\1/g' \
    bgr_core.spice > bgr_core_lvs.spice
```

**최종 결과**: `Circuits match uniquely`, 44/44 소자, 32/32 넷, property error 0

---

# 9. BGR 채팅 인터페이스

## 9.1 확정된 회로 수치 (schematic, tt/27, 트림 중앙코드)

| 항목 | 값 |
| :--- | :--- |
| V_ref | 1.205412 V |
| TC | 8.3 ppm/°C |
| I_tap (IB_EA) | 2.563374 µA |
| I_Q (코어+탭) | 62.2545 µA |
| 트림 LSB | 17.246 mV |
| 트림 DNL | 0.012 |
| trim_sw R_on | 4.573 Ω |
| 트림 LSB 저항 | 1,123 Ω |

## 9.2 더미 (스키매틱 반영 완료)

```text
XXDUM_B1, XXDUM_B2   pfet_g5v0d10v5  W=10 L=2   전 단자 VAPWR
XXDUM_C1, XXDUM_C2   nfet_g5v0d10v5  W=20 L=4   전 단자 VGND
XXDUM_D1, XXDUM_D2   nfet_g5v0d10v5  W=10 L=2   전 단자 VGND
XXDUM_Qn             pnp_05v5  m=16            E=B=C=VGND
XXDUM_RA1, XXDUM_RA2 res_high_po_0p69 L=31.49  양단 VGND
XXDUM_RB1, XXDUM_RB2 res_high_po_0p69 L=58.41  양단 VGND
```

## 9.3 PEX 산출물 (1차 완료 — R+C)

| 파일 | 내용 |
| :--- | :--- |
| `bgr_mos_pex_rc_safe.spice` | **R+C PEX (정본)** — flatten, 노드명 정리 |
| `bgr_mos_pex_rc.spice` | 원본 (점 노드 포함, 대조용) |
| `bgr_core_pex_rc_wrap.spice` | 핀 순서 변환 래퍼 |

```spice
.include bgr_mos_pex_rc_safe.spice
.subckt bgr_core VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 VGND
Xcore VGND VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 bgr_mos_flat
.ends
```

**추출 조건 (반드시 병기)**: magic **8.3.678** (HEAD 빌드) / `extract style` **기본값 `ngspice()`** / `flatten bgr_mos → bgr_mos_flat` / `extract no coupling` / `extract do resistance` / `ext2sim labels on` → `extresist` (전 넷) / `cthresh 0.01 fF` / `rthresh 1 Ω` / `ext2spice extresist on`

**산출**: 소자 186 / R 4942 / C 31 (DRC full 사인오프 백업: `bgr_mos_DRCCLEAN.mag`)  
**flatten판 LVS**: `Circuits match uniquely`, 44/44, 32/32, **property error 0**

## 9.4 ★ 1차 PEX 검증 결과 — 전 항목 통과

| 지표 | schematic | PEX R+C | 차이 |
| :--- | ---: | ---: | ---: |
| I_Q | 62.2545 µA | 62.054 µA | −0.3 % |
| V_ref | 1.205412 V | 1.204760 V | −0.05 % |
| **TC** | 8.3 ppm/°C | **10.9 ppm/°C** | +2.6 |
| IB_EA | 2.563374 µA | 2.560077 µA | −0.13 % |
| VBE1 | 0.778849 V | 0.779032 V | +0.2 mV |
| V_casc_n | 2.607819 V | 2.605132 V | −2.7 mV |
| sense_out | 13.546 mV | 14.239 mV | +0.7 mV |

**트림 16코드** (전 코너 단조 통과, 판정 기준 **DNL < 0.15 LSB**)

| 코너 | 중앙 V_out | LSB | DNL |
| :--- | ---: | ---: | ---: |
| tt/27 | 1.79882 | 17.353 mV | 0.0909 |
| ss/125 | 1.80033 | 17.255 mV | 0.0828 |
| ff/−40 | 1.86937 | 16.520 mV | **0.1152** |

**startup**: staircase(PWL 0→1.5→3.3 V, 35 µs) tt/27 · ss/−40 양 코너 정상 탈출, false-lock 없음.

**해석 결과**

- **V_ref가 거의 안 움직였다.** 시트저항 차이(magic 319.8 vs ngspice 325.0, −1.22 %)로 −14 mV를 예상했으나 실측 −0.65 mV. 저항 pcell 폴리 컨택(50.67 Ω/단자 × 22 = 1,115 Ω 추가)이 시트저항 감소를 거의 정확히 상쇄했다. 트림 창 중심이 유지되어 유리.
- **TC +2.6 ppm은 폴리 컨택 기여.** 컨택은 R1(16.7 kΩ)과 R6(115.7 kΩ)에 붙을 때 비중이 6.9배 다르므로 헤드 TC 2성분 모델과 같은 메커니즘. 10.9 ppm은 예산 50의 22 %.
- **ff/−40 중앙 1.869는 정상.** ff 칩은 V_ref가 높아 다른 코드를 선택하므로 코드 × 코너는 음의 상관.
- **트림 재배선(P4/P5) 확정.** 최악 DNL 0.1152 × 16.52 mV = 1.90 mV, 양자화 잔여 ±8.26 mV와 RSS 합성 시 ±8.48 mV (2.7 % 증가), LDO 스펙 ±36 mV 대비 24 %. 추가 조정 불요.

## 9.5 ★ 해석적 배선저항은 폐기 — 폴리 컨택을 안 셌다

`extresist`가 막혀 있던 동안 PDK 시트저항 + 기하 실측으로 산출한 값은 **과소평가**였다.

추출값에 반복 등장한 **50.6672 Ω**의 정체:

$$\frac{152\ \Omega\ (\texttt{contact pc,xpc})}{3\ \text{cuts}} = 50.67\ \Omega$$

**저항 pcell 단자의 폴리 컨택**이다. 해석 모델은 `metal1`·`metal2` 시트저항(125 mΩ/□)과 `m2c` via(4.5 Ω/컷)만 셌고 폴리 컨택은 **목록에조차 없었다.**

**추출값에서 읽히는 성분**

| 값 | 정체 |
| ---: | :--- |
| 50.67 Ω | 저항 pcell 단자 폴리 컨택 (152 ÷ 3컷) |
| 16.79 Ω | li + mcon 경로 |
| 8.11981 Ω | trim 유닛 핑거 → 콤 (22개 병렬이라 실효 0.37 Ω) |
| 10.67 / 12.29 / 1.90 Ω | met2 배선 세그먼트 |

**폐기된 해석값 (기록용, 인용 금지)**: P1 27.24 / P2 12.53 / P3 13.53 / P4 22.37 / P5 16.96 / P6 13.66 Ω → b0 44.34 / b1 30.63 / b2 43.90 / b3 35.19 Ω

**교훈**: 해석 모델은 "무엇을 세는가"만큼 **"무엇을 안 세는가"를 명시**해야 한다. 폴리 컨택은 목록에 없었기 때문에 자체 평가한 ±20~30 % 불확실성에도 잡히지 않았다.

## 9.6 2차 PEX 계획

현 넷리스트는 **BGR 코어 단독 · MiM 미배치 · no coupling**. 다음 변경이 기생 용량을 바꾼다.

- 컬럼 2 met3 제거·재배선 (MiM 6슬롯)
- LDO 존 배치 + C_out 뱅크가 BGR 상공을 덮음

| 항목 | 1차 | 2차 |
| :--- | :--- | :--- |
| TC · V_ref · IB_EA · I_Q · 트림 DNL | **확정** | 대조만 |
| PSRR · Noise | 참고용 | **최종** |
| startup | 마진 확인 | **재확인** |

**`no coupling`의 한계**: 커플링 용량을 기판으로 lumped하므로 총 부하는 보존되나 **넷 간 결합이 소거**된다 → PSRR 낙관적. 2차는 `extract do coupling`.

**`sense_out`은 고임피던스**(su1 스택 약 0.2 µA)라 C_out 뱅크가 상공을 덮으면 판정 타이밍이 밀릴 수 있다.

---

# 10. PEX 절차

## 10.1 magic 버전

| 경로 | 버전 |
| :--- | :--- |
| `/foss/tools/bin/magic` | 8.3.664 (기본) |
| `$HOME/.local/bin/magic` | **8.3.678 (HEAD 빌드)** — R 추출에 필수 |

```bash
cd /tmp && git clone --depth 1 https://github.com/RTimothyEdwards/magic.git
cd magic && ./configure --prefix=$HOME/.local && make -j4 && make install
```

**GUI 실행**

```bash
docker exec -it <컨테이너> bash -lc '
cd <작업디렉터리>
export DISPLAY=host.docker.internal:0
export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A
$HOME/.local/bin/magic -T sky130A'
```

**배치 실행** (크래시 로그 확보용)

```bash
docker exec <컨테이너> bash -l -c '
cd <작업디렉터리>
$HOME/.local/bin/magic -dnull -noconsole -T sky130A << "EOF" > log.txt 2>&1
... 명령 ...
quit -noprompt
EOF
echo "exit: $?"     # 139 = SIGSEGV
tail -30 log.txt
'
```

★ `-T sky130A`를 빼면 **다른 tech(ihp-sg13g2)가 로드된다.** 반드시 명시.

## 10.2 R+C 추출 (확정판)

```bash
rm -f bgr_mos_flat.ext bgr_mos_flat.sim bgr_mos_flat.nodes bgr_mos_flat.res.ext
```

```tcl
load bgr_mos
select top cell
flatten bgr_mos_flat
load bgr_mos_flat
select top cell
save bgr_mos_flat

extract no coupling
extract do resistance
extract all

ext2sim labels on
ext2sim

extresist

ext2spice lvs
ext2spice cthresh 0.01
ext2spice rthresh 1
ext2spice extresist on
ext2spice -o bgr_mos_pex_rc.spice
```

## 10.3 옵션 근거

| 옵션 | 설정 | 근거 |
| :--- | :--- | :--- |
| `extract style` | **명시 안 함** | `(si)`는 `w=10u l=0.15u`로 SI 접미사를 붙이고, netgen이 `0.15u = 1.5e-7`로 읽어 골든의 `0.15`와 비교 → property error delta 200 %. **LVS를 통과시킨 관례는 기본값 `ngspice()`** |
| `flatten` | 필수 | 계층 R-C 추출은 의미 있는 결과를 보장하지 않음 (magic 개발자 확인) |
| `no coupling` | 1차만 | §9.6 |
| `cthresh 0.01` | fF | `sense_out` 고임피던스라 작은 용량도 startup 타이밍에 실림 |
| `rthresh 1` | Ω, **정수만** | `0.1`은 `integer value or infinite expected`로 파싱 실패 → 넷리스트 출력이 **조용히 중단** |
| `extresist` | 인자 없이 | 전 넷 처리. `include <넷들>` / `ignore` / `force`로 제한 가능하나 `include`가 첫 인자만 먹은 사례 있음 — `Total Nets` 확인 필요 |
| `extresist tolerance` | 사용 안 함 | deprecated |

## 10.4 C-only 추출 (빠른 검증용)

```tcl
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice cthresh 0.01
ext2spice -o bgr_mos_pex.spice
```

## 10.5 검증용 추출 (연결 확인 · LVS)

```tcl
extract style ngspice(si)
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice -o chk.spice
```

`do resistance`·`cthresh`·`rthresh`는 기생 소자 출력에만 영향을 주고 **넷 연결성 판정에는 영향이 없다.**

## 10.6 flatten판 LVS (필수)

```bash
docker exec <컨테이너> bash -l -c '
cd <작업디렉터리>
$HOME/.local/bin/magic -dnull -noconsole -T sky130A << "EOF" > /dev/null 2>&1
load bgr_mos_flat
select top cell
extract no coupling
extract no resistance
extract all
ext2spice lvs
ext2spice -o bgr_mos_flat_chk.spice
quit -noprompt
EOF
netgen -batch lvs "bgr_mos_flat_chk.spice bgr_mos_flat" \
  "/foss/designs/designs/bgr_ldo/bgr/bgr_core_lvs.spice bgr_core" \
  /foss/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl lvs_flat.out 2>&1 | tail -12
'
```

**성공 조건**: `Circuits match uniquely` + **property error 0**

## 10.7 노드명 정리 (sanitize)

```bash
docker exec <컨테이너> python3 -c "
import re
d='<작업디렉터리>/'
NUM=re.compile(r'^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?\$')
out=[]
for line in open(d+'bgr_mos_pex_rc.spice'):
    if re.match(r'^[XRC]\d', line):
        f=line.split(); g=[f[0]]
        for t in f[1:]:
            if '=' in t or NUM.match(t) or t.startswith('sky130_fd_pr__') and '.' not in t:
                g.append(t)
            else:
                g.append(t.replace('.','_'))
        out.append(' '.join(g)+'\n')
    else:
        out.append(line)
open(d+'bgr_mos_pex_rc_safe.spice','w').writelines(out)
"
```

**검증 (§2.19 사고 재발 방지)**

```bash
docker exec <컨테이너> python3 -c "
import re
d='<작업디렉터리>/'
a=open(d+'bgr_mos_pex_rc.spice').read().splitlines()
b=open(d+'bgr_mos_pex_rc_safe.spice').read().splitlines()
assert len(a)==len(b)
for la,lb in zip(a,b):
    if re.match(r'^[XRC]\d', la):
        fa,fb=la.split(),lb.split()
        assert len(fa)==len(fb)
        for ta,tb in zip(fa,fb):
            if '=' in ta or re.match(r'^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?\$', ta):
                assert ta==tb, f'corrupted: {ta} -> {tb}'
print('[PASS] Verification PASSED')
"
```
