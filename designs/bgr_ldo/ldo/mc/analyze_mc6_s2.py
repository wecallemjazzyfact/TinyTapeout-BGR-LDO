#!/usr/bin/env python3
import glob, re, statistics as st

SPEC_MV = 36.0
D = {}

files = sorted(glob.glob("/foss/designs/designs/bgr_ldo/ldo/mc/mc6_o2_*.txt"))
for f in files:
    current_key = None
    for l in open(f, errors="ignore"):
        m = re.match(r"^FINAL\s+(\d+)\s+(\d+)\s+(\d+)", l.strip())
        if m:
            k, i, code = map(int, m.groups())
            current_key = (k, i)
            D[current_key] = {"code": code}
        m2 = re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)", l.strip())
        if m2 and current_key in D:
            D[current_key]["vddc"] = float(m2.group(1))
        m3 = re.match(r"^v\(vref_low\)\s*=\s*([\d.eE+-]+)", l.strip())
        if m3 and current_key in D:
            D[current_key]["vref"] = float(m3.group(1))

full = {k: v for k, v in D.items() if "vddc" in v}
print("=" * 60)
print(f"MC 6-bit Stage 2 최종 분석 결과   N = {len(full)} / 300 (수렴률 {len(full)/300*100:.1f}%)")
print("=" * 60)

vd = [v["vddc"] for v in full.values()]
vr = [v["vref"] for v in full.values()]
dv = [(x - 1.8) * 1000 for x in vd]
codes = [v["code"] for v in full.values()]

mean_dv = st.mean(dv)
sd_dv = st.pstdev(dv)
mean_vd = st.mean(vd)
mean_vr = st.mean(vr)
sd_vr = st.pstdev(vr)

print()
print("★ [트림 후 VDDC 통계 (1.800V 기준)]")
print(f"  평균 전압 (Mean)  : {mean_vd:.6f} V  (오차: {mean_dv:+.3f} mV)")
print(f"  표준편차 (sigma) : {sd_dv:8.3f} mV  ({sd_dv/1800*100:.3f}% of 1.8V)")
print(f"  3-sigma         : {3*sd_dv:8.3f} mV  (LDO 허용 규격 ±{SPEC_MV:.1f} mV)")
print(f"  최소 / 최대     : {min(dv):+.3f} mV ({min(vd):.6f} V) / {max(dv):+.3f} mV ({max(vd):.6f} V)")

viol = [x for x in dv if abs(x) > SPEC_MV]
print()
print(f"★ [스펙(±{SPEC_MV:.0f} mV) 판정 및 수율]")
print(f"  스펙 이탈 샘플 수 : {len(viol)} / {len(full)} = {len(viol)/max(1,len(full))*100:.2f}%")
print(f"  수율 (Yield)     : {(1 - len(viol)/max(1,len(full)))*100:.2f}%")
if viol:
    print("  이탈 샘플 값(mV) :", [f"{x:.1f}" for x in sorted(viol)])
else:
    print("  >> 전 표본 100% 스펙 안착 (이탈 0건)!")

print()
print("★ [VREF_LOW 통계]")
print(f"  평균 (Mean) : {mean_vr:.6f} V")
print(f"  sigma      : {sd_vr*1000:.3f} mV ({sd_vr/mean_vr*100:.3f}%)")

print()
print("★ [선택된 트림 코드 분포]")
for c in sorted(set(codes)):
    cnt = codes.count(c)
    bar = "#" * (cnt // 2)
    print(f"  code {c:02d} : {cnt:3d}개 ({cnt/len(codes)*100:4.1f}%) {bar}")

print()
print("★ [최종 판정]")
if 3 * sd_dv <= SPEC_MV and len(viol) == 0:
    print(f"  >> PASS (3-sigma {3*sd_dv:.2f} mV <= {SPEC_MV:.1f} mV, 수율 100%)")
else:
    print("  >> 확인 필요")
