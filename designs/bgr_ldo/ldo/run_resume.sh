#!/usr/bin/env bash
source /headless/.bashrc 2>/dev/null || true
export PATH="/headless/.local/bin:/foss/tools/bin:/foss/tools/sak:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
cd /foss/designs/designs/bgr_ldo/ldo
for c in $(seq -w 39 63); do
  echo "$c"
done | xargs -P 4 -I{} bash -c 'ngspice -b sw6/s6_tt_c{}.sp > sw6/o{}.txt 2>&1'
echo ALL_DONE > sw6_done.txt
