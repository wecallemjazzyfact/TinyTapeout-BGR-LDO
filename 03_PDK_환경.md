# 03_PDK_환경.md (PDK 핵심 명세 및 시뮬레이션 개발 환경 구축서)

### TL;DR (3줄 요약)
1. TinyTapeout 아날로그 설계를 위한 도커 컨테이너 실행 환경, 프로젝트 디렉토리 트리 및 GUI 툴(Xschem/Magic) 구동 절차를 규정합니다.
2. SkyWater 130nm PDK의 핵심 소자(5V NMOS/PMOS, 고시트 저항, PNP BJT, MiM 커패시터)의 모델명과 이산 빈(Bin) 경계 한계($L \le 20\,\mu\text{m}$) 등 공정 함정을 요약했습니다.
3. 몬테카를로 외부 루프 구성법, 다이오드 결선식 PMOS 특성화 레시피, pygmid의 Spectre 종속 우회 방안 및 ngspice 실행 가드레일 3종을 제공합니다.

---

## 1. 시뮬레이션 및 설계 구동 환경

*   **도커 컨테이너명**: `iic-osic-tools_xvnc_uid_1000` (또는 로컬 런칭된 활성 컨테이너)
*   **볼륨 마운트 경로**:
    *   **도커 내부**: `/foss/designs/` (리눅스 경로)
    *   **윈도우 호스트**: `c:\Users\aa\Desktop\school\TinyTapeout\` (Windows 로컬 작업 공간)
*   **환경 변수 활성화**: 컨테이너 셸 내부 진입 후 반드시 `export PDK=sky130A` 및 `export PDKPATH=/foss/pdks/sky130A` 설정 여부를 확인하십시오.

### 1.1. 도커 재기동 및 XServer 브릿지 활성화 절차 (PC 재부팅 후)

#### 옵션 A. MobaXterm 연동 터미널 구동 (X11 GUI 윈도우 직접 팝업)
1.  Windows에서 **MobaXterm**을 실행하여 상단의 X Server 아이콘이 녹색(활성)인지 확인합니다.
2.  WSL 터미널을 열고 런처 디렉토리로 이동합니다:
    ```bash
    cd /mnt/c/Users/aa/Desktop/school/TinyTapeout/open-source/IIC-OSIC-TOOLS
    ```
3.  구동 스크립트를 기동합니다:
    ```bash
    ./start_x.sh
    ```
    *(만약 기존 컨테이너가 멈춘 상태라면 터미널에 출력되는 선택지에서 `s` (start)를 입력합니다)*
4.  윈도우 화면에 가상 GUI 터미널 팝업이 출력되면 xschem을 기동할 준비가 완료된 것입니다.

#### 옵션 B. 웹 브라우저 VNC 구동 (리눅스 전체 데스크톱 원격 조작)
1.  WSL 터미널에서 다음 스크립트를 실행합니다:
    ```bash
    ./start_vnc.sh
    ```
2.  Windows 웹 브라우저(Chrome 또는 Edge)를 실행하여 아래의 주소로 접속합니다:
    *   **VNC 주소**: `http://localhost:80/?password=abc123`

---

## 2. 프로젝트 디렉토리 트리 최종본

```
c:\Users\aa\Desktop\school\TinyTapeout\
├─ 00_인계_통합.md
├─ 01_BGR_최종스펙.md
├─ 02_LUT_앵커.md
├─ 03_PDK_환경.md
├─ 04_LDO_스펙.md           # LDO 목표 스펙 및 아키텍처
├─ WORKSPACE.md
├─ RESTART_GUIDE.md
├─ tapeout-guardrails.md
├─ designs/
│  └─ bgr_ldo/
│     ├─ DESIGN_JOURNEY.md
│     ├─ LOGBOOK.md
│     ├─ NOTES.md
│     ├─ RECIPES.md
│     ├─ REFERENCE_NOTES.md
│     ├─ bgr/                # BGR 스키매틱 및 ngspice testbench 폴더
│     ├─ ldo/                # LDO 설계 및 시뮬레이션 환경 폴더
│     │  └─ DECISIONS.md    # LDO 판정 기록 (근거·대체 이력의 정본)
│     ├─ top/                # BGR + LDO 통합 칩 스키매틱 및 핀 매핑 폴더
│     ├─ layout/             # Magic 레이아웃 (.mag) 및 GDS/LEF 산출물
│     ├─ milestones/         # 01~09 개발 마일스톤 증거 보관실
│     ├─ work/               # 로컬 DRC 및 LVS 검증용 임시 폴더
│     └─ lut/                # gm/Id Look-Up Table 프로젝트 공용 폴더
│        ├─ README.md       # LUT 정본 (사양·부호규약·정확도·사고이력)
│        ├─ lookup.py       # 조회 API
│        ├─ design.py       # 사이징 계층 (curves/vgs_at/size/charts)
│        ├─ gen/            # run_sweep.py, verify_gmid.py, 앵커 덱
│        └─ data/           # nfet/pfet_g5v0d10v5.pkl
```

---

## 3. PDK 소자 모델 전체 목록 및 설계 함정

*   **PDK 경로**: `/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice` (`tt` 코너 라이브러리 사용)

### 3.1. 소자 목록 및 파라미터 명세

#### NMOS 트랜지스터
*   **PDK 모델명**: `sky130_fd_pr__nfet_g5v0d10v5`
*   **특징**: 5V/10.5V Thick-Oxide 고전압 NMOS 소자. LDO 오차 증폭기의 하단 스택 및 BGR active mirror 하단 평형 제어 장치에 사용.
*   **바디 효과 주의 사항**: 벌크가 접지(0V)되고 소스가 공중으로 뜨는 회로 구성(예: 등화쌍 XM3/XM4, 소스 전위 $\approx 0.78\text{V}$) 시, $V_{SB} \approx 0.78\,\text{V}$에 의한 바디 효과로 인해 문턱 전압 $V_{thn}$이 **`0.798 V ➔ 1.069 V`**로 $271\,\text{mV}$가량 치솟는 물리 현상이 존재함. 따라서 전압 헤드룸 예산 설계 시 $V_{GS}$ 상승에 따른 마진 하락을 선대입하여 계산해야 합니다.

#### PMOS 트랜지스터
*   **PDK 모델명**: `sky130_fd_pr__pfet_g5v0d10v5`
*   **특징**: 5V/10.5V Thick-Oxide 고전압 PMOS 소자. BGR 메인 바이어스 거울 및 LDO 패스 소자(Pass Device)로 사용.
*   **L 치수 제한 (PDK Binning 함정)**: sky130 bsimg4 모델 카드의 구간 경계(bin) 정의 상, 단일 FET의 최대 채널 길이는 **`20 µm`**로 단단히 묶여 있습니다. 만약 스타트업 감지 소자 설계 시 누설 전류 극소화를 위해 단일 트랜지스터 $L = 60\,\mu\text{m}$로 넷리스트를 작성하면 `could not find a valid modelname` (혹은 `no model available`) 에러가 떨어지며 시뮬레이션이 붕괴합니다. 따라서 $L > 20\,\mu\text{m}$의 초대형 L이 필요한 경우 반드시 복수의 서브 소자를 **직렬 스택(Series Stack)** 형태로 결선하여 유효 $L$을 확보해야 합니다.

#### 고시트 폴리 저항 (High-Sheet Poly Resistor)
*   **PDK 모델명**: `sky130_fd_pr__res_high_po_0p69`
*   **특징**: 고정밀 고저항용 폴리실리콘 저항 ($W=0.69\,\mu\text{m}$ 고정).
*   **확정 모델 파라미터 및 저항 합성식** (LDO 3점 피팅 + BGR 단독 실측 잔차 0.007 + in-circuit 3중 검증):
    *   **단위 저항률 (`sheet`)**: **`470.976 Ω/µm`** (시트 저항 교차 검증: $463.5\,\Omega/\mu\text{m}$)
    *   **헤드 접촉 저항 (`head1`)**: **`262.85 Ω/단자`** (소자당 2헤드 고정 기생 저항 = **`525.70 Ω`**)
    *   **유닛 저항 실측치 ($L=4.416\,\mu\text{m}$)**: **`2605.5 Ω`**
    *   **N개 직렬 유닛 합성 길이 공식**: **`L_total = 5.5322 N - 1.1162`** $(\mu\text{m})$ (역산: $N = (L + 1.1162) / 5.5322$)
    *   **최소 저항 하한**: **`525.70 Ω`** (컨택 2헤드 전압 강하 기생분)
    *   **실제 BGR 소자 실측**: $R_1 = 16,742\,\Omega$ ($L=34.4500\,\mu\text{m}$), $R_2=R_6=R_7 = 115,697\,\Omega$ ($L=243.4600\,\mu\text{m}$), 실효 저항비 $R_2/R_1 = 6.911$
    *   **변종 저항 실측치 (참고용)**:
        *   `res_high_po_2p85`: `sheet` = $113.901\,\Omega/\mu\text{m}$, `head1` = $71.61\,\Omega$
        *   `res_high_po_5p73`: `sheet` = $56.642\,\Omega/\mu\text{m}$, `head1` = $36.38\,\Omega$
        *   (W비 스케일 정합 확인됨. 필요시 저저항 경로용 가용, 트림엔 `0p69` 유지)
*   **온도 곡률 2차 보상**: 저항 소자의 2차 온도 계수인 `tc2 = +1.22 ppm/°C²`의 강한 양의 곡률이 BJT $V_{BE}$ 전압의 음의 비선형 곡률($T \ln(T)$ 표류)을 보완하여 BGR 출력 곡선의 S자 굴곡을 평탄화시키는 온도 2차 보상(Cubic Curvature Compensation) 기작이 존재합니다.



### 3.1.1. 폴리 저항 2성분 모델 (헤드 TC 2성분 모델)

■ 구조
  res_high_po_0p69 는 몸통(폴리)과 헤드(양단 컨택 단자부)의 직렬이다.
    R(L) = 470.976 × L + 525.70 [Ω]   (헤드 262.85 Ω/단자 × 2)
  헤드는 길이 무관 고정 성분이며, **몸통과 온도계수가 다르다.**

■ 실측 (단독 저항, tt, -40~125°C, 1V, 조건 병기)
  L(µm)     R@27(Ω)    헤드비중   TC(ppm/°C)
  1.000        996.7     52.7%      321.3
  2.438      1,673.9     31.4%      412.0
  3.327      2,092.6     25.1%      438.7
  10.000     5,235.5     10.0%      502.7
  50.000    24,074.5      2.2%      536.1
  243.4600  115,696.7      0.5%      543.4
  → TC 가 L 에 따라 69% 변동. 헤드 TC ≠ 몸통 TC 확정.

■ 2성분 모델 (레이아웃 채팅 피팅, 잔차 0.1 ppm)
  TC_eff(R, n) = [(R - 525.7n)·TC_body + 525.7n·TC_head] / R
    TC_body = 545.3 ppm/°C,  TC_head = 120.6 ppm/°C  (몸통의 1/4.5)
    정리형: TC_eff = 545.3 - 223,265·n / R    (n = 헤드 쌍 수)
  피팅에 안 쓴 4점이 0.1 ppm 이내로 재현됨.
  ※ 기존 폴리 TC1 실측 +514 ppm 은 헤드가 섞인 실효값이었다.

■ 설계 귀결
  - 헤드 쌍당 TC 기여는 R 에 반비례 → 작은 저항일수록 민감
      R1(16,742 Ω) -13.34 / R2fix(108,570) -2.06 / R6·R7(115,697) -1.93 ppm/쌍
  - 비를 이루는 저항의 분할 수를 바꾸면 비가 온도에 따라 드리프트한다
      실측: R1 통짜 + R6 55분할 → TC 45.3 ppm (기준 7.5 대비 6배)
  - **"모든 저항을 같은 비율로 분할" 은 오답.** 작은 저항(R1)이 6.9배 민감하므로
    큰 저항만 분할하는 쪽이 손해가 작다.




### 3.1.2. gencell 서펜타인 모델 (레이아웃 추출 l 실측 확정)

■ gencell 서펜타인 모델 (N=8)
★ 굴곡 보정은 N 에 대해 단조가 아니다 — N 별 실측 필수.
  실측 굴곡당 증분: N=2 +1.26 / N=4 +0.1927 / N=7 +0.1438 / N=8 -0.0386 µm
  (N=2 는 더미 저항 LVS 불일치에서 역산, 나머지는 gencell 추출 실측)
  단일 N 의 계수를 다른 N 에 외삽하면 부호까지 틀린다.
  → 사용하는 N 마다 2점 실측으로 l_ext = a·L_col + b 를 개별 확정할 것.
  확정된 것: N=8 → l_ext = 8·L_col - 0.27 (L_col 4.34~28.71 전 구간 검증)

  - 실측 L 합성식: l_ext = 8·L_col - 0.27  (N=8 기준, 폭 8.88 µm, 높이 L_col + 2.68 µm)
  - 구 모델 $l = N·L + (N-1)×0.1927$ 폐기: 코너 계수가 N 마다 부호 변동 (N=4 +0.1927 / N=7 +0.1438 / N=8 -0.0386). N 별 2점 실측이 정본.

■ 최종 확정 저항 L (magic gencell N=8 실측값)
  - XR1: L = 34.4500 µm
  - XR6a,b / XR7a,b: L = 121.7300 µm (각)
  - XR2fix: L = 229.4100 µm
  - XR_cn: L = 91.2050 µm
  - (트림 세그먼트 b0~b3 은 현행 유지)
  - 스키매틱 L 을 실제 그려질 값에 맞춤으로써 LVS 정합과 전기적 정확도를 동시 확보.


#### 저항 코너 구조 (`corner_factor` 메커니즘)
*   **sky130 폴리 시트 수식**:
    $$\text{sw\_sky130\_fd\_pr\_\_res\_high\_po\_rs} = \{325.0 + \text{corner\_factor} \times 45.0\} + \text{MC\_PR\_SWITCH} \times \text{GAUSS}(0, 0.035, 1) \quad [\Omega/\square]$$
*   **트랜지스터 코너 종속성**: `corner_factor`는 독립된 변수가 아니라 트랜지스터 코너(`tt`/`ss`/`ff`)가 설정하는 전역 변수입니다. 즉, 저항 코너는 독립 설정되지 않고 트랜지스터 코너에 종속됩니다 (경로: `parameters_res_high.spice`, 각 FET 코너 섹션이 include).
*   **직관과 반대인 코너 동작 ($T=27\,^\circ\text{C}$ 실측 $R_{2,\text{eff}}$)**:
    *   **`ff` 코너**: $122.18\,\text{k}\Omega$ ($\text{corner\_factor} > 0 \rightarrow$ **저항 High**)
    *   **`tt` 코너**: $115.75\,\text{k}\Omega$
    *   **`ss` 코너**: $113.93\,\text{k}\Omega$ ($\text{corner\_factor} < 0 \rightarrow$ **저항 Low**)
    *   저항 스프레드 $\text{ff}/\text{ss} = +6.8\%$.
*   **물리적 귀결**: $I_{B,\text{EA}}$와 $I_{\text{div}}$가 동일한 `res_high_po`를 공유하므로, `corner_factor`가 비(ratio)에서 완벽히 상쇄됩니다. **비율계량(Ratiometric) 방식이 PDK 모델 레벨에서 구조적으로 보증됨**을 입증합니다.



#### PNP 바이폴라 (BJT)
*   **PDK 모델명**: `sky130_fd_pr__pnp_05v5_W0p68L0p68`
*   **특징**: 에미터 면적 $0.68\times0.68\,\mu\text{m}^2$ 규격의 바이폴라 소자. BGR 코어의 PTAT 전압 발생 축으로 사용.
*   **실효 에미터 비 정정**: BGR 매칭 비율을 $1:8$ (N=8)로 설정하고 단일 분지에 $3\,\mu\text{A}$를 주입할 때, 에미터 주변부 효과(Periphery Effect)에 따른 전류 이탈로 인해 실효 면적비는 $N_{eff} \approx 7.77$로 떨어집니다. 이로 인해 PTAT 기준 전압이 이론치($V_T \ln(8) \approx 53.78\,\text{mV}$) 대비 $-1.4\%$ 감소한 **$\Delta V_{BE} = 53.02\,\text{mV}$**로 고정되므로, 저항 비율 산출 계산 시 실측된 $53.02\,\text{mV}$를 물리 기준으로 사용해야 정밀한 Zero-TC 튜닝이 가능합니다.

---

### 3.2. MiM 커패시터 명세 및 공정 산포

*   **PDK 모델명**: `cap_mim_m3_1` (met3 / capm), `cap_mim_m3_2` (met4 / cap2m)
*   **단위 면적 용량 (`camimc`)**:

| 코너 | 값 | 대표치 대비 |
| :--- | :---: | :---: |
| **Typical** | `2.00 fF/µm²` (`2.00e-15` F/µm²) | — |
| **cap_low** | `1.778 fF/µm²` | **`-11.1%`** |
| **cap_high** | `2.231 fF/µm²` | `+11.5%` |

*   **적층 특성**: 두 소자는 동일한 `camimc`를 사용합니다. 동일 풋프린트로 적층·병렬 결선하면
    면적 증가 없이 **$4.0\,\text{fF}/\mu\text{m}^2$**를 확보할 수 있습니다.
*   **배치 이점**: MiM은 **met3~met4 층**이므로 액티브 회로 위에 겹쳐 배치할 수 있습니다.
    LDO의 $C_{out}$처럼 큰 용량이 필요한 경우 **실면적 벌금이 거의 없습니다.**
    단 (a) 하판 아래에 스위칭 회로를 두면 보상·출력 노드에 직접 주입되므로 배치에 주의하고,
    (b) `cap_mim_m3_2`의 상판 `cap2m`이 met5 인접 층이므로 **TinyTapeout의 met5 금지 규칙과
    간섭이 없는지 확인**해야 합니다 (`cap_mim_m3_1` 단층은 $2.0\,\text{fF}/\mu\text{m}^2$로 확실히 안전).
*   **안정성 평가 최악 조건**: 글로벌 **`cap_low` ($-11\%$)** 가 LDO 위상 마진 감쇄와
    BGR 기동 루프 지연 양쪽에서 가장 보수적인 조건을 형성하므로,
    **루프 안정성 검증의 고정 기준 코너**로 사용합니다.

### 3.3. thin-ox MOS 커패시터 — $C_{out}$ 용도로 기각

*   **기각 사유**: thin-ox MOS 커패시터의 절대 최대 정격이 $\approx 1.95\,\text{V}$인데,
    LDO의 **오버슈트 하드 스펙이 정확히 $1.95\,\text{V}$**입니다.
    즉 스펙을 위반하는 순간 **디캡이 가장 먼저 파괴되는 소자**가 되는 구조이므로 채택하지 않습니다.
    → $C_{out}$은 §3.2의 MiM 적층을 사용합니다.
*   **참고 — thick-ox $C_{ox}$ 역산치**: `pfet_g5v0d10v5` $W=400/L=0.5$ (기본 geometry,
    $V_{SG}=1.3$, $V_{SD}=1.5$, tt/27) 실측 $C_{gg} = 326.18\,\text{fF}$를 게이트 면적
    $200\,\mu\text{m}^2$로 나누면 $1.63\,\text{fF}/\mu\text{m}^2$이고, 포화 영역의 $\approx \tfrac{2}{3}C_{ox}$
    관계에서 **$C_{ox} \approx 2.4\,\text{fF}/\mu\text{m}^2$**입니다.
    (thin-ox 값은 당세션 미실측 — 인용 시 조건 병기 필요)

---

## 4. 몬테카를로 분석 제어 및 외부 루프 설정법

*   **분석 설정 파라미터**:
    *   `MC_MM_SWITCH = 1` (로컬 미스매치 활성화)
    *   `MC_PR_SWITCH = 1` (글로벌 공정 산포 활성화)
*   **파이썬 외부 제어 루프 방식 사용 이유**:
    *   ngspice 내부 `.control` 블록의 `repeat` 루프나 `mc_run` 명령을 사용하여 100회 이상 통계 분석을 돌리면, 시뮬레이터 내부 메모리 누적 오류 및 다차원 데이터 파일 쓰기(wrdata) 병목으로 인해 툴이 다운되거나 데이터 누락 사고가 잦게 일어납니다.
    *   따라서 파이썬 스크립트(`mc_split.py` 등)에서 `.spice` 파일의 스위치 값을 재생성해 디스크에 쓴 뒤, `ngspice -b` 배치를 단발 구동하여 결과 텍스트를 파일로 파싱하고 누적하는 **외부 제어 루프(Outer-loop execution)** 방식이 수백 회의 시뮬레이션을 메모리 붕괴 없이 구동할 수 있는 유일한 안정 검증책입니다.

---

## 5. 핵심 캐릭터리제이션 시뮬레이션 레시피

### 5.1. 다이오드 연결형 PMOS 특성화 기법 (Diode-connected Characterization)
*   **원인/배경**: 일반 2차 자승 법칙(Square-law)은 Moderate Inversion($V_{ov} \approx 50 \sim 130\,\text{mV}$) 영역에서 쇼트 채널 효과로 인해 크게 이탈합니다. 원하는 바이어스 전류($I_{bias} = 9.68\,\mu\text{A}$)를 공급하기 위한 정확한 소자 면적 및 게이트 드라이브 헤드룸 전압을 도출하기 위해, 트랜지스터를 다이오드로 묶고 강제 전류원으로 동작점을 찾는 기법이 사용됩니다.
*   **시뮬레이션 덱 코드 ( pm_char.spice )**:
    ```spice
    * PMOS 동작점 직접 도출 테스트 덱
    .lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
    
    .param W_val = 10u
    .param L_val = 2u
    .param M_val = 4
    .param I_bias = 9.68u
    
    * 소스(s)와 벌크(b)는 3.3V, 게이트(g)와 드레인(d)은 단일 노드로 결합
    XM1 d d s b sky130_fd_pr__pfet_g5v0d10v5 w={W_val} l={L_val} m={M_val}
    
    Vs s 0 3.3
    Vb b 0 3.3
    I1 d 0 {I_bias}
    
    .op
    .control
      run
      show xm1  ; vgs, vds, vth, gm, gds, vdsat 목록 직접 확인
      print (3.3 - v(d)) ; Vsg(=Vsd) 실측값 터미널 출력
    .endc
    .end
    ```
*   **실행 명령어**:
    ```bash
    docker exec iic-osic-tools_xvnc_uid_1000 bash -l -c "cd /foss/designs/designs/bgr_ldo/bgr && ngspice -b pm_char.spice"
    ```


---

## 6. pygmid 프레임워크 한계 및 ngspice 우회

*   **Spectre 전용 제약**: python gm/Id 프레임워크 `pygmid`의 데이터 추출 모듈(`sweep`)은
    Cadence Spectre 전용 구성요소(`pysweep.scs`, `SpectreSimulator` 인터페이스,
    `psf_utils` 이진 파서)에 완전히 종속되어 있어 ngspice에서 구동할 수 없습니다.
*   **우회 설계**: ngspice 배치 출력을 직접 파싱하여 4D 바이어스 배열을 재구성하는
    자체 스크립트 `lut/gen/run_sweep.py`를 개발했습니다.
*   **데이터 연동**: 산출된 `.pkl`은 `pygmid.Lookup` 클래스와 호환되도록 포맷을 정합했으며,
    조회부(보간 API)는 시뮬레이터 독립이므로 그대로 재사용합니다 (래퍼 `lut/lookup.py`).
*   **재생성 소요**: nfet 14분 23초 + pfet 11분 45초 (총 약 26분).
    상세 사양·부호 규약·정확도는 `lut/README.md`가 정본입니다.

---

## 7. ngspice 실행 가드레일 (사고 이력 기반)

1.  **PATH 상속 — `bash -l -c` 필수**
    `bash -c`는 로그인 프로파일을 읽지 않아 PATH에 ngspice가 없습니다(`command not found`).
    **python `subprocess`로 ngspice를 호출하는 스크립트도 마찬가지**입니다 —
    파이썬이 상속받는 PATH가 셸의 PATH이기 때문입니다.
    파일 조작만 하는 명령은 `bash -c`로 충분하지만, **툴을 실행하는 순간 `bash -l -c`** 로 바꾸십시오.
2.  **`.control` 블록에서 세미콜론(`;`)은 주석**
    ngspice의 `.control` ~ `.endc` 내부에서 `;`는 주석 시작 기호입니다.
    한 줄에 명령 두 개를 `;`로 이어 쓰면 **뒤쪽이 통째로 무시**되므로,
    한 라인에는 반드시 명령 하나만 기재합니다.
3.  **넷리스트 grep은 `grep -A1`**
    xschem이 추출한 넷리스트에서 긴 인스턴스 라인은 `+` continuation으로 나뉘며,
    `m`(multiplier)이나 `mult` 같은 스케일 파라미터가 **다음 줄에 숨는 경우가 잦습니다.**
    소자 치수 검증 시에는 반드시 `grep -A1 "소자명"` 으로 다음 행까지 확인하십시오.
4.  **재생성 후 산출물 mtime 확인**
    스윕·MC 등 장시간 작업 후에는 **모든 산출물의 갱신 시각을 확인**합니다.
    한쪽만 갱신된 stale 파일로 코드 동작을 역추론하다 26분 재작업이 발생한 이력이 있습니다.
    **코드의 동작을 데이터로 역추론하지 말고, 데이터의 생성 시점을 먼저 확인하십시오.**

---

---

## 8. 폴리 저항 2성분 모델 (헤드 TC)

### 8.1 소자 구조 및 2성분 분해
Sky130A `res_high_po_0p69` 저항 소자는 **몸통(폴리)**과 **헤드(양단 컨택 단자부)**의 직렬 합성으로 동작한다.
$$R(L) = 470.976 \cdot L + 525.70\ [\Omega]$$
* **헤드 저항**: 단자당 $262.85\,\Omega \times 2 = 525.70\,\Omega$
* **특징**: 헤드는 소자 길이에 무관하게 고정값이며, **몸통과 온도계수(TC)가 서로 다르다.**

### 8.2 실측 데이터 (단독 저항, tt, -40~125°C, 1V, .dc temp)

| $L\ (\mu\text{m})$ | $R@27\ (\Omega)$ | 헤드 비중 | $\text{TC}\ (\text{ppm}/^\circ\text{C})$ |
| ---: | ---: | ---: | ---: |
| 1.000 | 996.7 | 52.7% | 321.3 |
| 2.438 | 1,673.9 | 31.4% | 412.0 |
| 3.327 | 2,092.6 | 25.1% | 438.7 |
| 10.000 | 5,235.5 | 10.0% | 502.7 |
| 50.000 | 24,074.5 | 2.2% | 536.1 |
| 244.537 | 115,696.7 | 0.5% | 543.4 |

$\rightarrow$ 소자 길이 $L$에 따라 실효 TC가 **321.3에서 543.4 ppm/°C까지 69% 변동**하며, 헤드 TC $\neq$ 몸통 TC임이 확정되었다.

### 8.3 2성분 피팅 모델 (2점 피팅 + 4점 검증, 잔차 0.1 ppm)
$$\text{TC}_{\text{eff}}(R, n) = 545.3 - 223,265 \cdot \frac{n}{R}$$
* $n$: 헤드 쌍 수 (넷리스트 상 저항 소자 개수)
* $\text{TC}_{\text{body}} = 545.3\,\text{ppm}/^\circ\text{C}$
* $\text{TC}_{\text{head}} = 120.6\,\text{ppm}/^\circ\text{C}$ (몸통 TC의 약 $1/4.5$)
* *(참고: 기존 PDK 사양서의 폴리 TC1 단독값 $+514\,\text{ppm}$은 헤드 저항 성분이 혼입된 실효값이었음)*

### 8.4 설계 귀결
1. **R에 대한 민감도**: 헤드 쌍당 TC 기여는 저항값 $R$에 반비례하므로, 저항이 작을수록 헤드 추가에 따른 TC 변화가 극도로 민감하다.
   * $R_1$ ($16.7\,\text{k}\Omega$): $-13.34\,\text{ppm}/\text{쌍}$
   * $R_{2fix}$ ($108.6\,\text{k}\Omega$): $-2.06\,\text{ppm}/\text{쌍}$
   * $R_6, R_7$ ($115.7\,\text{k}\Omega$): $-1.93\,\text{ppm}/\text{쌍}$
2. **비대칭 분할에 의한 드리프트**: 비를 이루는 저항의 분할 수가 다르면 온도에 따라 저항비가 드리프트한다.
   * *실측 사례*: $R_1$ 통짜(1분할) + $R_6$ 55분할 ➔ TC가 $45.3\,\text{ppm}$으로 치솟음 (기준 $7.5\,\text{ppm}$의 6배).
3. **★ 분할 전략 규율**: "모든 저항을 같은 비율로 분할하는 것"은 오답이다. 작은 저항($R_1$)이 $6.9$배 더 민감하므로, 큰 저항만 분할하는 편이 전체 TC 손실을 줄이는 데 유리하다.

---

## 9. 서펜타인 레이아웃 환산 (Serpentine Conversion Rules)

### 9.1 서펜타인 치수 환산 (N=8 피치 기준)
$$l_{\text{ext}} = 8 \cdot L_{\text{col}} - 0.27$$
* **셀 가용 폭**: $0.69 + 7 \times 1.17 = 8.88\,\mu\text{m}$
* **셀 가용 높이**: $L_{\text{col}} + 2.68\,\mu\text{m}$

### 9.2 ★ $L_{\text{col}}$ 격자 제약 규율
$L_{\text{col}}$ 수치는 **반드시 $0.01\,\mu\text{m}$의 배수만 사용**해야 한다.
* **이유**: $0.005\,\mu\text{m}$ 격자의 홀수 배수(예: $4.315\,\mu\text{m} = 863 \times 0.005$)를 사용하면 Magic이 폴리 마스크를 23개 타일로 조각내면서 추출 $l$ 값이 튀는 현상(목표 $34.25\,\mu\text{m} \rightarrow 35.19\,\mu\text{m}$, $+0.94\,\mu\text{m}$ 변동)이 발생한다.
* **실측 검증**:
  * $4.300\,\mu\text{m} \rightarrow 34.13\,\mu\text{m}$ (타일 15개, 정상)
  * $4.320\,\mu\text{m} \rightarrow 34.29\,\mu\text{m}$ (타일 15개, 정상)
  * $4.330\,\mu\text{m} \rightarrow 34.37\,\mu\text{m}$ (타일 15개, 정상)
  * $4.340\,\mu\text{m} \rightarrow 34.45\,\mu\text{m}$ (타일 15개, 정상)
  * $4.315\,\mu\text{m} \rightarrow 35.19\,\mu\text{m}$ (타일 23개, 이상 발생)

### 9.3 굴곡(Bend) 보정 계수 및 gencell 오차
* **굴곡 당 증분 실측값** (N에 따라 단조 증가하지 않음):
  * $N=2$: $+1.26\,\mu\text{m}$
  * $N=4$: $+0.1927\,\mu\text{m}$
  * $N=7$: $+0.1438\,\mu\text{m}$
  * $N=8$: $-0.0386\,\mu\text{m}$
  * *규율*: 단일 N 계수를 다른 N에 외삽하면 부호까지 달라지므로, 반드시 N별 2점 실측을 정본으로 삼는다.
* **gencell 파라미터 오차**: gencell 내부 모델($\rho=319.8\,\Omega/\square$, $\text{term}=194.82\,\Omega$)은 `ngspice` 정본($325.0\,\Omega/\square$, $262.85\,\Omega$)과 $+1.22\%$ 차이가 난다. LVS는 W/L 비율을 대조하므로 무해하나 PEX 저항 추출값에는 반영된다.

---

## 10. PEX 직접 스윕 기법 (PEX Direct Parameter Sweep)

레이아웃 파라미터를 바꿔 회로를 최적화할 때, 스키매틱 모델로 스윕하면 PEX 추출 후 최적점이 이동하여 레이아웃을 두 번 수정하게 되는 문제가 발생한다. PEX 넷리스트에서 해당 소자의 파라미터를 직접 스윕하면 이러한 재작업을 방지할 수 있다.

### 10.1 전제 조건
Magic `ext2spice` 추출 시 PDK 소자가 서브회로 인스턴스로 유지되는 경우
(예: `X67 net1_t1 VBE8 VGND_t67 sky130_fd_pr__res_high_po_0p69 l=34.45`)
$\rightarrow$ 이 `l` 값만 변경하면 컨택 저항(Contact R), 배선 저항, 기생 용량(C)은 실제 추출된 수치 그대로 유지된다.

### 10.2 실행 절차
1. **대상 소자 인스턴스 검색**: PEX 넷리스트에서 변경할 대상 소자를 식별 (`grep '^X.*모델명'`)
2. **PEX 사본 생성**: 해당 `l` / `w` 값만 치환한 PEX 넷리스트 사본을 N개 생성
3. **시뮬레이션 수행**: 각 사본에 래퍼(Wrapper)와 Testbench(TB)를 결합하여 시뮬레이션 실행
4. **★ 실측 검증**: 기존 PEX 결과가 원본 값에서 정확히 재현되는지 먼저 확인

### 10.3 실적 (R1 TC 최적화 사례)
* **스키매틱 + 컨택 모델 예측**: $12.05\,\text{ppm}/^\circ\text{C}$ (PEX 실측 $10.9\,\text{ppm}$, 오차 $1.15\,\text{ppm}$)
* **PEX 직접 스윕**: 원본 값($L=34.45$)에서 $10.85\,\text{ppm}/^\circ\text{C}$로 PEX 실측을 정확히 재현.
* **최적점 확정**: $L=34.25\,\mu\text{m}$ ($6.13\,\text{ppm}$) 근방 중, $0.01\,\mu\text{m}$ 격자 규약을 준수한 **$L=34.29\,\mu\text{m}$에서 최소점 $\mathbf{6.70\,\text{ppm}/^\circ\text{C}}$ 확정** $\rightarrow$ 레이아웃 재작업 **1회로 종료**.

### 10.4 한계 및 컨택 모델링 주의 사항
* **치수 변경 한계**: 소자 치수 변경에 따른 배선 길이의 미세 변화(수십 $\text{m}\Omega$)는 반영되지 않으나, 영향이 미미하여 무시 가능하다.
* **분해 소자 처리**: 소자가 기본 저항(`R`)으로 완전 분해(Flatten)된 경우, 소자 몸통 성분만 선별하여 스케일링해야 하므로 가공 방식이 복잡해진다.
* ★ **컨택 모델링 주의**: 폴리 컨택을 $L$ 연장으로 흉내내면 컨택부에 몸통 TC($545.3\,\text{ppm}$)가 잘못 부여된다. Magic은 컨택을 tech file 고정저항으로 추출하므로, **TC가 없는 plain R (저항 성분만)**로 기재해야 한다.
