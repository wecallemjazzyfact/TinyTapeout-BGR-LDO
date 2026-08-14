import re, subprocess, json
import numpy as np
LIB='.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice %s'
HEAD='''* night batch (R1 L=34.29)
%s
.include bgr_core_pex_rc_wrap.spice
VSource VAPWR 0 %s
Vload IB_EA 0 0.95
Vtrim0 t0 0 %.1f
Vtrim1 t1 0 %.1f
Vtrim2 t2 0 %.1f
Vtrim3 t3 0 %.1f
x1 VAPWR VREF_LOW IB_EA t0 t1 t2 t3 0 bgr_core
'''
def deck(corner,code,vsrc,ctrl):
    b=[1.8*((code>>i)&1) for i in range(4)]
    return HEAD%(LIB%corner,vsrc,b[0],b[1],b[2],b[3])+ctrl+'\n.end\n'
def run(name,txt,to=900):
    open(name,'w').write(txt)
    try:
        r=subprocess.run(['ngspice','-b',name],capture_output=True,text=True,timeout=to)
        return r.stdout+r.stderr
    except Exception as e: return 'TIMEOUT/ERR '+str(e)
def g(p,s):
    m=re.search(p,s); return float(m.group(1)) if m else None

out=run('n_chk.spice', deck('tt',7,'3.3',
  '.control\nop\nprint v(vref_low)\nprint i(vload)\nprint -i(vsource)\n.endc'))
vr=g(r'v\(vref_low\)\s*=\s*([0-9.eE+-]+)',out)
ib=g(r'i\(vload\)\s*=\s*([0-9.eE+-]+)',out)
iq=g(r'i\(vsource\)\s*=\s*([0-9.eE+-]+)',out)
print('SANITY Vref=%s  i(vload)=%s  IQ=%s'%(vr,ib,iq), flush=True)
if vr is None or not (1.15<vr<1.28) or ib is None or abs(ib)<1e-6:
    print('!! ABORT — 래퍼/넷리스트 이상'); print(out[-1500:]); raise SystemExit(1)
print('sanity OK -> batch start', flush=True)

res={}
for corner in ['tt','ss','ff']:
    for code in range(16):
        tag='%s_%02d'%(corner,code)
        run('n_tc_%s.spice'%tag, deck(corner,code,'3.3',
          '.dc temp -40 125 1\n.control\nrun\nwrdata n_tc_%s.csv v(vref_low)\n.endc'%tag))
        try:
            d=np.loadtxt('n_tc_%s.csv'%tag); T,v=d[:,0],d[:,1]
            res[tag]=dict(tc=float((v.max()-v.min())/(v.mean()*165)*1e6),
                          v27=float(v[np.argmin(abs(T-27))]),
                          vmin=float(v.min()), vmax=float(v.max()))
        except Exception as e: res[tag]=dict(err=str(e))
    print('%s done'%corner, flush=True)
    json.dump(res,open('night_tc.json','w'),indent=1)

PWL='PWL(0 0 1u 0 3u 1.5 23u 1.5 28u 3.3 35u 3.3)'
for corner,tmp in [('tt',27),('ss',-40),('ss',125),('ff',-40)]:
    tag='%s_%d'%(corner,tmp)
    run('n_st_%s.spice'%tag, deck(corner,7,PWL,
      '.control\nset temp=%d\ntran 50n 35u uic\nwrdata n_st_%s.csv v(vapwr) v(vref_low)\n.endc'%(tmp,tag)))
print('startup done', flush=True)

run('n_lr.spice', deck('tt',7,'3.3',
  '.control\ndc vsource 2.7 3.6 0.01\nwrdata n_lr.csv v(vref_low)\n.endc'))
print('ALL DONE', flush=True)
