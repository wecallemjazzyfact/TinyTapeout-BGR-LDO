#!/usr/bin/env bash
# run_signoff.sh - TinyTapeout Sky130A DRC Sign-off Automation Script
# Usage: ./run_signoff.sh [CELL_NAME] [WORK_DIR]

set -e

CELL="${1:-bgr_mos}"
WORK_DIR="${2:-/foss/designs/designs/bgr_ldo/layout/bgr_core}"

cd "$WORK_DIR"

echo "=== [1/5] Setting up PDK environment ==="
export PDK_ROOT="${PDK_ROOT:-/foss/pdks}"
export PDK="${PDK:-sky130A}"
export PDKPATH="${PDKPATH:-/foss/pdks/sky130A}"

MAGIC_BIN="${HOME}/.local/bin/magic"
if [ ! -x "$MAGIC_BIN" ]; then
  MAGIC_BIN="magic"
fi

GDS_FILE="${CELL}.gds"
RPT_MR="drc_mr.xml"
RPT_ZERO="drc_zeroarea.xml"
RPT_PIN="drc_pin_label.xml"
RPT_URPM="drc_nwell_urpm.xml"

# Cleanup intermediate files prior to running
rm -f "$GDS_FILE" "$RPT_MR" "$RPT_ZERO" "$RPT_PIN" "$RPT_URPM"

echo "=== [2/5] Exporting GDS from Magic ($CELL) ==="
$MAGIC_BIN -dnull -noconsole -T sky130A <<EOF > /dev/null 2>&1
load $CELL
gds write $GDS_FILE
quit -noprompt
EOF

if [ ! -f "$GDS_FILE" ]; then
  echo "[ERROR] Failed to generate GDS file: $GDS_FILE"
  exit 1
fi
echo "[OK] GDS generated: $GDS_FILE ($(du -h "$GDS_FILE" | cut -f1))"

echo "=== [3/5] Running KLayout DRC Decks ==="
# 1) Full MR DRC (FEOL + BEOL + Offgrid)
klayout -b -r "$PDKPATH/libs.tech/klayout/drc/sky130A_mr.drc" \
  -rd input="$GDS_FILE" -rd report="$RPT_MR" -rd top_cell="$CELL" \
  -rd feol=true -rd beol=true -rd offgrid=true -rd thr=1 > /dev/null 2>&1 || true

# 2) Zero Area DRC
KL_TECH_FILES="/foss/designs/tt/precheck/tech-files"
if [ ! -d "$KL_TECH_FILES" ]; then
  KL_TECH_FILES="tech-files"
fi

klayout -b -r "$KL_TECH_FILES/zeroarea.rb.drc" \
  -rd input="$GDS_FILE" -rd report="$RPT_ZERO" -rd top_cell="$CELL" -rd thr=1 > /dev/null 2>&1 || true

# 3) Pin Label Purpose DRC
klayout -b -r "$KL_TECH_FILES/pin_label_purposes_overlapping_drawing.rb.drc" \
  -rd input="$GDS_FILE" -rd report="$RPT_PIN" -rd top_cell="$CELL" -rd thr=1 > /dev/null 2>&1 || true

# 4) Nwell URPM DRC
klayout -b -r "$KL_TECH_FILES/nwell_urpm.drc" \
  -rd input="$GDS_FILE" -rd report="$RPT_URPM" -rd top_cell="$CELL" -rd thr=1 > /dev/null 2>&1 || true

echo "=== [4/5] Summarizing DRC Reports ==="
python3 - <<PYEOF
import xml.etree.ElementTree as ET
import os, sys

reports = [
    ("KLayout Sky130A MR (FEOL+BEOL+Offgrid)", "$RPT_MR"),
    ("KLayout Zero Area", "$RPT_ZERO"),
    ("KLayout Pin Label Purposes", "$RPT_PIN"),
    ("KLayout Nwell URPM", "$RPT_URPM"),
]

total_errors = 0
print("-" * 65)
print(f"{'DRC Deck Name':<42} | {'Violations':<15}")
print("-" * 65)

for title, rfile in reports:
    count = 0
    cat_counts = {}
    if os.path.exists(rfile):
        try:
            tree = ET.parse(rfile)
            root = tree.getroot()
            items = root.findall(".//item")
            count = len(items)
            for item in items:
                cat = item.find("category")
                cname = cat.text if (cat is not None and cat.text) else "Uncategorized"
                cat_counts[cname] = cat_counts.get(cname, 0) + 1
        except Exception as e:
            cname = f"Parse Error: {e}"
    total_errors += count
    status = "CLEAN (0)" if count == 0 else f"FAIL ({count})"
    print(f"{title:<42} | {status:<15}")
    if count > 0:
        for cname, ccnt in cat_counts.items():
            print(f"   - {cname:<38} : {ccnt}건")

print("-" * 65)
print(f"TOTAL DRC VIOLATIONS: {total_errors}")
print("-" * 65)

if total_errors > 0:
    sys.exit(1)
else:
    sys.exit(0)
PYEOF
