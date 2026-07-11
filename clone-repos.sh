#!/usr/bin/env bash
# =====================================================================
# TinyTapeout 아날로그 (BGR + LDO) 프로젝트용 레포 일괄 클론
# 사용법:  chmod +x clone-repos.sh && ./clone-repos.sh
# 결과:    ./tt-analog/repos/ 아래에 모든 레포가 클론됨
#          Antigravity에서 tt-analog 폴더를 workspace로 열면 됨
# =====================================================================
set -e
mkdir -p tt-analog/repos && cd tt-analog/repos

echo "== 1. TinyTapeout 제출 템플릿 (필수 · sky130A/ChipFoundry 전용) =="
git clone --depth 1 https://github.com/TinyTapeout/ttsky-analog-template.git

echo "== 2. 오픈소스 툴체인 =="
# iic-osic-tools: 클론 후 start 스크립트로 Docker 이미지를 pull 하는 용도
#                 (코드를 읽는 게 아니라 도커 실행 스크립트 모음)
git clone --depth 1 https://github.com/iic-jku/iic-osic-tools.git
git clone --depth 1 https://github.com/iic-jku/osic-multitool.git

echo "== 3. 레퍼런스 설계 (BGR / LDO / power 빌딩블록) =="
git clone --depth 1 https://github.com/westonb/sky130-analog.git
git clone --depth 1 https://github.com/iic-jku/sky130_power_gate.git

echo "== 4. PCB / 측정 인터페이싱 (칩 수령 후, 2027년) =="
git clone --depth 1 https://github.com/TinyTapeout/tt-demo-pcb.git
git clone --depth 1 https://github.com/tinytapeout/breakout-pcb.git

# --- 선택: NotebookLM을 굳이 MCP로 붙이고 싶을 때만 ---
# git clone --depth 1 https://github.com/jackc1111/antigravity-notebooklm-mcp.git

echo ""
echo "완료 ✅  tt-analog/ 폴더를 Antigravity workspace로 열면 됩니다."
echo "다음 단계: cd iic-osic-tools && (README의 start 스크립트로 Docker 이미지 pull)"
