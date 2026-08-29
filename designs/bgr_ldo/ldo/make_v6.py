#!/usr/bin/env python3
import os, sys, re

PEX = "/foss/designs/designs/bgr_ldo/layout/ldo_top/pex6_safe.spice"
PORT = "x1 VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN 0 VDPWR DIV_OUT RO_EN TRIM0 TRIM5 ldo_top_flat"
TRIM = (
    "VTRIM0 TRIM0 0 1.8\n"
    "VTRIM1 TRIM1 0 1.8\n"
    "VTRIM2 TRIM2 0 0\n"
    "VTRIM3 TRIM3 0 0\n"
    "VTRIM4 TRIM4 0 0\n"
    "VTRIM5 TRIM5 0 1.8"
)

TARGETS = [
    "t1_load",
    "t2_line",
    "t2b_line_slow",
    "t1b_snken",
    "t3_psrr_NL",
    "t3_psrr_IS",
    "t3_psrr_SNK",
    "t4_start",
]

BASE_DIR = "/foss/designs/designs/bgr_ldo/ldo"
OUT_DIR = os.path.join(BASE_DIR, "v6")
os.makedirs(OUT_DIR, exist_ok=True)

print("=== 6-bit 검증 덱 생성 (v6/) ===")
for f in TARGETS:
    src_file = os.path.join(BASE_DIR, f"{f}.sp")
    if not os.path.exists(src_file):
        print(f"  [SKIP] {src_file} 없음")
        continue

    s = open(src_file, encoding="utf-8", errors="ignore").read()
    s = re.sub(r"^\.include .*$", f".include {PEX}", s, flags=re.M)
    s = re.sub(r"(?m)^VTRIM[0-3] .*\n", "", s)
    s = re.sub(r"(?m)^(VSNK_EN)", TRIM + r"\n\1", s, count=1)
    s = re.sub(r"(?m)^x1 .*$", PORT, s)
    s = s.replace("TRIM=0111(code7)", "code28 (6-bit)").replace("TRIM=0111", "code28")
    s = re.sub(r"(simdata/)?" + f + r"\.txt", f"simdata/{f}_6b.txt", s)

    dst_file = os.path.join(OUT_DIR, f"{f}_6b.sp")
    open(dst_file, "w", encoding="utf-8").write(s)
    print(f"  [생성] v6/{f}_6b.sp")

print("\n--- 검증 (t1_load_6b.sp) ---")
test_file = os.path.join(OUT_DIR, "t1_load_6b.sp")
if os.path.exists(test_file):
    for i, line in enumerate(open(test_file)):
        if re.search(r"include|^VTRIM|^x1", line):
            print(f"{i+1:3d}: {line.rstrip()}")
