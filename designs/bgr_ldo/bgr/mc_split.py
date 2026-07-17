import re, subprocess, sys, statistics as st
mode = sys.argv[1]; N = int(sys.argv[2])
mm = 1 if mode=='mm' else 0
pr = 1 if mode=='pr' else 0
base = open('bgr_core_tb.spice').read()
base = base.replace(
  '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt',
  '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt\n.param MC_MM_SWITCH=%d\n.param MC_PR_SWITCH=%d' % (mm,pr))
base = re.sub(r'^\.dc .*$', '* dc off', base, flags=re.M)
res=[]
for i in range(1, N+1):
    ctrl = '.control\nset rndseed=%d\nop\nprint v(vref_low)\n.endc' % (i*7919)
    s = re.sub(r'\.control.*?\.endc', ctrl, base, flags=re.S)
    open('mc_%s_tmp.spice'%mode,'w').write(s)
    out = subprocess.run(['ngspice','-b','mc_%s_tmp.spice'%mode], capture_output=True, text=True).stdout
    m = re.search(r'v\(vref_low\)\s*=\s*([0-9.eE+-]+)', out)
    if m: res.append(float(m.group(1)))
    if i%5==0: print('  %s %d/%d'%(mode,i,N), flush=True)
open('mc_%s.txt'%mode,'w').write('\n'.join('%.6f'%v for v in res))
mu, sd = st.mean(res), st.stdev(res)
print('MODE=%s N=%d mean=%.5f sigma=%.5f (%.2f%%)' % (mode, len(res), mu, sd, sd/mu*100))
