# Magic Layout Session Checklist & Safety Guide

This checklist enforces mandatory verification steps before editing, after editing, and before running LVS in Magic VLSI, based on real accident history from the TinyTapeout BGR & LDO layout session (`BGR_LAYOUT_HANDOFF.md` §2 & Appendix B).

---

## 1. 🔍 편집 전 (Before Editing Checklist)

| # | 체크 항목 | 검증 방법 & 명령 | 실제 사고 사례 (1줄) |
| ---: | :--- | :--- | :--- |
| **1.1** | **`erase` 박스 겹침 관통 점검** | `box` 영역 내 레이어 덤프 후 복구 대상 기록 | **사고 사례**: `erase metal3` 박스가 `VBE1` 세로를 삭제하여 $V_{BE1}$ 노드가 남북 두 섬으로 분리됨. |
| **1.2** | **라벨 위치의 층 단독 여부 확인** | `rlabel <layer>`로 층 명시 + 교차 노드 피함 | **사고 사례**: `VGND` 포트 라벨을 (60.00, -1.95)에 찍었으나 $V_{BE1}$ met3와 겹쳐 $V_{BE1}$이 `VGND`로 명명 단락됨. |
| **1.3** | **소자 중심 오프셋 실측치 확인** | 마커(`error_p`) 제외 실확산 기준 중심 산출 | **사고 사례**: 행 B 중심을 `error_p` 마커 포함 bbox로 계산해 배선하여 13개 FET 전체가 G-S 단락됨. |
| **1.4** | **`nf ≥ 2` 소자의 메탈1/li 배선 가용성 검증** | 핑거 간격 vs `via1` 최소폭(0.26) 대조 | **사고 사례**: `nf=22` `G5UXWG` 셀 배선 시 핑거 간격(0.025)이 `met1.2`(0.14) 미달로 결선 불가 판명. |
| **1.5** | **백업 파일 저장** | `save bgr_mos` + `writeall force` | **사고 사례**: `getcell` 자식 셀 미저장 상태로 종료하여 파라미터 변경 사항이 유실됨. |

---

## 2. ✏️ 편집 후 (After Editing Checklist)

| # | 체크 항목 | 검증 방법 & 명령 | 실제 사고 사례 (1줄) |
| ---: | :--- | :--- | :--- |
| **2.1** | **Contact 지운 구역 금속 재도포** | `erase via2` 후 `paint metal2`, `paint metal3` | **사고 사례**: `erase via2` 지운 자리에 메탈이 함께 파여 DRC 슬리버 에러 20건이 폭발함. |
| **2.2** | **동일 넷 미세 간격(`met1.2`) 점검** | 0.02~0.08m 간격을 0으로 붙이거나 0.14m 이상 뗌 | **사고 사례**: 동일 넷 간격이 0.05m로 애매하게 떨어져 `met1.2`(0.14) 위반 지속 발생. |
| **2.3** | **광폭 메탈(`width > 3µm`) 옆 이격 점검** | `met1.3b` 규격에 따라 무관 met1과 0.28m 확보 | **사고 사례**: 더미 tie를 통짜 met1(높이 10.88m)로 덮어 이웃 riser와 0.12m 이격 위반 발생. |
| **2.4** | **`feedback` 흰 해칭 잔상 제거** | `feedback clear` 실행 | **사고 사례**: DRC 잔상 흰 해칭이 마스크/선택 박스로 잡히지 않아 레이아웃 미배선으로 오인함. |
| **2.5** | **`space` 층 유령 라벨 검사** | `rlabel space` 검색 후 `erase labels` | **사고 사례**: 도형 없는 자리에 붙은 유령 라벨이 진짜 노드를 `_uq0`로 밀어내어 노드 분리 발생. |

---

## 3. 🛡️ LVS 전 (Before LVS Checklist)

| # | 체크 항목 | 검증 방법 & 명령 | 실제 사고 사례 (1줄) |
| ---: | :--- | :--- | :--- |
| **3.1** | **`_uq` (Unquoted/Unconnected) 노드 0건 확인** | 추출 SPICE에서 `_uq` 검색 | **사고 사례**: `VBE1_uq0` 발생으로 $V_{BE1}$ 노드 단절 상태를 간과하고 LVS 진행하여 넷 불일치. |
| **3.2** | **4포트 전체(D, S, G, B) 인스턴스 검사** | `python3 -c "print(t[1], t[2], t[3], t[4])"` | **사고 사례**: D, S 단자만 대조하다 G 단자 단락/미결선(`cn_mir` D 누락)을 발견하지 못함. |
| **3.3** | **넷 카운트 기준값 일치 확인** | 추출 넷리스트 단자 카운트 대조 | **사고 사례**: `net9` 가로 met3가 세로 met3를 관통하여 $V_{bias}$ 카운트가 167개로 튀어 흡수됨. |
| **3.4** | **Netgen LVS 배치 실행** | `netgen -batch lvs "bgr_mos.spice bgr_mos" ...` | **사고 사례**: SPICE 연속행(`\n+`) 미병합 상태로 파싱하여 LVS 넷 대조 오진 발생. |
| **3.5** | **Property Error 0건 확인** | `lvs_bgr.out`에서 `Property errors` 0건 검증 | **사고 사례**: N=2 더미 저항 굴곡 증분(+1.26m) 누락으로 $L=31.49$ vs $30.23$ Property mismatch 발생. |
