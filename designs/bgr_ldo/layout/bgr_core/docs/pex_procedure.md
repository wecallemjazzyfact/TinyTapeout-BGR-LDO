# TinyTapeout Analog BGR + LDO — PEX (Parasitic Extraction) 표준 절차서

본 문서는 TinyTapeout Sky130A 공정 기반 BGR 및 LDO 설계의 레이아웃 기생 성분 추출(PEX: Parasitic Extraction) 표준 절차와 검증 가이드라인을 정의합니다.

---

## 1. Magic 버전 관리 & 실행 지침

### 1.1 설치 및 버전 이원화 명세
* **기본 패키지 버전**: `/foss/tools/bin/magic` (v8.3.664)
* **최신 개발(HEAD) 빌드**: `$HOME/.local/bin/magic` (v8.3.678 이상)

#### HEAD 버전 소스 빌드 절차
```bash
cd /tmp && git clone --depth 1 https://github.com/RTimothyEdwards/magic.git
cd magic && ./configure --prefix=$HOME/.local && make -j4 && make install
```

> ⚠️ **PATH 우선순위 및 호출 주의사항**  
> 쉘의 `PATH` 환경변수 구성상 단순히 `magic`으로 실행할 경우 원하는 바이너리가 실행되지 않거나 환경에 따라 구버전/신버전 혼선이 발생할 수 있습니다. **반드시 절대/상대 경로(`$HOME/.local/bin/magic` 또는 `/foss/tools/bin/magic`)를 명시하여 호출**하십시오.

### 1.2 Technology 타겟 지정 (필수)
* Magic 실행 시 반드시 **`-T sky130A`** 플래그를 명시해야 합니다.
* 플래그 누락 시 기본 타겟인 `ihp-sg13g2` 등 타 공정 tech가 로드되어 DRC/PEX 추출 규칙이 손상됩니다.

### 1.3 실행 방법 (GUI 및 배치 모드)

#### GUI 실행 (MobaXterm / X11 연동)
```bash
docker exec -it iic-osic-tools_xvnc_uid_1000 bash -lc '
cd /foss/designs/designs/bgr_ldo/layout/bgr_core
export DISPLAY=host.docker.internal:0
export PDK_ROOT=/foss/pdks PDK=sky130A PDKPATH=/foss/pdks/sky130A
$HOME/.local/bin/magic -T sky130A
'
```

#### 배치 실행 (자동화 및 세그멘테이션 폴트/크래시 로그 확보용)
```bash
$HOME/.local/bin/magic -dnull -noconsole -T sky130A << "EOF" > log.txt 2>&1
# Tcl extraction commands...
quit -noprompt
EOF
echo "exit: $?"     # 139 = SIGSEGV (메모리 세그멘테이션 폴트 확인)
```

---

## 2. Extract Style과 단위 관례 (사고 사례)

### 2.1 사용 가능한 Extract Style
Magic에서 `extract style`로 설정 가능한 스타일 목록:
* `ngspice()` *(기본값 - 표준)*
* `(orig)`
* `(si)` *(주의: SI 단위 접미사 강제)*
* `(hrhc)` / `(lrhc)` / `(hrlc)` / `(lrlc)` *(hr/lr = High/Low Resistor Corner, hc/lc = High/Low Capacitor Corner)*

> 🛑 **주의**: Magic 내에 `sky130(full)` 스타일은 존재하지 않으며 지정 시 에러가 발생합니다.

### 2.2 🚨 실측 사고 사례: `(si)` 스타일 사용 금지
* `extract style (si)`를 적용할 경우, 트랜지스터 수치에 `w=10u l=0.15u`와 같이 **`u` 단위 접미사가 강제로 부착**됩니다.
* Netgen LVS 엔진은 `0.15u`를 `1.5e-7` 미터 단위로 파싱하는 반면, 골든 스키매틱의 `0.15`는 $\mu\text{m}$ 단위($1.5 \times 10^{-7}$)로 해석하여 **Property error delta 200% 단락 에러**가 발생하는 심각한 수치 오염 사고가 일어납니다.

### 2.3 추출 원칙
* LVS를 정상 통과시킨 표준 관례는 기본값인 **`ngspice()`**입니다. PEX 추출 시 별도의 `extract style`을 명시하지 말고 `.magicrc` 기본값을 그대로 사용합니다.
* Magic extraction 옵션은 **현재 세션에 잔류**하므로, 신규 검증 추출 전 반드시 아래 명령으로 옵션을 명시적 초기화합니다:
  ```tcl
  extract no coupling ; extract no resistance ; extract all
  ```

---

## 3. R+C 추출 절차 (확정 표준)

### 3.1 🚨 추출 전 필수 준비 규칙 (개발자 확인 사항)
1. **Flatten 필수성**: 계층(Hierarchical) 상태에서의 R+C 추출은 유효한 기생성분을 보장하지 않습니다 (Magic 개발자 R.T. Edwards 확인 사항). 반드시 최상위에서 `flatten`된 셀을 생성하여 추출해야 합니다.
2. **중간 찌꺼기 파일 삭제 필수**: 이전 run의 중간 파일(`.ext`, `.sim`, `.nodes`, `.res.ext`)이 잔류하면 `"No device of type nmos found at..."`, `"Couldn't find wire at..."`, `"Nets output: 0"` 에러가 나타납니다. **매 추출 시작 전 반드시 중간 찌꺼기 파일을 삭제**합니다.

### 3.2 R+C 표준 추출 명령어 절차 (Full Flow)

```tcl
# 1. 이전 중간 찌꺼기 파일 삭제
rm -f <cell>_flat.ext <cell>_flat.sim <cell>_flat.nodes <cell>_flat.res.ext

# 2. 셀 탑레벨 로드 및 Flatten 셀 생성
load <cell> ; select top cell
flatten <cell>_flat
load <cell>_flat ; select top cell ; save <cell>_flat

# 3. Magic Extraction 수행
extract no coupling
extract do resistance
extract all

# 4. ext2sim 및 extresist 처리
ext2sim labels on
ext2sim
extresist                       # 인자 없을 경우 전체 넷 대상 기생저항 계산

# 5. SPICE 넷리스트 변환
ext2spice lvs
ext2spice cthresh 0.01          # 0.01 fF 미만 용량 컷오프
ext2spice rthresh 1             # ★ 정수(Integer)만 인식! (0.1 입력 시 파싱 실패)
ext2spice extresist on
ext2spice -o <cell>_pex_rc.spice
```

> 💡 **Tip (넷 범위 제한 및 Deprecated 옵션)**  
> * `extresist include <net1> <net2>` / `ignore` / `force` 로 기생저항 계산 대상을 특정 넷으로 제한할 수 있습니다. (단, `include` 사용 시 첫 번째 인자만 정상 인식하는 이슈가 보고되었으므로 추출 후 로그의 "Total Nets" 수치를 반드시 검증하십시오.)  
> * `extresist tolerance` 옵션은 Deprecated 되어 더 이상 사용하지 않습니다.

---

## 4. C-only 추출 (빠른 검증용)

기생 저항을 제외하고 기생 용량만 빠르게 검증할 경우 아래 단축 절차를 사용합니다:

```tcl
extract no coupling ; extract no resistance ; extract all
ext2spice lvs
ext2spice cthresh 0.01
ext2spice -o <cell>_pex.spice
```

---

## 5. Coupling Cap (커플링 용량) 켜고 끄기의 의미

* **`extract no coupling` (Lumped Cap 모드)**:
  * 커플링 용량을 기판(GND)으로 합산(Lumped to Ground) 처리합니다.
  * 각 노드의 총 노드 부하 C_total은 정확히 보존되지만, 넷 간 상호 결합(Cross-coupling) 효과가 소거되어 **PSRR 및 AC CMRR 특성이 지나치게 낙관적**으로 평가될 수 있습니다.
* **단계별 적용 원칙**:
  * **1차 (구조 및 기본 연결 검증)**: `no coupling` 사용
  * **2차 (Top 블록 최종 사인오프)**: `do coupling`을 활성화하여 최종 PSRR 및 노이즈 검증

---

## 6. Flatten 셀 LVS 무결성 검증

Flatten 과정에서 레이어 손실이나 소자 삭제가 없는지 **LVS 재검증을 반드시 수행**해야 합니다.

```bash
# 1. Flatten 판 검증 넷리스트 추출
load <cell>_flat ; extract no coupling ; extract no resistance ; extract all
ext2spice lvs ; ext2spice -o <cell>_flat_chk.spice

# 2. Netgen LVS 수행
netgen -batch lvs "<cell>_flat_chk.spice <cell>_flat" \
  "<골든_스키매틱>.spice bgr_core" <setup_file>.tcl lvs_flat.out
```

* **LVS 성공 기준**:  
  `Circuits match uniquely` 출력 및 **`Property error: 0`** 확인

---

## 7. 노드명 정형화 (Sanitize) 규칙 및 사고 예방

### 7.1 추출 넷리스트 특성 및 위험성
* Magic PEX 넷리스트에는 `VGND.t12`, `sky130_fd_pr__pfet_01v8_JS995W_21.S`와 같이 **점(`.`)을 포함하는 노드명**이 대량 발생합니다.
* ngspice 엔진은 점(`.`) 문자를 서브서킷 계층 구분자로 파싱할 수 있으므로 시뮬레이션 중 오류나 노이즈 해석 에러를 유발합니다.

### 7.2 🚨 치환 스크립트 오작동 사고 사례
* 과거 단순 치환 스크립트가 등호(`=`) 없는 토큰을 구별 없이 치환하여, **저항 및 용량 수치의 소수점까지 밑줄(`_`)로 치환**되는 사고가 발생했습니다.
  * 예: `0.79685f` ➔ `0_79685f`, `10079.4` ➔ `10079_4`
* 이로 인해 소수점 수치가 손실되어 BGR ngspice 시뮬레이션 시 **바이어스 전류(I_Q)가 3배 폭등**하는 치명적 오류가 발생하였습니다.

### 7.3 Sanitize 안전 치환 규칙
노드명 파싱 시 **다음 3가지 조건 중 하나라도 만족하는 토큰은 절대로 변형하지 않고 그대로 유지**해야 합니다:
1. 등호(`=`)를 포함하는 소자 파라미터 토큰 (예: `w=10`, `l=0.15`)
2. 단위 접미사를 포함하는 숫자 토큰 (예: `0.79685f`, `10079.4`, `1.5e-7`)
3. `sky130_fd_pr__`로 시작하고 점이 없는 PDK 소자/모델명

> 전용 파이썬 처리 도구: `designs/bgr_ldo/layout/bgr_core/tools/sanitize_pex.py` 사용

---

## 8. Subcircuit Wrapper 구성

PEX로 추출된 최상위 셀명은 `<cell>_flat` 형태이며, 핀 순서가 기존 Testbench와 다를 수 있으므로 래퍼 서브서킷을 작성하여 시뮬레이션에 결합합니다.

```spice
* PEX Subcircuit Wrapper
.include <cell>_pex_rc_safe.spice

.subckt bgr_core VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 VGND
Xcore VGND VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 <cell>_flat
.ends
```

---

## 9. PEX 산출물 건전성 체크리스트

모든 PEX 파일 생성 후 시뮬레이션 전 다음 6개 검증 항목을 체크하십시오:

- [ ] **소자 수 일치**: 원본 스키매틱 대비 소자 개수가 완전 일치하는가 (Flatten 소실 확인)
- [ ] **단위 표기 오염 검증**: R/C 값 수치 뒤에 불필요한 `u`/`n`/`p` 접미사가 강제 결합되지 않았는가
- [ ] **LVS 무결성**: Netgen LVS 결과 `Property error`가 0 인가
- [ ] **Sanitize 수치 검증**: `sanitize_pex.py --verify` 실행 시 sanitize 전후 R/C 소자 값 수치가 100% 동일한가
- [ ] **노드 점 잔재 검사**: 노드 파라미터 필드에 잔여 점(`.`) 문자가 0개인가
- [ ] **FLOATING 노드 검사**: 넷리스트 주석에 `FLOATING` 플래그가 부착된 노드가 없는가 (플로팅 메탈 잔재 유무 확인)
