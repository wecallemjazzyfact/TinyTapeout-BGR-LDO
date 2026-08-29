#!/usr/bin/env python3
import collections
D="/foss/designs/designs/bgr_ldo/layout/ldo_top"
NS=50
lst=collections.defaultdict(dict)
for line in open("stage2_list.txt"):
    k,i,u=map(int,line.split()); lst[k][i]=u
for k in sorted(lst):
    seed=10000+k*1000
    header="""* MC stage2  chunk=%d  seed=%d  N=%d  추정 ui 에서 실측 (전개형)
* tt_mm / TEMP=27 / SNK_EN=1.8 / RO_EN=0 / code = 15 - ui_in
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt_mm
.include %s/ldo_top_pex_rc_safe.spice
.options TEMP=27 TNOM=27
VAPWR VAPWR 0 3.3
VDPWR VDPWR 0 1.8
VTRIM0 TRIM0 0 0
VTRIM1 TRIM1 0 1.8
VTRIM2 TRIM2 0 1.8
VTRIM3 TRIM3 0 0
VSNK_EN SNK_EN 0 1.8
VRO_EN  RO_EN  0 0
x1 VAPWR TRIM0 VREF_LOW TRIM1 TRIM2 VDDC TRIM3 SNK_EN 0 VDPWR DIV_OUT RO_EN ldo_top_flat
.control
setseed %d
"""%(k,seed,NS,D,seed)
    body=[]
    for i in range(NS):
        u=lst[k].get(i,6)
        v0="1.8" if u&1 else "0"
        v1="1.8" if (u>>1)&1 else "0"
        v2="1.8" if (u>>2)&1 else "0"
        v3="1.8" if (u>>3)&1 else "0"
        body.append("""reset
alter VTRIM0 = %s
alter VTRIM1 = %s
alter VTRIM2 = %s
alter VTRIM3 = %s
op
echo FINAL %d %d %d %s %s %s %s
print v(VDDC) v(VREF_LOW)"""%(v0,v1,v2,v3,k,i,u,v3,v2,v1,v0))
    with open("run2_%d.sp"%k,"w") as f:
        f.write(header+"\n".join(body)+"\n.endc\n.end\n")
    print("run2_%d.sp  (%d samples)"%(k,len(body)))
