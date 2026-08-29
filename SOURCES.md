# TinyTapeout 아날로그(BGR+LDO / TTSKY26c) — 소스 모음

> 용도 구분: **문서 URL → NotebookLM 소스로 추가 OR snapshot-docs.py로 로컬 .md** · **GitHub 레포 → clone-repos.sh로 로컬 클론**

---

## ▼ AI 도구에 그대로 붙여넣을 문서 URL (복붙용)

```
https://tinytapeout.com/specs/analog/
https://tinytapeout.com/specs/pinouts/
https://tinytapeout.com/specs/gpio/
https://tinytapeout.com/specs/clock/
https://tinytapeout.com/specs/pcb/
https://tinytapeout.com/guides/local-hardening/
https://tinytapeout.com/guides/laying-standard-cells-with-magic/
https://tinytapeout.com/guides/analog-discovery/
https://tinytapeout.com/guides/get-started-demoboard/
https://tinytapeout.com/guides/documentation/
https://tinytapeout.com/making_asics/
https://tinytapeout.com/faq/
https://tinytapeout.com/chips/
https://tinytapeout.com/chips/silicon-proven/
https://www.zerotoasiccourse.com/analog/
https://zerotoasiccourse.com/terminology/
```

*(주: 지난번 유튜브 링크 2개는 출처 재확인이 안 돼서 뺐습니다. 영상 학습은 Zero to ASIC 코스가 더 정확합니다.)*

---

## 1. 필수 스펙
- Analog Specs (성경) — https://tinytapeout.com/specs/analog/
- Pinouts (물리핀 ↔ ua/ui/uo) — https://tinytapeout.com/specs/pinouts/
- GPIO pins (PG/EN 무료 디지털핀) — https://tinytapeout.com/specs/gpio/
- Clock — https://tinytapeout.com/specs/clock/
- PCB (devkit/breakout) — https://tinytapeout.com/specs/pcb/

## 2. 플로우 가이드
- Local hardening (GDS/프리체크) — https://tinytapeout.com/guides/local-hardening/
- Magic 커스텀 레이아웃 — https://tinytapeout.com/guides/laying-standard-cells-with-magic/
- Analog Discovery 측정 — https://tinytapeout.com/guides/analog-discovery/
- Demoboard 부팅/Commander — https://tinytapeout.com/guides/get-started-demoboard/
- 프로젝트 문서화 — https://tinytapeout.com/guides/documentation/

## 3. 개요 · 레퍼런스
- Making ASICs — https://tinytapeout.com/making_asics/
- FAQ — https://tinytapeout.com/faq/
- Chips (셔틀별 마감/배송) — https://tinytapeout.com/chips/
- Silicon-proven projects — https://tinytapeout.com/chips/silicon-proven/

## 4. 학습
- Zero to ASIC — Analog 코스 — https://www.zerotoasiccourse.com/analog/
- 용어 사전 — https://zerotoasiccourse.com/terminology/

---

## ▼ GitHub 레포 (clone-repos.sh로 로컬 클론 — Antigravity workspace)

### 필수
- 제출 템플릿 — https://github.com/TinyTapeout/ttsky-analog-template
- 오픈소스 툴 도커 — https://github.com/iic-jku/iic-osic-tools
- 아날로그 플로우 스크립트 — https://github.com/iic-jku/osic-multitool

### 레퍼런스 설계 (BGR/LDO/power)
- https://github.com/westonb/sky130-analog
- https://github.com/iic-jku/sky130_power_gate

### PCB / 측정 (칩 수령 후)
- https://github.com/TinyTapeout/tt-demo-pcb
- https://github.com/tinytapeout/breakout-pcb

### 선택 (NotebookLM을 MCP로 붙일 때만 · 비공식/불안정)
- https://github.com/jackc1111/antigravity-notebooklm-mcp

---

## ▼ 웹 툴 (클론 X · 브라우저에서 사용)
- 가격 계산기 — https://app.tinytapeout.com/calculator
- 프로젝트 생성/제출 — https://app.tinytapeout.com/projects/create
- 타일/PCB 선구매 — https://app.tinytapeout.com/prepurchase
- Commander (칩 테스트) — https://commander.tinytapeout.com/
- GDS 뷰어 — https://gds-viewer.tinytapeout.com/
- 스토어 — https://store.tinytapeout.com/
- Discord — https://tinytapeout.com/discord
