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
*   **특징**: 고정밀 고저항용 폴리실리콘 저항 ($W=0.69\,\mu\text{m}$ 고정, 시트 저항 $\approx 2\,\text{k}\Omega/\text{sq}$).
*   **온도 곡률 2차 보상**: 저항 소자의 2차 온도 계수인 `tc2 = +1.22 ppm/°C²`의 강한 양의 곡률이 BJT $V_{BE}$ 전압의 음의 비선형 곡률($T \ln(T)$ 표류)을 보완하여 BGR 출력 곡선의 S자 굴곡을 평탄화시키는 온도 2차 보상(Cubic Curvature Compensation) 기작이 존재합니다. 단, 저항 헤드의 접촉 저항($R_{head} \approx 780\,\Omega$) 성분이 기생 기여하므로 유닛 셀 단위 매칭 시 $R_{head}$를 합산한 실효 저항비를 매칭해야 합니다.

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
