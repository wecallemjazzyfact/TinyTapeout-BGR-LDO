# 03_PDK_환경.md (PDK 핵심 명세 및 시뮬레이션 개발 환경 구축서)

### TL;DR (3줄 요약)
1. TinyTapeout 아날로그 설계를 위한 도커 컨테이너 실행 환경, 프로젝트 디렉토리 트리 및 GUI 툴(Xschem/Magic) 구동 절차를 규정합니다.
2. SkyWater 130nm PDK의 핵심 소자(5V NMOS/PMOS, 고시트 저항, PNP BJT, MiM 커패시터)의 모델명과 이산 빈(Bin) 경계 한계를 분석했습니다.
3. pygmid Spectre 전용 한계 우회 방안, 몬테카를로 split 구동 제어법 및 3대 ngspice 실행 가드레일을 구축하여 검증 무결성을 확보했습니다.

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
│     ├─ top/                # BGR + LDO 통합 칩 스키매틱 및 핀 매핑 폴더
│     ├─ layout/             # Magic 레이아웃 (.mag) 및 GDS/LEF 산출물
│     ├─ milestones/         # 01~09 개발 마일스톤 증거 보관실
│     ├─ work/               # 로컬 DRC 및 LVS 검증용 임시 폴더
│     └─ lut/                # gm/Id Look-Up Table 프로젝트 공용 폴더
```

---

## 3. PDK 소자 모델 전체 목록 및 설계 함정

*   **PDK 경로**: `/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice` (`tt` 코너 라이브러리 사용)

### 3.1. 소자 목록 및 파라미터 명세

#### NMOS 트랜지스터
*   **PDK 모델명**: `sky130_fd_pr__nfet_g5v0d10v5`
*   **특징**: 5V/10.5V Thick-Oxide 고전압 NMOS 소자. LDO 오차 증폭기의 하단 스택 및 BGR active mirror 하단 평형 제어 장치에 사용.
*   **바디 효과 주의 사항**: 벌크가 접지(0V)되고 소스가 공중으로 뜨는 회로 구성(예: 등화쌍 XM3/XM4, 소스 전위 $pprox 0.78	ext{V}$) 시, $V_{SB} pprox 0.78\,	ext{V}$에 의한 바디 효과로 인해 문턱 전압 $V_{thn}$이 **`0.798 V ➔ 1.069 V`**로 $271\,	ext{mV}$가량 치솟는 물리 현상이 존재함. 따라서 전압 헤드룸 예산 설계 시 $V_{GS}$ 상승에 따른 마진 하락을 선대입하여 계산해야 합니다.

#### PMOS 트랜지스터
*   **PDK 모델명**: `sky130_fd_pr__pfet_g5v0d10v5`
*   **특징**: 5V/10.5V Thick-Oxide 고전압 PMOS 소자. BGR 메인 바이어스 거울 및 LDO 패스 소자(Pass Device)로 사용.
*   **L 치수 제한 (PDK Binning 함정)**: sky130 bsimg4 모델 카드의 구간 경계(bin) 정의 상, 단일 FET의 최대 채널 길이는 **`20 µm`**로 단단히 묶여 있습니다. 만약 스타트업 감지 소자 설계 시 누설 전류 극소화를 위해 단일 트랜지스터 $L = 60\,\mu	ext{m}$로 넷리스트를 작성하면 `could not find a valid modelname` 에러가 떨어지며 시뮬레이션이 붕괴합니다. 따라서 $L > 20\,\mu	ext{m}$의 초대형 L이 필요한 경우 반드시 복수의 서브 소자를 **직렬 스택(Series Stack)** 형태로 결선하여 유효 $L$을 확보해야 합니다.

#### 고시트 폴리 저항 (High-Sheet Poly Resistor)
*   **PDK 모델명**: `sky130_fd_pr__res_high_po_0p69`
*   **특징**: 고정밀 고저항용 폴리실리콘 저항 ($W=0.69\,\mu	ext{m}$ 고정, 시트 저항 $pprox 2\,	ext{k}\Omega/	ext{sq}$).
*   **온도 곡률 2차 보상**: 저항 소자의 2차 온도 계수인 `tc2 = +1.22 ppm/°C²`의 강한 양의 곡률이 BJT $V_{BE}$ 전압의 음의 비선형 곡률($T \ln(T)$ 표류)을 보완하여 BGR 출력 곡선의 S자 굴곡을 평탄화시키는 온도 2차 보상(Cubic Curvature Compensation) 기작이 존재합니다. 단, 저항 헤드의 접촉 저항($R_{head} pprox 780\,\Omega$) 성분이 기생 기여하므로 유닛 셀 단위 매칭 시 $R_{head}$를 합산한 실효 저항비를 매칭해야 합니다.

#### PNP 바이폴라 (BJT)
*   **PDK 모델명**: `sky130_fd_pr__pnp_05v5_W0p68L0p68`
*   **특징**: 에미터 면적 $0.68	imes0.68\,\mu	ext{m}^2$ 규격의 바이폴라 소자. BGR 코어의 PTAT 전압 발생 축으로 사용.
*   **실효 에미터 비 정정**: BGR 매칭 비율을 $1:8$ (N=8)로 설정하고 단일 분지에 $3\,\mu	ext{A}$를 주입할 때, 에미터 주변부 효과(Periphery Effect)에 따른 전류 이탈로 인해 실효 면적비는 $N_{eff} pprox 7.77$로 떨어집니다. 이로 인해 PTAT 기준 전압이 이론치($V_T \ln(8) pprox 53.78\,	ext{mV}$) 대비 $-1.4\%$ 감소한 **$\Delta V_{BE} = 53.02\,	ext{mV}$**로 고정되므로, 저항 비율 산출 계산 시 실측된 $53.02\,	ext{mV}$를 물리 기준으로 사용해야 정밀한 Zero-TC 튜닝이 가능합니다.

### 3.2. MiM 커패시터 명세 및 공정 산포
*   **PDK 모델명**: `cap_mim_m3_1` 및 `cap_mim_m3_2`
*   **단위 면적 커패시턴스 (camimc)**:
    *   **Typical (대표치)**: $2.00\,	ext{fF}/\mu	ext{m}^2$ (`2.00e-15` F/um^2)
    *   **Cap-Low 코너 (최소값 코너)**: $1.778\,	ext{fF}/\mu	ext{m}^2$ (`1.778e-15` F/um^2, 대표치 대비 **-11.1%**)
    *   **Cap-High 코너 (최대값 코너)**: $2.231\,	ext{fF}/\mu	ext{m}^2$ (`2.231e-15` F/um^2, 대표치 대비 **+11.5%**)
*   **적층형 결선 특성**: `cap_mim_m3_1`과 `cap_mim_m3_2`는 동일한 단위 면적 커패시턴스(`camimc`) 파라미터를 사용합니다. 레이아웃 상에서 동일 풋프린트로 적층(Stacking)하여 병렬 결선할 경우, 면적 증가 없이 **$4.0\,	ext{fF}/\mu	ext{m}^2$**의 단위 면적 용량을 안전하게 설계할 수 있습니다.
*   **안정성 평가 최악 조건**: 몬테카를로 분석 및 코너 시뮬레이션 시 글로벌 `-11%`가 감쇄되는 `cap_low` 변이 지점이 LDO 오차 증폭기의 위상 마진(Phase Margin) 감쇄 및 BGR 기동 시간 루프 지연 평가에서 가장 보수적이고 불리한 최악 조건(Worst-case corner)을 형성하므로, 루프 안정성 보상 설계의 검증 기준으로 고정해야 합니다.

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
*   **원인/배경**: 일반 2차 자승 법칙(Square-law)은 Moderate Inversion($V_{ov} pprox 50 \sim 130\,	ext{mV}$) 영역에서 쇼트 채널 효과로 인해 크게 이탈합니다. 원하는 바이어스 전류($I_{bias} = 9.68\,\mu	ext{A}$)를 공급하기 위한 정확한 소자 면적 및 게이트 드라이브 헤드룸 전압을 도출하기 위해, 트랜지스터를 다이오드로 묶고 강제 전류원으로 동작점을 찾는 기법이 사용됩니다.
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

## 6. pygmid 프레임워크 한계 및 ngspice 우회 방안
*   ** Specter 전용 제약**: python gm/Id 프레임워크인 `pygmid` 패키지의 원본 데이터 추출 모듈(`sweep`)은 내부적으로 Cadence Spectre 전용 시뮬레이션 환경 파서(`pysweep.scs`, `SpectreSimulator` 인터페이스, `psf_utils` 이진 데이터 추출 라이브러리)에 완전 종속되어 개발되었습니다.
*   **오픈소스 우회 설계**: 오픈소스 시뮬레이터인 ngspice 환경에서는 해당 모듈의 직접 구동이 불가능하므로, 당사는 ngspice 배치 시뮬레이션 데이터를 직접 파싱하여 4차원 바이어스 어레이 데이터 테이블을 재구성하는 독자적인 추출 스크립트(`run_sweep.py`)를 개발하였습니다.
*   **데이터 연동**: 추출이 끝난 pickle 형식의 소자 테이블(`.pkl`) 데이터는 `pygmid.Lookup` 클래스와 호환되도록 데이터 포맷을 정합하였으며, 최종 사이징 분석 단계에서는 pygmid의 보간 및 조회 API를 그대로 재사용(Wrapper 모듈 `lookup.py` 사용)하도록 인프라를 확정지었습니다.

---

## 7. ngspice 시뮬레이션 개발 실행 규칙 (Execution Guardrails)

1.  **컨테이너 기반 실행 보장 (PATH 상속)**: python `subprocess` 등을 사용하여 ngspice 배치를 백그라운드로 자동 실행하는 스크립트도 셸 환경의 PATH 및 환경 변수 종속성을 그대로 상속받도록 반드시 **`docker exec -l`** 또는 **`bash -l -c`** 셸 옵션을 매핑하여 컨테이너 환경 내에서 실행되도록 보장해야 합니다.
2.  **control 블록 내부 세미콜론(;) 사용 제한**: ngspice의 `.control` ~ `.endc` 실행 제어 블록 내부에서 **세미콜론(`;`)은 주석 시작 기호**로 동작합니다. 따라서 복수의 ngspice 명령어를 한 줄에 줄여 쓰기 위해 `;`로 구분하여 넷리스트를 작성하면, 뒤쪽 명령어 전체가 주석으로 간주되어 무시됩니다. 한 라인에는 반드시 단 하나의 명령어만 분리하여 기재해야 합니다.
3.  **넷리스트 Continuation (+) 라인 확인**: xschem 등에서 스키매틱을 통해 SPICE 넷리스트를 자동 추출할 때, 긴 인스턴스 라인은 줄바꿈 기호인 **`+`** 라인으로 나뉘어 기재됩니다. 이 때 `m` (multiplier) 또는 `mult`와 같은 스케일 파라미터가 continuation 라인 밑으로 숨는 경우가 잦으므로, 넷리스트 grep 조사 시에는 오판 방지를 위해 반드시 **`grep -A1 "소자명"`** 형태로 다음 행까지 조사하여 정밀한 치수를 검증해야 합니다.
