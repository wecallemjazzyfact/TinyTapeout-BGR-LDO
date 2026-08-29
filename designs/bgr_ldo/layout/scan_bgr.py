#!/usr/bin/env python3
import sys
MAG="/foss/designs/designs/bgr_ldo/layout/bgr_core/bgr_mos.mag"
def scan(x0,x1,y0,y1,layers=None):
    L=open(MAG).read().splitlines(); S=200.0
    for l in L:
        if l.startswith("magscale"):
            t=l.split(); S=100.0*float(t[2])/float(t[1]); break
    lay=None; rects=[]; cells=[]; i=0
    while i<len(L):
        l=L[i]
        if l.startswith("<< "): lay=l.strip()[3:-3]
        elif l.startswith("use "):
            t=[int(v) for v in L[i+2].split()[1:]]
            b=[int(v) for v in L[i+3].split()[1:]]
            xa=[(bx*t[0]+by*t[1]+t[2])/S for bx,by in ((b[0],b[1]),(b[2],b[3]))]
            ya=[(bx*t[3]+by*t[4]+t[5])/S for bx,by in ((b[0],b[1]),(b[2],b[3]))]
            if min(xa)<x1 and max(xa)>x0 and min(ya)<y1 and max(ya)>y0:
                cells.append((l.split()[1],min(xa),max(xa),min(ya),max(ya)))
            lay=None; i+=4; continue
        elif l.startswith("rect ") and lay:
            if layers is None or lay in layers:
                v=[int(x)/S for x in l.split()[1:5]]
                if v[0]<x1 and v[2]>x0 and v[1]<y1 and v[3]>y0: rects.append((lay,v))
        i+=1
    return rects,cells
x0,x1,y0,y1=map(float,sys.argv[1:5])
lay=sys.argv[5].split(",") if len(sys.argv)>5 else None
r,c=scan(x0,x1,y0,y1,lay)
print("=== bgr_mos  x %.1f..%.1f  y %.1f..%.1f ==="%(x0,x1,y0,y1))
print("--- 도형 %d ---"%len(r))
for l,v in sorted(r,key=lambda z:(z[0],z[1][1]))[:40]:
    print("  %-14s x %8.3f..%8.3f y %8.3f..%8.3f"%(l,v[0],v[2],v[1],v[3]))
if len(r)>40: print("  ...")
print("--- 셀 %d ---"%len(c))
for n,a,b,cc,d in c[:20]:
    print("  %-44s x %8.3f..%8.3f y %8.3f..%8.3f"%(n[:44],a,b,cc,d))
if len(c)>20: print("  ...")
