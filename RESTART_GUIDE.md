# 🚀 TinyTapeout 아날로그 설계 환경 재시작 가이드 (PC 재부팅 후)

이 가이드는 PC를 재부팅한 이후 Docker 환경에서 Xschem 및 설계 도구들을 다시 실행하여 작업을 시작하는 방법을 설명합니다.

사용하시는 구동 모드(X11 모드 또는 VNC 웹 모드)에 맞춰 선택하여 진행하세요.

---

## 1. 공통 준비 단계
1. **Docker Desktop 실행**: Windows에서 Docker Desktop 앱을 실행하고, 작업 표시줄 우측 하단의 고래 아이콘이 **초록색(Running)**이 될 때까지 기다립니다.
2. **WSL 터미널 열기**: WSL(Ubuntu) 터미널을 실행합니다.
3. **런처 스크립트 경로로 이동**:
   ```bash
   cd /mnt/c/Users/aa/Desktop/school/TinyTapeout/open-source/IIC-OSIC-TOOLS
   ```

---

## 2. 구동 모드 선택 (X11 vs VNC)

### 📌 옵션 A. MobaXterm 연동 모드 (X11 모드)
> [!NOTE]
> 윈도우에 설치된 MobaXterm의 X Server를 통해 터미널과 Xschem 창을 직접 윈도우 화면에 띄우는 모드입니다.
> 단순히 도커 GUI의 '시작' 버튼만 누르면 윈도우와 연결해주는 `socat` 통신 브릿지가 실행되지 않으므로, **반드시 아래 스크립트를 통해 실행**해야 합니다.

1. Windows에서 **MobaXterm을 실행**하고 X Server가 활성화되어 있는지 확인합니다.
2. WSL 터미널에서 다음 스크립트를 실행합니다:
   ```bash
   ./start_x.sh
   ```
   * *기존 컨테이너가 존재하여 `s` (start) / `r` (remove) 선택 창이 뜬다면, **`s`**를 눌러 시작합니다.*
3. 윈도우 화면에 가상 터미널 창이 자동으로 실행됩니다.

---

### 📌 옵션 B. 브라우저 접속 모드 (VNC 웹 모드)
> [!NOTE]
> 브라우저 탭을 통해 가상 리눅스 데스크톱 환경 전체를 조작하는 모드입니다. MobaXterm이 없어도 작동합니다.

1. WSL 터미널에서 다음 스크립트를 실행합니다:
   ```bash
   ./start_vnc.sh
   ```
   * *동일하게 선택 창이 뜨면 **`s`**를 입력합니다.*
2. Windows 웹 브라우저(Chrome, Edge 등)를 열고 아래 주소로 접속합니다:
   * **주소:** `http://localhost:80/?password=abc123`

---

## 3. Xschem 실행 및 작업 재개 (중요)
VNC 브라우저 창 또는 MobaXterm을 통해 열린 **가상 리눅스 터미널**에서 아래 명령을 입력하여 작업을 재개합니다.

> [!WARNING]
> **Xschem의 핵심 철칙**
> Xschem은 프로그램이 켜진 시점의 폴더를 기준으로 로컬 심볼(`.sym`)들을 검색합니다. 
> 경로가 꼬여 심볼이 깨지는 것을 막으려면 **반드시 아래와 같이 해당 프로젝트 폴더로 이동한 뒤 실행**해야 합니다.

```bash
# 1. 시뮬레이션 및 설계에 사용할 PDK 환경 변수 활성화 (이미 .bashrc에 영구 등록해 두었다면 생략 가능)
export PDK=sky130A

# 2. 작업할 프로젝트 폴더의 xschem 폴더로 직접 이동
cd /foss/designs/SKY130_SAR-ADC1/xschem

# 3. xschem으로 회로도 열기
xschem adc_top.sch
```
