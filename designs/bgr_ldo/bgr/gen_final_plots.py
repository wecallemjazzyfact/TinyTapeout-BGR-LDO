import re
base = open('bgr_core_tb.spice').read()
def make(f, lib, csv):
    s = base.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
    ctrl = '.control\nrun\nwrdata %s v(vref_low)\necho DONE_%s\n.endc' % (csv, csv)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open(f,'w').write(s)
make('run_f_tt.spice','tt','f_tt.csv')
make('run_f_ss.spice','ss','f_ss.csv')
make('run_f_ff.spice','ff','f_ff.csv')
print('GEN_OK')
