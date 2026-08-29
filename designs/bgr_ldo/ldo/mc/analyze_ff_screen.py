#!/usr/bin/env python3
import glob, re
D = {}
for f in sorted(glob.glob("ffout_*.txt")):
    for l in open(f):
        m = re.match(r"^SCR\s+(\d+)\s+(\d+)\s+code(\d+)", l)
        if m:
            k, i, c = m.groups()
            D[(int(k), int(i), c)] = {}
        m2 = re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)", l)
        if m2 and D:
            D[list(D)[-1]]["v"] = float(m2.group(1))
c0 = [v["v"] for k, v in D.items() if k[2] == "0" and "v" in v]
c15 = [v["v"] for k, v in D.items() if k[2] == "15" and "v" in v]
print(f"N: code0={len(c0)}  code15={len(c15)}  (target 60/60)")
print()
LOW, HIGH = 1.764, 1.836
low_fail = [v for v in c0 if v < LOW]
high_fail = [v for v in c15 if v > HIGH]
print(f"code0  (V max)  범위 {min(c0):.4f} ~ {max(c0):.4f}   mean {sum(c0)/len(c0):.4f}")
print(f"code15 (V min)  범위 {min(c15):.4f} ~ {max(c15):.4f}   mean {sum(c15)/len(c15):.4f}")
print()
print(f"하단 스펙(<{LOW}) 미달 (하단 포화):  {len(low_fail)}/{len(c0)} = {100*len(low_fail)/len(c0):.1f}%")
if low_fail: print("  값:", sorted(f"{v:.4f}" for v in low_fail))
print(f"상단 스펙(>{HIGH}) 초과 (상단 포화):  {len(high_fail)}/{len(c15)} = {100*len(high_fail)/len(c15):.1f}%")
if high_fail: print("  값:", sorted(f"{v:.4f}" for v in high_fail))
print()
if low_fail or high_fail:
    print("판정: 포화 확인됨 -> B안(상하 1비트씩) 필요")
else:
    print("판정: 스크리닝 N=60 에서 포화 미검출 -> A안도 방어 가능 (단, N 작음 주의)")
