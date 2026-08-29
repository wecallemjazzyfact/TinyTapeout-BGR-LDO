#!/usr/bin/env python3
import re, glob

files = sorted(glob.glob("/foss/designs/designs/bgr_ldo/ldo/sw6/o*.txt"))
rows = []
for f in files:
    txt = open(f).read()
    m_code = re.search(r'code=(\d+)', txt)
    m_vddc = re.search(r'v\(vddc\)\s*=\s*([0-9.eE+-]+)', txt)
    m_vref = re.search(r'v\(vref_low\)\s*=\s*([0-9.eE+-]+)', txt)
    if m_code and m_vddc and m_vref:
        rows.append((int(m_code.group(1)), float(m_vddc.group(1)), float(m_vref.group(1))))

rows.sort(key=lambda x: x[0])
print(f"수집 완료: {len(rows)} / 64")

codes = [r[0] for r in rows]
vddcs = [r[1] for r in rows]
vrefs = [r[2] for r in rows]

is_mono_vddc = all(vddcs[i] > vddcs[i+1] for i in range(len(vddcs)-1))
is_mono_vref = all(vrefs[i] > vrefs[i+1] for i in range(len(vrefs)-1))

print(f"VDDC 단조 감소: {'PASS (완벽 단조)' if is_mono_vddc else 'FAIL'}")
print(f"VREF 단조 감소: {'PASS (완벽 단조)' if is_mono_vref else 'FAIL'}")

span_vddc = (vddcs[0] - vddcs[-1]) * 1000
span_vref = (vrefs[0] - vrefs[-1]) * 1000

print(f"code 00: VDDC = {vddcs[0]:.6f} V, VREF = {vrefs[0]:.6f} V")
print(f"code 63: VDDC = {vddcs[-1]:.6f} V, VREF = {vrefs[-1]:.6f} V")
print(f"전체 스팬: VDDC = {span_vddc:.3f} mV (±{span_vddc/2:.2f} mV), VREF = {span_vref:.3f} mV")

v_mid_vddc = (vddcs[31] + vddcs[32]) / 2
v_mid_vref = (vrefs[31] + vrefs[32]) / 2
print(f"중앙(code 31~32): VDDC = {v_mid_vddc:.6f} V (code 31: {vddcs[31]:.6f} V, code 32: {vddcs[32]:.6f} V)")
print(f"중앙(code 31~32): VREF = {v_mid_vref:.6f} V (code 31: {vrefs[31]:.6f} V, code 32: {vrefs[32]:.6f} V)")

lsb_vddc = [(vddcs[i] - vddcs[i+1]) * 1000 for i in range(len(vddcs)-1)]
avg_lsb = sum(lsb_vddc) / len(lsb_vddc)
max_lsb = max(lsb_vddc)
min_lsb = min(lsb_vddc)
max_idx = lsb_vddc.index(max_lsb)
min_idx = lsb_vddc.index(min_lsb)

print(f"VDDC LSB 통계: 평균 = {avg_lsb:.3f} mV | 최소 = {min_lsb:.3f} mV (code {min_idx}->{min_idx+1}) | 최대 = {max_lsb:.3f} mV (code {max_idx}->{max_idx+1})")

near_1p8 = sorted(rows, key=lambda x: abs(x[1] - 1.800))[:5]
print("1.800V 최인접 코드 TOP 5:")
for c, vdc, vrf in near_1p8:
    print(f"  code {c:02d}: VDDC = {vdc:.6f} V (오차 {(vdc-1.8)*1000:+.3f} mV), VREF = {vrf:.6f} V")
