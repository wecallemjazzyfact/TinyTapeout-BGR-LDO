import re
base = open('bgr_core_tb.spice').read()
def mk(name, lib, dc, ctrl):
    s = base.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
    s = re.sub(r'^\.dc .*$', dc, s, flags=re.M)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open(name,'w').write(s)
# TC 3코너
for c in ['tt','ss','ff']:
    mk('run_f_tc_%s.spice'%c, c, '.dc temp -40 125 1',
       '.control\nrun\nwrdata f_tc_%s.csv v(vref_low)\necho DONE_TC_%s\n.endc'%(c,c))
# line reg
mk('run_f_lr.spice','tt','.dc VSource 2.7 3.6 0.02',
   '.control\nrun\nwrdata f_lr.csv v(vref_low) (v(vbe1)-v(net1)) v(v_casc_n)\necho DONE_LR\n.endc')
# power (tt)
mk('run_f_pwr.spice','tt','.dc temp -40 125 5',
   '.control\nrun\nwrdata f_pwr.csv -i(vsource)\necho DONE_PWR\n.endc')
# staircase tt / ss-40
for c,tmp,tag in [('tt',None,'tt'),('ss',-40,'ss40')]:
    t = 'set temp=%d\n'%tmp if tmp else ''
    s = base.replace('sky130.lib.spice tt','sky130.lib.spice '+c)
    s = s.replace('VSource VAPWR 0 3.3','VSource VAPWR 0 PWL(0 0 1u 0 3u 1.5 23u 1.5 28u 3.3 35u 3.3)')
    s = re.sub(r'^\.dc .*$','* dc off', s, flags=re.M)
    ctrl = '.control\n%stran 50n 35u\nmeas tran vref_final find v(vref_low) at=34u\nwrdata f_stair_%s.csv v(vapwr) v(vref_low) v(vbe1) v(sense_out) v(v_bias_n) v(v_gate_top)\necho DONE_ST_%s\n.endc'%(t,tag,tag)
    s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
    open('run_f_st_%s.spice'%tag,'w').write(s)
print('GEN_OK')
