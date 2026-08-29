#!/usr/bin/env python3
"""6-bit 트림 스윕 덱 생성 (64코드).

포트 순서 (PEX 실측, 2026-08-28):
  VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN VGND VDPWR DIV_OUT RO_EN TRIM0 TRIM5

트림 극성:
  code = 내부 TRIM 비트값 (BGR 정의)
  VTRIM 전압원 = 외부 핀 (인버터 앞단)
  VTRIM 비트 = 1 - (code 비트)   즉 VTRIM 패턴 = 63 - code
  code 0  = V 최대,  code 63 = V 최소

사용:  python3 gen_sweep6.py <corner> <temp> <outdir>
"""
import os, sys

corner = sys.argv[1] if len(sys.argv) > 1 else "tt"
temp   = sys.argv[2] if len(sys.argv) > 2 else "27"
outdir = sys.argv[3] if len(sys.argv) > 3 else "."

PEX = "/foss/designs/designs/bgr_ldo/layout/ldo_top/pex6_safe.spice"
LIB = "/foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice"

TMPL = """* corner={corner} {temp}C  code={code}  (내부 TRIM 비트값)
* VTRIM 외부핀 패턴 = 63 - code = {vt}   (인버터가 반전)
* PEX port order (2026-08-28):
*   VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN VGND VDPWR DIV_OUT RO_EN TRIM0 TRIM5
.lib {lib} {corner}
.include {pex}
.options TEMP={temp} TNOM=27
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
op
print v(VDDC) v(VREF_LOW)
.endc
.end
"""

os.makedirs(outdir, exist_ok=True)
made = []
for code in range(64):
    vt = 63 - code                      # 외부 핀 패턴
    b = [(vt >> i) & 1 for i in range(6)]
    txt = TMPL.format(
        corner=corner, temp=temp, code=code, vt=format(vt, "06b"),
        lib=LIB, pex=PEX,
        **{f"b{i}": ("1.8" if b[i] else "0") for i in range(6)})
    fn = os.path.join(outdir, f"s6_{corner}_c{code:02d}.sp")
    open(fn, "w").write(txt)
    made.append(fn)

print(f"{len(made)}개 생성  ->  {outdir}/s6_{corner}_c00.sp .. c63.sp")
print()
print("검산 (code -> VTRIM 비트, MSB=TRIM5):")
for code in (0, 1, 30, 31, 32, 62, 63):
    vt = 63 - code
    print("  code %2d  ->  VTRIM %s  (%2d)" % (code, format(vt, "06b"), vt))
print()
print("  code  0 = 내부 TRIM 000000 = 저항 최대 = V 최대")
print("  code 63 = 내부 TRIM 111111 = 저항 최소 = V 최소")
