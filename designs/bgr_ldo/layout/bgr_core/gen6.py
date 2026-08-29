import os
LIB='.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice %s'
HEAD='''* 6-bit batch
%s
.include bgr_core_pex_rc_wrap.spice
VSource VAPWR 0 %s
Vload IB_EA 0 0.95
Vtrim0 t0 0 %.1f
Vtrim1 t1 0 %.1f
Vtrim2 t2 0 %.1f
Vtrim3 t3 0 %.1f
Vtrim4 t4 0 %.1f
Vtrim5 t5 0 %.1f
x1 VAPWR VREF_LOW IB_EA t0 t1 t2 t3 t4 t5 0 bgr_core
'''
def deck(corner,code,vsrc,ctrl):
    b=[1.8*((code>>i)&1) for i in range(6)]
    return HEAD%(LIB%corner,vsrc,b[0],b[1],b[2],b[3],b[4],b[5])+ctrl+'\n.end\n'
os.makedirs('d6',exist_ok=True)
n=0
# (1) tt 64코드 op — DNL/가중치/IB_EA
for code in range(64):
    open('d6/op_tt_%02d.spice'%code,'w').write(deck('tt',code,'3.3',
      '.control\nop\necho ===OP===\nprint v(vref_low)\nprint i(vload)\n.endc')); n+=1
# (2) 코너 x 64코드 TC
for c in ['tt','ss','ff']:
    for code in range(64):
        open('d6/tc_%s_%02d.spice'%(c,code),'w').write(deck(c,code,'3.3',
          '.dc temp -40 125 1\n.control\nrun\nwrdata tc_%s_%02d.csv v(vref_low)\n.endc'%(c,code))); n+=1
# (3) startup 4점
PWL='PWL(0 0 1u 0 3u 1.5 23u 1.5 28u 3.3 35u 3.3)'
for c,t in [('tt',27),('ss',-40),('ss',125),('ff',-40)]:
    open('d6/st_%s_%d.spice'%(c,t),'w').write(deck(c,31,PWL,
      '.control\nset temp=%d\ntran 50n 35u uic\nwrdata st_%s_%d.csv v(vapwr) v(vref_low)\n.endc'%(t,c,t))); n+=1
# (4) line reg
open('d6/lr.spice','w').write(deck('tt',31,'3.3',
  '.control\ndc vsource 2.7 3.6 0.01\nwrdata lr.csv v(vref_low)\n.endc')); n+=1
print('generated %d decks'%n)
