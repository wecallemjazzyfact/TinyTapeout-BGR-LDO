# tt-analog workspace — 셋업 & Antigravity 런북

## 폴더 구조
```
tt-analog/
├─ repos/                 # clone-repos.sh 결과 (읽기 전용 참고)
├─ docs/                  # snapshot-docs.py 결과 (스펙 .md, 에이전트가 인덱싱=자체 RAG)
├─ designs/
│  └─ bgr_ldo/
│     ├─ src/             # xschem 스키매틱 (.sch, .sym)
│     ├─ sim/             # ngspice testbench (.spice) + 결과
│     ├─ layout/          # magic (.mag) + gds
│     └─ NOTES.md         # ★ 에이전트가 스펙에서 뽑은 제약 요약 (경량 컨텍스트)
├─ SOURCES.md
├─ clone-repos.sh
└─ snapshot-docs.py
```

## 셋업 (터미널, 1회)
```
chmod +x clone-repos.sh && ./clone-repos.sh
pip install requests beautifulsoup4 markdownify && python snapshot-docs.py
```
그 다음 Antigravity에서 `tt-analog` 폴더를 workspace로 엽니다.

---

## Antigravity 작업 순서 (프롬프트 예시)

### 0단계 — 제약 distill  ★토큰 문제의 진짜 해법
> "docs/analog-specs.md, docs/pinouts.md, docs/gpio.md, 그리고
> repos/ttsky-analog-template의 info.yaml과 README를 읽고, 아날로그 제출의
> 하드 제약을 designs/bgr_ldo/NOTES.md에 표로 정리해줘. 항목: 사용 가능
> 아날로그 핀(ua[]) 개수·순서 규칙, 파워핀(VDD/VAPWR/VGND) 규칙, 금지 메탈층,
> 타일 크기(1x2/2x2), info.yaml 필수 키. 각 항목 옆에 출처 파일명도 적어줘."

→ 이후엔 이 **NOTES.md(작음)만 참조**하면 되므로, 매 턴 대용량 스펙을 다시
읽지 않습니다. NotebookLM RAG보다 나은 이유: 요약본을 **네가 직접 보고 검수**할
수 있고, 원문(docs/)도 그대로 남아서 정밀 확인이 필요할 때 인용 가능.

### 1단계 — 레퍼런스 분석
> "repos/sky130_power_gate와 repos/sky130-analog를 훑고, 우리 BGR+LDO에
> 재사용할 구조(PMOS pass device, 밴드갭 코어, 커런트 미러)를 NOTES.md에
> 추가해줘. sky130 소자명(pnp, res, moscap)과 주의점도 정리."

### 2단계 — 설계 스캐폴딩
> "designs/bgr_ldo/src/에 xschem top 스키매틱 뼈대와, sim/에 ngspice
> testbench 템플릿 4종(op-point, DC line/load sweep, AC PSRR, transient)을
> 만들어줘. NOTES.md 제약 반영: 입력 3.3V(VAPWR) → 출력 1.8V, 부하 ≤5mA,
> PG/EN은 디지털핀(uo_out/ui_in)."

### 3단계~ — 블록별 반복 설계·검증
- 블록 단위로 프롬프트 스코프: BGR 코어 → LDO 루프(PM/PSRR) → soft-start → PG 비교기
- ngspice 결과 파싱/플롯도 에이전트에 위임 ("sim 결과에서 PM, UGB, PSRR@1kHz 뽑아서 표로")
- 레이아웃 단계: `docs/guide-magic-layout.md` 참조시키기
- 제출 전: `docs/guide-local-hardening.md`로 프리체크(DRC/LVS) 흐름 확인

---

## 에이전트에게 각인시킬 규칙 (workspace rules에 넣기)
- 스펙 확인은 항상 `docs/` 원문 인용 — 요약 말고 정확한 규칙 그대로.
- `info.yaml` 수정 시 `repos/ttsky-analog-template` 스키마와 대조.
- **met5 사용 금지, 파워핀은 met4** — NOTES.md 체크리스트로 매번 확인.
- 부하 전류/PDN 가정은 NOTES.md 값(≤5mA, 20mA→0.1V drop) 벗어나지 말 것.

---

## (선택) NotebookLM MCP를 굳이 쓰겠다면
1. `repos/antigravity-notebooklm-mcp` 빌드 → Google 브라우저 인증(비공식, 세션 방식).
2. Antigravity → Settings → MCP Servers 에 등록.
3. NotebookLM에 SOURCES.md의 문서 URL을 소스로 추가.
4. 에이전트에 "notebooklm에서 ~ 찾아줘"로 질의.

⚠ 이 MCP 서버들은 공식 API가 아니라 리버스엔지니어링이라, Google이 뭔가 바꾸면
프로젝트 중간에 끊길 수 있음. 마감 있는 작업의 **주력 지식베이스로는 비권장**.
docs/ 로컬 방식이 더 안전하고 정밀함.
