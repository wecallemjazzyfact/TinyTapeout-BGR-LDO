#!/usr/bin/env python3
"""MC 6-bit Stage3 — 전압정렬 LUT(rank) 기준 재트림.

Stage2 의 +17 mV 편향은 MSB 전환(code 31->32)에서 전압이 역전하기 때문.
이진 code 대신 rank(전압 내림차순 순위)로 이동시키면 단조가 보장된다.
"""
import glob, re

D="/foss/designs/designs/bgr_ldo/layout/ldo_top"
NS=50

# LUT: rank -> (code, V)
LUT=[]
for l in open("../lut6.txt"):
    r,c,v=l.split(); LUT.append((int(c),float(v)))
C2R={c:r for r,(c,v) in enumerate(LUT)}
STEP=(LUT[0][1]-LUT[-1][1])/(len(LUT)-1)

# Stage2 결과
T={}
for f in sorted(glob.glob("mc6_o2_*.txt")):
    cur=None
    for l in open(f):
        m=re.match(r"^FINAL\s+(\d+)\s+(\d+)\s+(\d+)",l)
        if m: cur=(int(m.group(1)),int(m.group(2)),int(m.group(3)))
        m=re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)",l)
        if m and cur: T[(cur[0],cur[1])]=(cur[2],float(m.group(1))); cur=None

HDR="""* MC 6-bit stage3  chunk={k}  seed={seed}  N={ns}  LUT(rank) 재트림
* tt_mm / TEMP=27 / SNK_EN=1.8 / RO_EN=0
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt_mm
.include {d}/pex6_safe.spice
.options TEMP=27 TNOM=27
VAPWR VAPWR 0 3.3
VDPWR VDPWR 0 1.8
VTRIM0 TRIM0 0 0
VTRIM1 TRIM1 0 0
VTRIM2 TRIM2 0 0
VTRIM3 TRIM3 0 0
VTRIM4 TRIM4 0 0
VTRIM5 TRIM5 0 0
VSNK_EN SNK_EN 0 1.8
VRO_EN  RO_EN  0 0
x1 VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN 0 VDPWR DIV_OUT RO_EN TRIM0 TRIM5 ldo_top_flat
.control
setseed {seed}
"""

nch=max(k for k,_ in T)+1
moves=[]
for k in range(nch):
    seed=10000+k*1000; body=[]
    for i in range(NS):
        e=T.get((k,i))
        if e is None: code=28
        else:
            c0,v=e
            r0=C2R.get(c0, 28)
            r1=max(0,min(len(LUT)-1, r0+round((v-1.800)/STEP)))
            code=LUT[r1][0]; moves.append(r1-r0)
        vt=63-code
        b=[("1.8" if (vt>>j)&1 else "0") for j in range(6)]
        body.append("reset\n"+"\n".join("alter VTRIM%d = %s"%(j,b[j]) for j in range(6))
                    +"\nop\necho FINAL %d %d %d\nprint v(VDDC) v(VREF_LOW)"%(k,i,code))
    open("mc6_s3_%d.sp"%k,"w").write(HDR.format(k=k,seed=seed,ns=NS,d=D)+"\n".join(body)+"\n.endc\n.end\n")
    print("mc6_s3_%d.sp"%k)
import collections
print()
print("LUT step mean %.3f mV, 엔트리 %d"%(STEP*1e3,len(LUT)))
print("rank 이동 분포:", dict(sorted(collections.Counter(moves).items())))
