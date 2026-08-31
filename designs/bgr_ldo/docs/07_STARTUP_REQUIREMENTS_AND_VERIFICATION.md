# Start-up 회로 — 요구조건과 검증

**문서 번호**: `07_STARTUP_REQUIREMENTS_AND_VERIFICATION.md`  
**회로 대상**: Banba Current-Mode BGR Core Start-up Circuit  
**검증 조건**: Post-layout PEX R+C (`pex6_safe.spice`), 트림 code 31, $V_{APWR} = 3.3\text{ V}$

---

## 1. 요구조건 (선행 정의)

자기바이어스(Self-biased) 루프는 구조적으로 모든 소자가 꺼져 있는 축퇴해(Degenerate Zero State, $I=0$)를 필연적으로 갖는다.  
이를 안전하게 탈출하고 회로 본래의 기능을 온전히 보장하기 위해 Start-up 회로는 다음 **세 가지 상호 독립적인 요구조건**을 동시에 만족해야 한다:

* **(R1) DC 해 유일성**: 축퇴해를 소거하여 전원 인가 시 존재하는 유효 DC 평형해가 오직 정상 동작점 1개뿐이어야 함.
* **(R2) 기동 신뢰성**: 전 공정 코너, 전 온도 및 임의의 전원 램프 조건(급격한 변동 및 브라운아웃 포함)에서 확실하게 정상 상태로 기동할 것.
* **(R3) 정상 진입 후 완전 차단(Off-state Isolation)**:  
  * $V_{gate\_top}$ 노드는 소신호 출력 임피던스가 **$820\text{ M}\Omega$**에 달하는 초고임피던스 고감도 노드임.
  * 나노암페어($\text{nA}$) 수준의 미세 잔류 전류만으로도 $V_{ref}$와 온도계수(TC)가 심각하게 왜곡됨.
  * *(참고: $IB\_EA$ 바이어스 탭을 칩 핀으로 인출하지 않고 내부 차폐한 설계 결정과 동일한 철학을 같은 노드에 일관되게 적용).*

---

## 2. 회로 구조 및 동작 메커니즘

`sense_out` 노드를 판정 노드로 삼는 **전류 비교(Current-Comparator) 기반 능동 스타트업 구조**:

* **Pull-up 네트워크**: `XM_su1a/b/c` (W 0.42 / L 20 PMOS 3단 직렬)
  * 상시 극약 정전류(Sub-threshold / Deep Saturation) 공급.
* **Pull-down 소자**: `XM_pd` (W 12 / L 2 NMOS, 게이트 = $V_{BE1}$)
  * BGR 코어가 정상 도통하여 $V_{BE1}$이 상승하면 강력하게 턴온되어 `sense_out`을 접지 레벨로 견인.
* **시동 주입 소자**: `XM_su_n1` (W 1 / L 2 NMOS)
  * `sense_out`이 High일 때 $V_{gate\_top}$을 접지로 끌어내려 상단 PMOS 미러를 강제 도통시킴.

> ★ **핵심 설계 특징: BGR 자체의 $V_{BE}$를 이용한 자기 참조(Self-Referenced) 해제 판정**  
> 별도의 불안정한 외부 기준 전압 없이 BGR 코어 내부의 $V_{BE1}$을 직접 해제 판정 기준으로 사용함. 기준점이 회로와 함께 거동하므로 공정 코너 및 온도 변화에 따른 추적(Tracking)이 자동으로 이루어짐.

---

## 3. 포스트 레이아웃 실측 검증 결과 (PEX R+C)

### (R1) DC 해 유일성 — 평형해 직접 계수 (Zero-Crossing Counting)
* **검증 방법론**: $V_{gate\_top}$을 0 V부터 3.3 V까지 $2\text{ mV}$ 스텝으로 강제 스윕하며, 해당 노드로 공급되는 순전류($I_{net}$)의 영점(Zero-crossing)을 직접 계수.
  * 영점은 $I_{net} = 0$인 지점으로, 회로의 DC 평형해(Equilibrium Points)의 개수를 누락 없이 전수 조사하는 엄밀한 방법임.
* **검증 결과**:
  * 전 9개 조건 (공정 코너 `tt / ss / ff` × 온도 `-40 / 27 / 125°C`) 전수 조사 결과 **영점은 정확히 1개만 존재**.
  * 국소 기울기($\partial I / \partial V$)의 부호 검증을 통해 유일한 평형해가 동역학적으로 안정한 점(Stable Attractor)임을 확인.
  * 동작점 $V_{gate\_top}$: **$1.984\text{ V} \sim 2.306\text{ V}$**.
  * 축퇴해 상태($V_g = V_{APWR} = 3.3\text{ V}$)에서 순 주입 전류는 **$-1.41\text{ }\mu\text{A} \sim -2.21\text{ }\mu\text{A}$**로 0이 아님 $\rightarrow$ **축퇴해가 평형점이 될 수 없으며, 유일한 정상 DC 해만 존재함을 수학적·구조적으로 입증**.

---

### (R2) 기동 구동력 및 과도 동특성 (Startup & Brownout)
* **기동 구동력 (Drive Strength)**:
  * Zero-state($V_g = 3.3\text{ V}$) 순 주입 전류 최악 조건: **$1.412\text{ }\mu\text{A}$** (`ss / 125°C`)  
    $\rightarrow$ BGR 단일 브랜치 전류($9.7\text{ }\mu\text{A}$)의 **$15\%$**에 달하여 미러를 즉각 도통시키기에 충분한 강도.
  * 최대 구동 전류: **$2.206\text{ }\mu\text{A}$** (`ff / -40°C`).
  * $V_g = 3.0\text{ V} \rightarrow 3.3\text{ V}$ 구간 전류 변화율 **$0.2\%$ 이하**로 정전류원 특성을 유지하여 확실한 기동 보장.
* **전원 램프 과도 해석**:
  * 4개 코너 transient 전수 통과 (기동 중간 $1.5\text{ V} / 20\text{ }\mu\text{s}$ 전압 정체 구간 포함 시험 완료).
* **브라운아웃(Brown-out) 복구력 검증**:
  * 4개 코너 × 전원 전압 강하(Dip) 3종($0.3\text{ V}, 0.8\text{ V}, 1.5\text{ V}$) = **총 12개 조건 전수 정상 재기동 확인**.
  * 전원 Dip 중 $V_{ref}$가 $0.00001\text{ V}$까지 완전 붕괴된 후에도 정상 동작점으로 $100\%$ 복귀.
  * 최악 회복 지연 시간: **$0.7\text{ }\mu\text{s}$**.
  * ★ **1.5 V 딥 고전적 실패 모드 극복**:  
    $1.5\text{ V}$ 딥 조건에서는 $V_{ref}$가 $0.095\text{ V} \sim 0.282\text{ V}$로 어중간하게 잔류할 수 있음. 이 경우 $V_{BE1}$이 미세하게 살아있어 `XM_pd`가 불완전하게 도통되고 `sense_out`을 억눌러 재기동을 방해하는 취약점이 발생하기 쉬우나, 본 구조는 이 조건에서도 완벽하게 재기동에 성공함.

---

### (R3) 정상 상태 완전 해제 (Leakage & High-Z Isolation)
* **정상 동작 시 잔류 전류**:
  * `XM_su_n1`의 차단 상태 누설 전류 최악 조건: **단 $9.1\text{ pA}$** (`ff / 125°C`).
  * 이는 정상 브랜치 전류($9.7\text{ }\mu\text{A}$) 대비 **$0.00009\%$** 수준으로, $820\text{ M}\Omega$ 고임피던스 노드 전압 왜곡이 $7.5\text{ }\mu\text{V}$ 미만에 불과하여 $V_{ref}$ 및 TC에 측정 가능한 영향을 일절 주지 않음.
* **차단 전압 마진**:
  * 정상 동작 시 `sense_out` 전압: **$8.2\text{ mV} \sim 23.4\text{ mV}$**.
  * $V_{th\_nfet}$ (약 $0.7\text{ V}$) 대비 **$3\%$ 수준**으로 완전한 Sub-threshold 차단 영역 유지.
* **자기보상(Self-Compensation) 메커니즘**:
  * 온도가 상승함에 따라 $V_{BE1}$($-1.5\text{ mV/}^\circ\text{C}$)과 `XM_pd`의 $V_{th}$($-1\text{ mV/}^\circ\text{C}$)가 같은 방향으로 이동함.
  * 이에 따라 $V_{GS} - V_{th}$ 오버드라이브 전압의 감소폭이 완충되어, 최고 온도($125^\circ\text{C}$)에서도 `sense_out` 전압 억제 마진을 **30배 이상** 유지함.

---

## 4. 설계 및 아키텍처 관점의 고찰

1. **비경쟁 코너(Orthogonal Worst Cases) 특성**:
   * 기동력 (R2) 최악 조건: **`ss / 125°C`** (약한 PMOS, 고온 채널 저항 증가)
   * 차단력 (R3) 최악 조건: **`ff / 125°C`** (강한 소자, 고온 누설 전류 증가)
   * 최악 조건이 상호 배타적인 코너에서 발생하므로, 두 요구조건 간에 파라미터 트레이드오프 없이 **양쪽 마진을 동시에 극대화**할 수 있음.

2. **포스트 레이아웃 기생 성분 불감성 (PEX Immunity)**:
   * 스키매틱 해석치 대비 PEX 실측 편차는 **$0.09\%$ 이내**로 완벽히 일치.
   * 스타트업 라인은 $\mu\text{A}$ 급 미소 전류 경로이므로, PEX 배선 저항($3.6\text{ }\Omega \sim 23\text{ }\Omega$)에 의한 기생 IR 드롭이 수십 $\mu\text{V}$에 불과함.
   * *(트림 네트워크에서 $101.3\text{ }\Omega$ 폴리 컨택 저항으로 인해 LSB 가중치가 왜곡되었던 고민감 부위와 달리, 스타트업 회로는 레이아웃 기생 성분에 본질적으로 견고함).*

3. **검증 방법론의 엄밀성 (Existence vs Structure)**:
   * 과도 해석(Transient)은 "특정 램프 조건에서 기동에 성공했다"는 **존재 증명(Existence Proof)**에 머무름.
   * 반면, 평형해 계수(Zero-crossing analysis, R1)는 "기동하지 않고 머무를 수 있는 축퇴 상태가 회로 상태 공간(State Space) 상에 아예 존재하지 않는다"는 **구조적 불변성(Structural Invariant)**을 증명함.
