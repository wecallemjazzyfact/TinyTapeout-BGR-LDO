# 6-bit 트림 전환 — LDO 세션 정리 (2026-08-27 ~ 08-29)

정본 문서 위치: [`designs/bgr_ldo/docs/05_6BIT_TRIM_LDO_SESSION.md`](file:///c:/Users/aa/Desktop/school/TinyTapeout/designs/bgr_ldo/docs/05_6BIT_TRIM_LDO_SESSION.md)

## 0. 결론 요약
6-bit 트림 전환 완료. **DRC / LVS / PEX / MC 전부 통과.**
- **Monte Carlo**: 4-bit 대비 대폭 개선 ($3\sigma$: $15.22\text{ mV} \rightarrow 10.25\text{ mV}$, 여유 $2.37 \rightarrow 3.51$배, 수율 100%)
- **코너 드리프트**: 27°C 기준 $75.2\text{ mV}$ (전체 스팬 $2042.6\text{ mV}$ 대비 충분)
- **핵심 원칙**: 이진 코드가 아닌 **LUT rank 이동(`ldo/lut6.txt`)**으로 트림 수행

## 1. 핀 배정 및 극성
```text
TRIM0 (LSB, 613 Ω)   = ui_in[7]   x 101.700
TRIM1 = ui_in[0]  x 120.930
TRIM2 = ui_in[1]  x 118.170
TRIM3 = ui_in[2]  x 115.410
TRIM4 = ui_in[3]  x 112.650
TRIM5 (MSB, 18198 Ω) = ui_in[6]   x 104.460
SNK_EN = ui_in[4], RO_EN = ui_in[5]
```
극성: `VTRIM 외부핀 패턴 = 63 - code` (인버터 반전, code 0: 최대 / code 63: 최소)

## 2. 다음 세션 작업
- `ac_tb.sp`, `t1_load.sp`, `t2_line.sp`, `t3_psrr_*.sp`, `t4_start.sp` 포트 14개/VTRIM 6개/`pex6_safe.spice` 수정 및 재실행
- GDS 제출본 갱신 및 Precheck
