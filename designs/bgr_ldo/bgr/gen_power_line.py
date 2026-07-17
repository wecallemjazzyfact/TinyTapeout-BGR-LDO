import re
base = open('bgr_core_tb.spice').read()
# 1) 온도별 전력 (코너 3종)
for lib in ['tt','ss','ff']:
    s = base.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
    s = re.sub(r'^\.dc .*$', '.dc temp -40 125 5', s, flags=re.M)
    ctrl = '.control\nrun\nwrdata pwr_%s.csv -i(vsource) v(vref_low)\necho DONE_PWR_%s\n.endc' % (lib,lib)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open('run_pwr_%s.spice'%lib,'w').write(s)
# 2) VAPWR 스윕 (line regulation) - tt/27C
s = base
s = re.sub(r'^\.dc .*$', '.dc VSource 2.7 3.6 0.01', s, flags=re.M)
ctrl = '.control\nrun\nwrdata line_reg.csv v(vref_low)\necho DONE_LINE\n.endc'
s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
open('run_linereg.spice','w').write(s)
print('GEN_OK')
