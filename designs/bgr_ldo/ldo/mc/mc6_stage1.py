#!/usr/bin/env python3
"""MC 6-bit Stage1 — code 28 고정, N=300 (chunk 6 x 50).

4-bit 절차와 동일:  setseed + reset 루프 (프로세스간 재현성 확보)
code 28  ->  VTRIM = 63-28 = 35 = 100011
  TRIM5=1  TRIM4=0  TRIM3=0  TRIM2=0  TRIM1=1  TRIM0=1
"""
D = "/foss/designs/designs/bgr_ldo/layout/ldo_top"
NS, NCH, CODE = 50, 6, 28

vt = 63 - CODE
bits = [("1.8" if (vt >> i) & 1 else "0") for i in range(6)]

HDR = """* MC 6-bit stage1  chunk={k}  seed={seed}  N={ns}  code={code} 고정
* tt_mm / TEMP=27 / SNK_EN=1.8 / RO_EN=0
* code = 내부 TRIM 비트값,  VTRIM 외부핀 = 63 - code = {vt} ({vtb})
* port: VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN VGND VDPWR DIV_OUT RO_EN TRIM0 TRIM5
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt_mm
.include {d}/pex6_safe.spice
.options TEMP=27 TNOM=27
VAPWR VAPWR 0 3.3
VDPWR VDPWR 0 1.8
VTRIM0 TRIM0 0 {b0}
VTRIM1 TRIM1 0 {b1}
VTRIM2 TRIM2 0 {b2}
VTRIM3 TRIM3 0 {b3}
VTRIM4 TRIM4 0 {b4}
VTRIM5 TRIM5 0 {b5}
VSNK_EN SNK_EN 0 1.8
VRO_EN  RO_EN  0 0
x1 VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN 0 VDPWR DIV_OUT RO_EN TRIM0 TRIM5 ldo_top_flat
.control
setseed {seed}
"""

BODY = """reset
op
echo FINAL {k} {i} {code}
print v(VDDC) v(VREF_LOW)"""

for k in range(NCH):
    seed = 10000 + k * 1000
    h = HDR.format(k=k, seed=seed, ns=NS, code=CODE, vt=vt,
                   vtb=format(vt, "06b"), d=D,
                   **{f"b{i}": bits[i] for i in range(6)})
    b = "\n".join(BODY.format(k=k, i=i, code=CODE) for i in range(NS))
    open(f"mc6_s1_{k}.sp", "w").write(h + b + "\n.endc\n.end\n")
    print(f"mc6_s1_{k}.sp  ({NS} samples, seed {seed})")

print()
print(f"code {CODE}  ->  VTRIM {format(vt,'06b')}  (TRIM5..TRIM0)")
print(f"  TRIM0={bits[0]}  TRIM1={bits[1]}  TRIM2={bits[2]}")
print(f"  TRIM3={bits[3]}  TRIM4={bits[4]}  TRIM5={bits[5]}")
