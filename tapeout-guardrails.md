# Tapeout guardrails — BGR + LDO (TTSKY26c / sky130A)

Always On. 아래는 협상 불가 제약. 위반 감지 시 멈추고 사용자에게 알릴 것.

## 프로세스 / 제출 (TinyTapeout sky130A)
- 타깃 PDK는 sky130A 하나뿐. 다른 PDK(ihp-sg13g2, gf180)로 하드닝 금지.
- 레이아웃에서 **met5 사용 금지** (TT 파워그리드 전용).
- 파워핀은 **met4** 수직 스트라이프, TT 규칙 준수.
- `info.yaml` 수정 시 항상 `repos/ttsky-analog-template`의 스키마와 대조.
- 아날로그 슬롯은 1x2 또는 2x2만. 핀은 ua[0]부터 순서대로.

## 전기적 제약 (이 프로젝트)
- BGR 출력 V_ref = 1.2 V (기준만 생성, 부하 구동 안 함).
- LDO: 입력 VAPWR = 3.3 V → 출력 V_out = 1.8 V.
- 분압비: V_out = (1 + R1/R2) × V_ref, R1=위(V_out→V_fb), R2=아래(V_fb→GND), **R2 = 2·R1**.
- 분압기는 V_out에 연결 (BGR 로딩 금지). V_ref는 error amp + 입력으로만.
- **Error amp 전원 = VAPWR (3.3 V)** — 1.8 V로 급전 금지 (PMOS pass 못 끔).
- 부하 전류 가정 ≤ 5 mA. PDN: 20 mA에서 0.1 V drop — 이 범위 벗어나지 말 것.
- 안정도(PM)는 경부하·중부하 양쪽에서 검증. PSRR은 AC로 확인.

## 작업 방식
- 스펙 확인은 `docs/` 원문 인용 — 요약 말고 정확한 규칙 그대로.
- 트랜지스터 사이징은 sky130 소자로 재설계 (28nm 값 복사 금지). gm/Id 활용.
- BGR startup 회로(0전류 축퇴점 탈출)와 LDO soft-start는 별개로 구현.
- 값을 임의로 지어내지 말 것. 근거는 NOTES.md / docs / 시뮬 결과.
