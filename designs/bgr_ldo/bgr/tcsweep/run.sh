#!/bin/bash
# BGR TC sweep: R1 l 값을 바꿔가며 온도 스윕 -> CSV
# 조건: PEX R+C (bgr_mos_pex_rc_safe.spice), tt, 트림 code7 (TRIM3=0, TRIM2/1/0=1.8)
set -e
PEX=/foss/designs/designs/bgr_ldo/layout/bgr_core/bgr_mos_pex_rc_safe.spice
OUT=/foss/designs/designs/bgr_ldo/bgr/tcsweep
BASE=34.29

for L in "$@"; do
  sed "s/res_high_po_0p69 l=${BASE}\$/res_high_po_0p69 l=${L}/" "$PEX" > "$OUT/pex_${L}.spice"
  n=$(grep -c "res_high_po_0p69 l=${L}\$" "$OUT/pex_${L}.spice")
  if [ "$n" != "1" ]; then echo "L=$L 치환 실패 (n=$n)"; exit 1; fi

  cat > "$OUT/tb_${L}.sp" << EOF
* BGR TC sweep  R1 l=${L}  PEX R+C  tt  trim code7
.include ${OUT}/pex_${L}.spice
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt

VAPWR VAPWR 0 3.3
VIB   IB_EA 0 0.95
VT0   TRIM0 0 1.8
VT1   TRIM1 0 1.8
VT2   TRIM2 0 1.8
VT3   TRIM3 0 0

Xcore VGND VAPWR VREF_LOW TRIM0 TRIM1 TRIM2 TRIM3 IB_EA bgr_mos_flat
VG VGND 0 0

.dc temp -40 125 1
.control
run
wrdata ${OUT}/raw_${L}.dat v(vref_low)
.endc
.end
EOF

  ngspice -b "$OUT/tb_${L}.sp" > "$OUT/log_${L}.txt" 2>&1
  echo -n "L=${L} "
  if [ -s "$OUT/raw_${L}.dat" ]; then
    awk "NR==1{f=\$2} {l=\$2} END{printf \"n=%d  V(-40)=%.6f V(125)=%.6f\\n\", NR, f, l}" "$OUT/raw_${L}.dat"
  else
    echo "실패 - log 확인"; tail -5 "$OUT/log_${L}.txt"
  fi
done
