import re
for tag, src in [('before','bgr_before.spice'), ('after','bgr_core_tb.spice')]:
    base = open(src).read()
    def mk(name, lib, dc, ctrl):
        s = base.replace('sky130.lib.spice tt', 'sky130.lib.spice '+lib)
        s = re.sub(r'^\.dc .*$', dc, s, flags=re.M)
        s = re.sub(r'\.control.*?\.endc', ctrl, s, flags=re.S)
        open(name,'w').write(s)
    for c in ['tt','ss','ff']:
        mk('r_%s_tc_%s.spice'%(tag,c), c, '.dc temp -40 125 1',
           '.control\nrun\nwrdata %s_tc_%s.csv v(vref_low)\necho DONE_%s_TC_%s\n.endc'%(tag,c,tag,c))
    mk('r_%s_lr.spice'%tag, 'tt', '.dc VSource 2.7 3.6 0.02',
       '.control\nrun\nwrdata %s_lr.csv v(vref_low) (v(vbe1)-v(net1))\necho DONE_%s_LR\n.endc'%(tag,tag))
    mk('r_%s_op.spice'%tag, 'tt', '* dc off',
       '.control\nop\necho ===== OP_%s =====\nprint v(vref_low) (v(vbe1)-v(net1))\nprint -i(vsource)\n.endc'%tag)
print('GEN_OK')
