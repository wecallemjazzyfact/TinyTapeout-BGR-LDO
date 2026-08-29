#!/usr/bin/env python3
"""MC 2단계 최종 분석: 트림 후 VDDC 통계."""
import glob, re, statistics as st
SPEC_MV = 36.0
D={}
for f in sorted(glob.glob("out2_*.txt")):
    for l in open(f):
        m=re.match(r"^FINAL\s+(\d+)\s+(\d+)\s+(\d+)\s+\S+\s+\S+\s+\S+\s+\S+",l)
        if m:
            k,i,ui=map(int,m.groups()); D[(k,i)]={"ui":ui}
        m2=re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)",l)
        if m2 and D:
            last=list(D)[-1]; D[last]["vddc"]=float(m2.group(1))
full={k:v for k,v in D.items() if "vddc" in v}
print("="*60)
print("MC stage2 최종 결과   N = %d (기대 300)"%len(full))
print("="*60)
vd=[v["vddc"] for v in full.values()]
dv=[(x-1.8)*1000 for x in vd]
uis=[v["ui"] for v in full.values()]
mean=st.mean(dv); sd=st.pstdev(dv)
print()
print("트림 후 VDDC (mV, 1.800V 기준)")
print("  mean   %+8.3f mV"%mean)
print("  sigma   %8.3f mV"%sd)
print("  3sigma  %8.3f mV   (스펙 +-%.1f mV)"%(3*sd,SPEC_MV))
print("  min/max %+.3f / %+.3f mV"%(min(dv),max(dv)))
viol=[x for x in dv if abs(x)>SPEC_MV]
print()
print("스펙(+-%.0f mV) 위반: %d / %d = %.2f %%"%(SPEC_MV,len(viol),len(full),100*len(viol)/max(1,len(full))))
if viol: print("  위반값:",["%.1f"%x for x in sorted(viol)])
print()
print("사용된 ui 분포")
for u in range(16):
    n=uis.count(u)
    if n: print("  ui %2d (code %2d) : %3d  %s"%(u,15-u,n,"#"*n))
print()
print("=== sanity check ===")
print("  BGR pre-layout MM-only sigma(V_ref) 2.11%%  vs  stage1 sigma(V_ref,ui=6) 2.040%%")
print("  트림 후 VDDC sigma %.3f mV = %.3f%% of 1.8V"%(sd,sd/1800*100))
print("  판정: %s"%("PASS (3sigma < spec)" if 3*sd<=SPEC_MV else "FAIL (확인 필요)"))
