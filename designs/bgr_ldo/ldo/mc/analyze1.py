#!/usr/bin/env python3
"""MC 1단계 분석: ui 0/6/15 -> 최적 ui 추정

조건 (산출물 기록용):
  넷리스트 ldo_top_pex_rc_safe.spice (PEX R+C, no coupling, cthresh 0.01, rthresh 1)
  코너 tt_mm (MC_MM_SWITCH=1 / MC_PR_SWITCH=0)
  온도 .options TEMP=27 TNOM=27
  입력 SNK_EN=1.8 RO_EN=0 VAPWR=3.3 VDPWR=1.8
  code = 내부 TRIM 비트값,  ui_in = 15 - code
  seed base 10000 + chunk*1000, setseed + reset 루프 (재현성 검증됨)
"""
import glob, re, statistics as st

S = {}
for f in sorted(glob.glob("out_*.txt")):
    for l in open(f):
        m = re.match(r"^DATA\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", l)
        if m:
            k, i, ui, vd, vr = m.groups()
            S.setdefault((int(k), int(i)), {})[int(ui)] = (float(vd), float(vr))

full = {k: v for k, v in S.items() if len(v) == 3}
print("샘플 %d (완전 %d)" % (len(S), len(full)))
if not full:
    raise SystemExit("데이터 없음")

# 트림 전 (ui=6) 통계
v6 = [v[6][0] for v in full.values()]
r6 = [v[6][1] for v in full.values()]
print()
print("=== 트림 전 (ui=6, code 9) ===")
print("  VDDC     mean %.6f  sigma %.6f  (%.3f %%)" % (st.mean(v6), st.pstdev(v6), st.pstdev(v6)/st.mean(v6)*100))
print("  VREF_LOW mean %.6f  sigma %.6f  (%.3f %%)" % (st.mean(r6), st.pstdev(r6), st.pstdev(r6)/st.mean(r6)*100))
print("  BGR pre-layout MM-only 기준선 2.11 %")

# 최적 ui 추정 (0-6-15 조각별 선형)
def best_ui(d):
    p = [(0, d[0][0]), (6, d[6][0]), (15, d[15][0])]
    lo, hi = (p[0], p[1]) if d[6][0] >= 1.8 else (p[1], p[2])
    if hi[1] == lo[1]:
        return lo[0], lo[1]
    u = lo[0] + (hi[0]-lo[0]) * (1.8-lo[1]) / (hi[1]-lo[1])
    ur = max(0, min(15, round(u)))
    return ur, lo[1] + (hi[1]-lo[1]) * (ur-lo[0]) / (hi[0]-lo[0])

est = {k: best_ui(v) for k, v in full.items()}
uis = [e[0] for e in est.values()]
print()
print("=== 최적 ui 분포 (추정) ===")
for u in range(16):
    n = uis.count(u)
    if n: print("  ui %2d (code %2d) : %3d  %s" % (u, 15-u, n, "#"*min(n, 50)))
out = sum(1 for k, v in full.items() if v[0][0] > 1.8 or v[15][0] < 1.8)
print("  창 이탈 (1.8 이 [ui0, ui15] 밖): %d / %d = %.2f %%" % (out, len(full), out/len(full)*100))

# 2단계 입력 파일
with open("stage2_list.txt", "w") as fp:
    for (k, i), (u, _) in sorted(est.items()):
        fp.write("%d %d %d\n" % (k, i, u))
print()
print("stage2_list.txt 생성 (chunk sample ui)")
