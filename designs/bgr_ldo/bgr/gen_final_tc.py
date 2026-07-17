import re
base = open('bgr_core_tb.spice').read()
for lib in ['tt','ss','ff']:
    s = base.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
    s = re.sub(r'^\.dc .*$', '.dc temp -40 125 1', s, flags=re.M)   # 1도 스텝: 정밀
    ctrl = '.control\nrun\nwrdata final_tc_%s.csv v(vref_low)\necho DONE_%s\n.endc' % (lib,lib)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open('run_ftc_%s.spice'%lib,'w').write(s)
print('GEN_OK')
