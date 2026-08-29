#!/usr/bin/env python3
"""MC 6-bit Stage2 — Stage1 결과로 샘플별 최적 코드 추정 후 재실행.

code 증가 = V 감소 (LSB 8.7 mV)
  dcode = round((V_stage1 - 1.800) / 8.7mV)
  code_new = 28 + dcode   (0..63 클램프)
"""
import glob, re

D="/foss/designs/designs/bgr_ldo/layout/ldo_top"
NS, LSB, BASE = 50, 8.7e-3, 28

# Stage1 읽기 (chunk, idx 순서 보존)
S={}
for f in sorted(glob.glob("mc6_o1_*.txt")):
    k=int(re.search(r"mc6_o1_(\d+)",f).group(1)); i=0; cur=None
    for l in open(f):
        if l.startswith("FINAL"): cur={}
        m=re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)",l)
        if m and cur is not None: cur["v"]=float(m.group(1))
        m=re.match(r"^v\(vref_low\)",l)
        if m and cur is not None:
            S[(k,i)]=cur["v"]; i+=1; cur=None

HDR="""* MC 6-bit stage2  chunk={k}  seed={seed}  N={ns}  샘플별 추정 코드
* tt_mm / TEMP=27 / SNK_EN=1.8 / RO_EN=0
* code = 내부 TRIM 비트값,  VTRIM 외부핀 = 63 - code
* port: VAPWR TRIM1 VREF_LOW TRIM2 TRIM3 VDDC TRIM4 SNK_EN VGND VDPWR DIV_OUT RO_EN TRIM0 TRIM5
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

nch=max(k for k,_ in S)+1
tot=0
for k in range(nch):
    seed=10000+k*1000
    body=[]
    for i in range(NS):
        v=S.get((k,i))
        if v is None: code=BASE
        else: code=max(0,min(63, BASE+round((v-1.800)/LSB)))
        vt=63-code
        b=[("1.8" if (vt>>j)&1 else "0") for j in range(6)]
        body.append("reset\n"+"\n".join("alter VTRIM%d = %s"%(j,b[j]) for j in range(6))
                    +"\nop\necho FINAL %d %d %d\nprint v(VDDC) v(VREF_LOW)"%(k,i,code))
        tot+=1
    open("mc6_s2_%d.sp"%k,"w").write(HDR.format(k=k,seed=seed,ns=NS,d=D)+"\n".join(body)+"\n.endc\n.end\n")
    print("mc6_s2_%d.sp  (%d samples)"%(k,NS))
print()
print("총 %d 샘플, Stage1 %d 건 사용"%(tot,len(S)))
codes=[max(0,min(63,BASE+round((v-1.800)/LSB))) for v in S.values()]
import collections
c=collections.Counter(codes)
print("코드 분포: %d ~ %d"%(min(codes),max(codes)))
for cd in sorted(c): print("  code %2d : %3d"%(cd,c[cd]))
