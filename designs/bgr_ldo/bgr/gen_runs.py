import re
base = open('bgr_core_tb.spice').read()
STAIR = 'PWL(0 0 1u 0 3u 1.5 23u 1.5 28u 3.3 35u 3.3)'
RAMP5 = 'PWL(0 0 1u 0 6u 3.3 12u 3.3)'
SIGS  = 'v(vapwr) v(vref_low) v(vbe1) v(sense_out) v(v_bias_n) v(v_gate_top)'

def make(fname, vsrc, lib, ctrl, keep_dc=False):
    s = base
    s = re.sub(r'^VSource VAPWR 0 .*$', 'VSource VAPWR 0 '+vsrc, s, flags=re.M)
    s = s.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
    if not keep_dc:
        s = re.sub(r'^\.dc temp.*$', '* dc disabled', s, flags=re.M)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open(fname,'w').write(s)

def tran_ctrl(tstep, tstop, csv, temp=None):
    t = 'set temp=%s\n' % temp if temp is not None else ''
    return '.control\n%stran %s %s\nwrdata %s %s\necho DONE_%s\n.endc' % (t, tstep, tstop, csv, SIGS, csv)

def tc_ctrl(csv):
    return '.control\nrun\nwrdata %s v(vref_low)\necho DONE_%s\n.endc' % (csv, csv)

make('run_w1.spice', STAIR, 'tt', tran_ctrl('50n','35u','w1_tt_stair.csv'))
make('run_w2.spice', STAIR, 'ss', tran_ctrl('50n','35u','w2_ss40_stair.csv', -40))
make('run_w3.spice', RAMP5, 'tt', tran_ctrl('10n','12u','w3_tt_ramp5u.csv'))
make('run_tc_tt.spice','3.3','tt', tc_ctrl('w4_tc_tt.csv'), keep_dc=True)
make('run_tc_ss.spice','3.3','ss', tc_ctrl('w5_tc_ss.csv'), keep_dc=True)
make('run_tc_ff.spice','3.3','ff', tc_ctrl('w6_tc_ff.csv'), keep_dc=True)
print('GEN_OK: 6 run files')
