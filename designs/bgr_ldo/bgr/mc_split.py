import re, subprocess
import statistics as st
src=open('bgr_core_tb2.spice').read()
L=((115696.7/2)-525.70)/470.976
src=re.sub(r'XR6 VGND VBE1 VGND sky130_fd_pr__res_high_po_0p69 L=[0-9.]+ mult=1',
 'XR6a VGND n_r6m VGND sky130_fd_pr__res_high_po_0p69 L=%.4f\nXR6b n_r6m VBE1 VGND sky130_fd_pr__res_high_po_0p69 L=%.4f'%(L,L), src)
src=re.sub(r'XR7 VGND net1 VGND sky130_fd_pr__res_high_po_0p69 L=[0-9.]+ mult=1',
 'XR7a VGND n_r7m VGND sky130_fd_pr__res_high_po_0p69 L=%.4f\nXR7b n_r7m net1 VGND sky130_fd_pr__res_high_po_0p69 L=%.4f'%(L,L), src)
src=re.sub(r'(res_high_po_0p69 L=[0-9.]+) mult=1', r'\1', src)
src=src.replace('.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt',
  '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt\n.param MC_MM_SWITCH=1\n.param MC_PR_SWITCH=1')
src=re.sub(r'^\.save .*$','* save off', src, flags=re.M)
src=re.sub(r'^\.dc .*$','* dc off', src, flags=re.M)
for i,v in [(0,1.8),(1,1.8),(2,1.8),(3,0.0)]:
    src=re.sub(r'(Vtrim%d net%d 0 )[0-9.]+'%(i,i+1), r'\g<1>%.1f'%v, src)
vs=[]
for i in range(1,101):
    s=re.sub(r'\.control.*?\.endc','.control\nset rndseed=%d\nop\nprint v(vref_low)\n.endc'%(i*7919), src, flags=re.S)
    open('mcs_tmp.spice','w').write(s)
    o=subprocess.run(['ngspice','-b','mcs_tmp.spice'],capture_output=True,text=True).stdout
    m=re.search(r'v\(vref_low\)\s*=\s*([0-9.eE+-]+)',o)
    if m: vs.append(float(m.group(1)))
    if i%25==0: print('  %d/100'%i, flush=True)
mu,sd=st.mean(vs),st.stdev(vs)
print('R6/R7 2분할 MC: mean=%.5f sigma=%.5f (%.2f%%) 3sig=+-%.2f%%'%(mu,sd,sd/mu*100,3*sd/mu*100))
print('참조: 분할전 2.38%% / pooled 설계기준 2.22%%')
