import re, subprocess, os

base = open('bgr_before.spice').read()
# MC 스위치 켜기 (.lib 뒤에)
base = base.replace(
  '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt',
  '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt\n.param MC_MM_SWITCH=1\n.param MC_PR_SWITCH=1')
base = re.sub(r'^\.dc .*$', '* dc off', base, flags=re.M)

N = 100
results = []
for i in range(1, N+1):
    ctrl = '''.control
set rndseed=%d
op
print v(vref_low)
.endc''' % (i * 7919)          # 소수 곱으로 seed 분산
    s = re.sub(r'\.control.*?\.endc', ctrl, base, flags=re.S)
    open('mc_before_tmp.spice','w').write(s)
    out = subprocess.run(['ngspice','-b','mc_before_tmp.spice'],
                         capture_output=True, text=True).stdout
    m = re.search(r'v\(vref_low\)\s*=\s*([0-9.eE+-]+)', out)
    if m:
        results.append(float(m.group(1)))
    if i % 20 == 0:
        print('  %d/%d done' % (i, N), flush=True)

with open('mc_vref_before.txt','w') as f:
    for v in results:
        f.write('%.6f\n' % v)
print('COLLECTED %d samples' % len(results))
if len(results) > 1:
    import statistics as st
    print('first5:', ['%.5f'%x for x in results[:5]])
    print('mean=%.5f  sigma=%.5f  (%.2f%%)' % (st.mean(results), st.stdev(results),
          st.stdev(results)/st.mean(results)*100))
