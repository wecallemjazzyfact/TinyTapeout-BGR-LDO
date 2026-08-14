#!/usr/bin/env python3
"""PEX 넷리스트에 개루프 AC 프로브 삽입.
EA 입력쌍 XM1(게이트 FB_TAP, pfet_g5v0d10v5) 24개의 게이트를
FB_TAP_PRB 로 옮기고 Vprb 로 원래 노드와 이어 루프를 끊는다.
"""
import re, sys
SRC="ldo_top_pex_rc_safe.spice"
DST="ldo_top_pex_ac.spice"
lines=open(SRC).read().splitlines(keepends=True)
out=list(lines); n=0
for i,l in enumerate(lines):
    if not re.match(r"^X\d",l): continue
    f=l.split()
    if len(f)<5: continue
    if f[2]=="FB_TAP" and "pfet_g5v0d10v5" in l:
        f[2]="FB_TAP_PRB"; out[i]=" ".join(f)+"\n"; n+=1
print("EA XM1 게이트 치환:",n,"개 (기대 24)")
if n!=24:
    print("!! 개수 불일치 - 중단"); sys.exit(1)
for i in range(len(out)-1,-1,-1):
    if out[i].strip().lower().startswith(".ends"):
        out.insert(i,"Vprb FB_TAP_PRB FB_TAP 0\n"); break
open(DST,"w").writelines(out)
print("wrote",DST)
