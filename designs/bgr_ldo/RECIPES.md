# 📖 Analog Design Recipes

이 문서는 BGR & LDO 설계 과정에서 사용하는 핵심 특성화 기법과 시뮬레이션 방법론을 정리해 둔 설계 매뉴얼(Recipe)입니다.

---

## 🛠️ 1. 다이오드 연결형 PMOS 특성화 (Diode-connected + Current Forcing Characterization)

### 1) 기법 개요 및 원리
일반적인 트랜지스터 특성화는 게이트 전압($V_{GS}$)을 스윕하면서 드레인 전류($I_D$)를 측정합니다. 하지만 이 방식은 특정 목표 전류(예: $9.68\,\text{µA}$)가 흐르는 정확한 동작점을 찾기 위해 눈으로 그래프를 대조해야 하는 번거로움이 있습니다.
본 기법은 다음 원리를 이용해 원하는 동작점을 1초 만에 직접 도출합니다.
- 트랜지스터를 **다이오드 형태(Gate-Drain 연결)**로 묶습니다.
- 드레인 단자에서 **목표 전류($I_{bias}$)**를 강제로 싱크(Sink)시킵니다.
- SPICE 솔버가 해당 전류를 흘리기 위해 필요한 **게이트 전압($V_{GS}$ 및 $V_{DS}$)**을 피드백 루프 연산으로 자동 수렴시킵니다.

### 2) 테스트벤치 템플릿 및 파라미터 파일
- **경로:** [sim/char/pmos_char.spice](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/sim/char/pmos_char.spice)

```spice
* PMOS Characterization Template
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt

* ==========================================
* [USER PARAMETERS]
* ==========================================
.param W_val = 10u
.param L_val = 2u
.param M_val = 4
.param I_bias = 9.68u

* ==========================================
* [DEVICE UNDER TEST]
* ==========================================
XM1 d d s b sky130_fd_pr__pfet_g5v0d10v5 w={W_val} l={L_val} m={M_val}

* Supplies
Vs s 0 3.3
Vb b 0 3.3
I1 d 0 {I_bias}

.op
.control
  run
  show xm1  ; vgs, vds, vth, gm, gds(ro), vdsat 확인
  print (3.3 - v(d)) ; Vsg (Vsd)
.endc
.end
```

### 3) 실행 명령어
터미널에서 아래 명령어를 실행하여 ngspice를 배치 모드로 구동합니다.
```bash
docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c "cd /foss/designs/designs/bgr_ldo/sim/char && ngspice -b pmos_char.spice"
```

### 4) 확인 및 분석해야 할 핵심 데이터 (Output checklist)
* **`id`**: 목표 전류($I_{bias}$)와 일치하는지 확인.
* **`vgs` / `vth`**: 문턱 전압 및 인가 전압 확인.
* **오버드라이브 전압 ($V_{ov}$)**: `vgs - vth`로 계산하며, 통상 매칭 향상을 위해 **$100\sim150\,\text{mV}$** 수준으로 맞춤.
* **`vdsat`**: 포화 영역 동작을 위해 필요한 최소 드레인-소스 전압.
* **`gm` / `gds`**: 트랜스컨덕턴스 및 출력 저항($r_o = 1/g_{ds}$) 확인.

### ⚠️ [중요gotchas] 특성화 과정의 3대 함정
1. **Moderate Inversion 영역의 공식 왜곡:**
   - 2차 자승 법칙(Square-law)에 따르면 트랜지스터 크기 비율을 $1/4$로 줄이면 오버드라이브 전압 $V_{ov}$가 정확히 $2$배 늘어나야 합니다. 
   - 하지만 약반전(Weak)과 강반전(Strong) 사이의 **중간 반전(Moderate Inversion, $V_{ov} \approx 50\sim130\,\text{mV}$)** 대역에서는 쇼트 채널 및 아임계 특성 때문에 이 단순 비율 공식이 크게 어긋납니다. 따라서 바이어스 소자의 $V_{bias}$ 전압은 반드시 **실제 ngspice 시뮬레이션을 돌려 실측한 전압을 기준으로 마진을 산출**해야 합니다.
2. **Wide-Swing 캐스코드의 극점 일치 함정:**
   - 단순히 이론적으로 중간 노드의 전압이 상단 PMOS의 $V_{SD} = V_{ov}$로 완벽히 일치하면 최적 설계라고 착각하기 쉽습니다. 
   - 하지만 실물 동작점에서는 **$V_{SD} \ge v_{dsat} + 50\,\text{mV}$의 Saturation Margin이 보장되지 않으면 상단 PMOS가 Triode 영역으로 밀려나 성능이 크게 퇴화**합니다. 이론적 "경계 일치"는 실제 공정 편차 하에서 실패 조건(Fail Condition)임을 명심하고 반드시 바이어스 소자 크기를 더 조여서 마진을 넓혀야 합니다.
3. **벌크-소스 전위차에 의한 바디 효과 (Body Effect):**
   - NMOS 등화기(`M3`/`M4`)처럼 소스가 BJT 에미터(약 $0.78\,\text{V}$)에 접촉하고 벌크는 GND(0V)에 묶이는 경우, $V_{SB} \approx 0.78\,\text{V}$에 의해 강력한 바디 효과가 발생합니다.
   - 이로 인해 문턱 전압 $V_{thn}$이 $270\,\text{mV}$가량 상승하여 실제 동작점 $V_{GS}$ 및 중간 노드 전압이 예측보다 $270\,\text{mV}$ 높게 형성됩니다. 헤드룸 계산 시 이 바디 효과에 의한 전압 상승분($V_{GS} \approx 1.18\,\text{V}$)을 전압 예산표에 반드시 선반영해야 합니다.
