#!/bin/bash
# xschem 넷리스트 -> LVS 골든
#  (1) 저항 mult 제거 (netgen 미인식)
#  (2) W/L 에 u 접미사 (netgen 은 없으면 미터로 읽음)
SRC=$1; DST=${2:-${SRC%.spice}_lvs.spice}
D=$(cd "$(dirname "$0")" && pwd)
[ -z "$SRC" ] && { echo "usage: mklvs.sh <in.spice> [out.spice]"; exit 1; }

sed -E "s/(res_high_po_[0-9a-z]+p[0-9]+ L=[0-9.]+) mult=[0-9]+/\1/g" "$SRC" \
  | python3 "$D/_addunit.py" > "$DST"

echo "생성: $DST"
echo -n "  줄수        : "; wc -l < "$DST"
echo -n "  subckt      : "; grep -c "^\.subckt" "$DST"
echo -n "  mult 잔여   : "; grep -c "res_high_po.*mult=" "$DST"
echo -n "  단위없음    : "; grep -cE "[WL]=[0-9.]+( |$)" "$DST"
echo -n "  MF=1 잔여   : "; grep -c "MF=1" "$DST"; echo -n "  MF=1 잔여   : "; grep -c "MF=1" "$DST"; echo -n "  프로브 잔여 : "; grep -cE "^(Vprb|Iprb)" "$DST"
echo    "  nf 종류     : $(grep -oE "nf=[0-9]+" "$DST" | sort -u | tr "\n" " ")"
