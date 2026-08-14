import re
base = open('bgr_core_tb.spice').read()
vals = {39:'232.531', 40:'238.534', 41:'244.537', 42:'250.540', 43:'256.543'}
for N,L in vals.items():
    s = base.replace('L=244.537', 'L='+L)
    ctrl = '.control\nrun\nwrdata n%d_tc.csv v(vref_low)\necho DONE_N%d\n.endc' % (N,N)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open('run_n%d.spice'%N,'w').write(s)
print('GEN_OK')
