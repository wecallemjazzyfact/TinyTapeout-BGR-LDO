# BGR 코어 1차 PEX 기록

**대상**: sky130A TinyTapeout 아날로그 타일 BGR 코어 (`bgr_mos`, 186 소자)
**결과**: R+C 추출 완료, post-layout 검증 전 항목 통과
**도구**: magic 8.3.678 (HEAD 빌드), netgen, ngspice
**상태**: 2차 PEX(top 조립 + coupling) 대기

---

# 1. 최종 결과

| 지표 | schematic | PEX R+C | 차이 |
| :--- | ---: | ---: | ---: |
| I_Q | 62.2545 µA | 62.054 µA | −0.3 % |
| V_ref | 1.205412 V | 1.204760 V | −0.05 % |
| **TC** | 8.3 ppm/°C | **10.9 ppm/°C** | +2.6 |
| IB_EA | 2.563374 µA | 2.560077 µA | −0.13 % |
| VBE1 | 0.778849 V | 0.779032 V | +0.2 mV |
| V_casc_n | 2.607819 V | 2.605132 V | −2.7 mV |
| sense_out | 13.546 mV | 14.239 mV | +0.7 mV |

**트림 16코드** (전 코너 단조 통과)

| 코너 | 중앙 V_out | LSB | DNL |
| :--- | ---: | ---: | ---: |
| tt/27 | 1.79882 | 17.353 mV | 0.0909 |
| ss/125 | 1.80033 | 17.255 mV | 0.0828 |
| ff/−40 | 1.86937 | 16.520 mV | 0.1152 |

판정 기준 **DNL < 0.15 LSB**(오차 예산에서 역산). 최악 ff/−40에서 0.1152 × 16.52 mV = 1.90 mV, 양자화 잔여 ±8.26 mV와 RSS 합성 시 ±8.48 mV로 2.7 % 증가. LDO 스펙 ±36 mV 대비 24 %.

**startup**: staircase(PWL 0→1.5→3.3 V, 35 µs) tt/27 · ss/−40 양 코너 정상 탈출, false-lock 없음.

**LVS (flatten판)**: `Circuits match uniquely`, 44/44 소자, 32/32 넷, property error 0.

---

# 2. 추출 절차 (확정판)

```tcl
# 중간 파일 삭제 후 단일 세션에서 실행
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

**산출**: 소자 186 / R 4945 / C 30 (넷별 합산 700.8 fF)

## 옵션 근거

| 옵션 | 설정 | 근거 |
| :--- | :--- | :--- |
| `extract style` | **명시 안 함** (기본 `ngspice()`) | `(si)`를 쓰면 `w=10u l=0.15u`로 SI 접미사가 붙어 netgen이 `0.15u = 1.5e-7`로 읽고 골든의 `0.15`와 비교 → property error delta 200 % |
| `flatten` | 필수 | 계층 상태의 R-C 추출은 의미 있는 결과를 보장하지 않음 (magic 개발자 확인) |
| `no coupling` | 1차만 | 커플링 용량을 기판으로 lumped. 총 부하는 보존되나 넷 간 결합 소거 → PSRR 낙관적. 2차는 `do coupling` |
| `cthresh 0.01` | fF | `sense_out`이 고임피던스(su1 스택 약 0.2 µA)라 작은 용량도 startup 타이밍에 실림 |
| `rthresh 1` | Ω, **정수만** | `0.1`은 `integer value or infinite expected`로 파싱 실패 → 넷리스트 출력이 조용히 중단됨 |
| `extresist` | 인자 없이 | 전 넷 처리. `include <넷들>`로 제한 가능하나 첫 인자만 먹은 사례 있음 — `Total Nets` 확인 필요 |

## 노드명 정리

추출 넷리스트에 `VGND.t12`, `sky130_..._JS995W_21.S` 같은 점 포함 노드가 나온다. ngspice가 점을 계층 구분자로 해석할 수 있어 밑줄로 치환한다.

**치환 제외 조건** (셋 중 하나라도 해당하면 원본 유지)

1. `=` 포함 토큰 (소자 파라미터)
2. 숫자 토큰: `^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?$`
3. `sky130_fd_pr__`로 시작하고 점이 없음 (모델명)

**검증**: 원본 대비 행수·X/R/C 개수 동일, 값 필드 변형 0행, 잔여 점 노드 0.

## 래퍼

```spice
.include bgr_mos_pex_rc_safe.spice

.subckt bgr_core VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 VGND
Xcore VGND VAPWR VREF_LOW IB_EA TRIM0 TRIM1 TRIM2 TRIM3 bgr_mos_flat
.ends
```

PEX 최상위 셀명이 `bgr_mos_flat`이고 핀 순서가 TB(`bgr_core_tb2`)와 다르므로 필요.

---

# 3. 해결한 문제 3건

## 3.1 `extract do resistance` 세그폴트

**증상**: `extract all` 중 프로세스 사망(exit 139), 마지막 출력 `Extracting R1`, 에러 메시지 없음.

**격리**: 빈 셀에 `sky130_fd_pr__res_high_po_0p69` (W=0.69, L=3.650) 하나만 놓아도 재현. 같은 pcell의 L=1.27 / 31.49 / 91.2 / 229.4는 통과. snake 유무 무관.

**원인** (magic 개발자 R. T. Edwards 확인): 특정 extraction style이 `xpolycontact`의 contact residue mask에 `xpolycontact` 자신을 포함시켜 `FindStartTile()`이 동일 인자로 자기 자신을 호출 → 무한 재귀 → 스택 오버플로.

**해결**: magic 8.3.678에서 수정. 아울러 **flatten 선행이 필수**라는 지적을 받음.

**과정에서 배운 것**: 최소 재현 케이스를 만들 때 과도하게 줄이면 "유효하지 않은 테스트 케이스"가 되어 원인 파악을 방해할 수 있다. 이 경우 단일 인스턴스·미연결·계층 구조 세 가지가 지적받았다.

## 3.2 중간 파일 오염

**증상**: 재추출 시 `No device of type nmos found at ...`, `Couldn't find wire at ...`, `Nets output: 0`.

**원인**: `extresist`는 `.ext` / `.sim` / `.nodes`를 함께 읽는데, 이전 run이 다른 `extract style`(스케일이 다름)로 만든 파일이 남아 좌표가 어긋남.

**해결**: 매 run 전 `rm -f <cell>_flat.{ext,sim,nodes,res.ext}`.

## 3.3 ★ 치환 스크립트가 값 필드를 파괴

**증상**: post-layout `.op`에서 I_Q 190.5 µA (schematic 62.25의 **3.06배**), TC 170.7 ppm/°C (20배), V_ref +1.2 %.

**원인**: 노드명 치환 스크립트가 `=`를 포함하지 않은 토큰을 무조건 치환하도록 작성되어 **저항·용량 값의 소수점까지** 밑줄이 됨.

```text
0.79685f → 0_79685f
10079.4  → 10079_4
```

ngspice가 `10079_4`를 `10079` + 미상 접미사로 읽으면 저항이 통째로 달라지고, 미러 전류가 바뀌어 I_Q 3배가 그대로 설명된다.

**해결**: 숫자 토큰·파라미터·모델명을 치환에서 제외. 재측정 결과 I_Q 62.054 µA로 정상 복귀.

**교훈**: 넷리스트 후처리는 **전수 대조로 검증**해야 한다. 행수·소자 개수만 맞으면 통과시켰던 것이 문제였고, 값 필드가 원본과 완전히 동일한지 확인하는 항목이 빠져 있었다.

---

# 4. 무해로 확인된 경고 3건

## (a) 더미 소자의 확산 파라미터 이상치

`X10` (`XDUM_B` 계열)에서 `as=104.5218`, `ps=734.76` — 정상값(2.9 / 20.58)의 36배.

flatten으로 인접 더미 확산이 병합된 결과. 더미는 전 단자가 동전위(VAPWR 또는 VGND)라 **접합 전압차가 0**이므로 접합 용량·누설 기여가 0. 무해.

## (b) `VAPWR` 노드 분할

`VAPWR` / `VAPWR.t33` / `VAPWR.t0` 세 노드로 나뉘어 있으나 저항으로 연결됨:

```text
R0 VAPWR      VAPWR.n0   18.6672 Ω
R2 VAPWR      VAPWR.t33   1.52698 Ω
R1 VAPWR.t33  VAPWR.t0   13.1902 Ω
```

`extresist`가 전원 레일을 세그먼트로 쪼갠 정상 동작.

## (c) `Missing source connection` 14건

좌표를 µm로 환산(내부단위 ÷200)하니 정확히 PNP 5×5 격자:

$$x = 67.0 + 4.6i + 0.77, \qquad y = 4.6j + 0.77 \quad (i, j = 0..4)$$

셀 내부 고정 오프셋 (0.77, 0.77) = PNP 확산부. **PNP는 소스 단자가 없는 소자**인데 magic이 MOS 규칙으로 검사해 낸 오경고. `net VBE1` 1건도 QA(76.97, 9.96) 자리와 정합.

**결정적 근거**: flatten판 LVS가 `Circuits match uniquely` + property error 0으로 통과. 소스가 실제로 끊겼다면 PNP 3클래스(QA / QB / 더미) 구분이 무너져 LVS가 실패한다.

---

# 5. 배선 저항 — 해석 모델의 실패와 교정

`extresist`가 막혀 있던 동안 PDK 시트저항 + 기하 실측으로 해석적 산출을 시도했다. 추출이 가능해진 뒤 대조하니 **과소평가**였다.

## 해석 모델이 놓친 것

추출값에 반복 등장한 **50.6672 Ω**의 정체:

$$\frac{152\ \Omega\ (\texttt{contact pc,xpc})}{3\ \text{cuts}} = 50.67\ \Omega$$

**저항 pcell 단자의 폴리 컨택**이다. 해석 모델은 `metal1`·`metal2` 시트저항(125 mΩ/□)과 `m2c` via(4.5 Ω/컷)만 셌고 폴리 컨택은 고려조차 하지 않았다.

## 추출값에서 읽히는 성분

| 값 | 정체 |
| ---: | :--- |
| 50.67 Ω | 저항 pcell 단자 폴리 컨택 (152 ÷ 3컷) |
| 16.79 Ω | li + mcon 경로 |
| 8.11981 Ω | trim 유닛 핑거 → 콤 (22개 병렬이라 실효 0.37 Ω) |
| 10.67 / 12.29 / 1.90 Ω | met2 배선 세그먼트 |

`8.11981`은 해석 시점에 "누락했다"고 명시했던 콤 분산 성분이다. 22 병렬이라 실효는 작았다.

## 폐기된 해석값 (기록용)

| 분기 | 경로 | 해석값 (typ) |
| :--- | :--- | ---: |
| P1 | n_b0 → b0.D | 27.24 Ω |
| P2 | n_b1 → b0.S | 12.53 Ω |
| P3 | n_b2 → b1.S | 13.53 Ω |
| P4 | n_b2 → b2.D | 22.37 Ω |
| P5 | n_b3 → b2.S | 16.96 Ω |
| P6 | b3.S → VGND | 13.66 Ω |

스위치별 $R_{\text{short}} = P_{\text{head}} + R_{on} + P_{\text{tail}}$ → b0 44.34 / b1 30.63 / b2 43.90 / b3 35.19 Ω.

**교훈**: 해석 모델은 "무엇을 세는가"만큼 **"무엇을 안 세는가"를 명시**해야 한다. 이 경우 폴리 컨택은 목록에조차 없었기 때문에 불확실성 ±20~30 %라는 자체 평가에도 잡히지 않았다.

---

# 6. 예상과 다르게 나온 것

## V_ref가 거의 안 움직였다

시트저항 차이(magic 319.8 vs ngspice 325.0, −1.22 %)로 **약 −14 mV 이동**을 예상했으나 실측 **−0.65 mV**.

저항 pcell 폴리 컨택(50.67 Ω/단자 × 22 = 1,115 Ω 추가)이 시트저항 감소를 거의 정확히 상쇄했다. 결과적으로 트림 창 중심이 유지되어 유리하다.

## TC +2.6 ppm/°C

폴리 컨택의 기여. 컨택은 R1(16.7 kΩ)에 붙을 때와 R6(115.7 kΩ)에 붙을 때 **비중이 6.9배 다르므로**, 헤드 TC 2성분 모델과 같은 메커니즘으로 작동한다.

10.9 ppm/°C는 예산 50의 22 %로 여유가 크다.

## ff/−40 트림 중앙이 1.869로 높다

정상이다. ff 칩은 V_ref가 높아 다른 코드를 선택하므로 **코드 × 코너는 독립이 아니라 음의 상관**이다.

---

# 7. 트림 균등화 재배선 (완료, 확정)

DNL 기여를 줄이기 위해 두 분기를 수정했다.

| 분기 | 조치 | 해석값 |
| :--- | :--- | ---: |
| P4 (n_b2 → b2.D) | 최하 가로 서단 x 99.90 → **112.80** 단축, via1 착지점 이동 | 26.71 → 22.37 Ω |
| P5 (n_b3 → b2.S) | 세로 폭 0.30 → **0.48** (x 114.24–114.72) | 24.24 → 16.96 Ω |

코리도 여유: 신 n_b3 세로 서변 114.24 ↔ b0 S콤 met2(→114.10) **0.14** / 동변 114.72 ↔ n_b2 세로(114.86) **0.14**. 양쪽 최소치라 더 이상 확장 불가.

**PEX 결과 DNL 최악 0.1152 (ff/−40)로 기준 0.15 통과.** 추가 조정 불요.

---

# 8. 2차 PEX 계획

현 넷리스트는 **BGR 코어 단독 · MiM 미배치 · no coupling**이다. 다음 변경이 기생 용량을 바꾼다.

- 컬럼 2 met3 제거·재배선 (MiM 6슬롯 확보)
- LDO 존 배치 + C_out 뱅크가 BGR 상공을 덮음

| 항목 | 1차 | 2차 |
| :--- | :--- | :--- |
| TC · V_ref · IB_EA · I_Q · 트림 DNL | **확정** | 대조만 |
| PSRR · Noise | 참고용 | **최종** |
| startup | 마진 확인 | **재확인** |

`sense_out`은 고임피던스 노드(su1 스택 약 0.2 µA)라 C_out 뱅크가 상공을 덮으면 판정 타이밍이 밀릴 수 있다.

2차는 `extract do coupling`으로 추출한다.

---

# 부록. 재현 명령

## 배치 모드 실행 (크래시 로그 확보용)

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

GUI에서 프로세스가 죽으면 로그가 날아간다. `-T sky130A`를 빼면 다른 tech가 로드된다.

## HEAD 빌드

```bash
cd /tmp && git clone --depth 1 https://github.com/RTimothyEdwards/magic.git
cd magic && ./configure --prefix=$HOME/.local && make -j4 && make install
```

PATH 우선순위상 `magic`을 그냥 치면 구버전(`/foss/tools/bin/magic`)이 잡힌다. **전체 경로로 호출할 것.**

## 산출물 건전성 체크리스트

- [ ] 소자 수가 원본과 동일한가 (flatten 손실 확인)
- [ ] 단위 표기에 `u`/`n`/`p` 접미사가 붙지 않았는가
- [ ] flatten판 LVS가 property error 0으로 통과하는가
- [ ] sanitize 전후로 R/C 값 필드가 **완전히 동일**한가
- [ ] 잔여 점 노드 0인가
- [ ] `**FLOATING` 주석 노드가 없는가 (있으면 부유 금속 잔재)
