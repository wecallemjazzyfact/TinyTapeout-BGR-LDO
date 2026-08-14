import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, os

def tc(f):
    d=np.loadtxt(f); t,v=d[:,0],d[:,1]
    return v[np.argmin(abs(t-27))], (v.max()-v.min())/(v.mean()*165)*1e6, t, v

print('=== TC comparison (W10/L2 -> W20/L4) ===')
print('corner | before Vref/TC        | after Vref/TC')
for c in ['tt','ss','ff']:
    vb,tb,_,_ = tc('before_tc_%s.csv'%c)
    va,ta,_,_ = tc('after_tc_%s.csv'%c)
    print('%s     | %.5f V / %5.1f ppm | %.5f V / %5.1f ppm' % (c, vb, tb, va, ta))

print()
print('=== Line reg ===')
for tag in ['before','after']:
    d=np.loadtxt('%s_lr.csv'%tag); vin,vref,eq = d[:,0],d[:,1],d[:,3]
    i30,i36=np.argmin(abs(vin-3.0)),np.argmin(abs(vin-3.6))
    lr=(vref[i36]-vref[i30])/(vin[i36]-vin[i30])
    print('%-7s: %.4f %%/V   eq_err delta = %+.1f uV' % (tag, lr/vref[i30]*100, (eq[-1]-eq[0])*1e6))

# fig: TC 코너 before/after 나란히
fig, ax = plt.subplots(1,2, figsize=(13,5), sharey=False)
for k,tag in enumerate(['before','after']):
    for c in ['tt','ss','ff']:
        v27,t_ppm,t,v = tc('%s_tc_%s.csv'%(tag,c))
        ax[k].plot(t, v*1e3, lw=2, label='%s (%.1f ppm)'%(c,t_ppm))
    ax[k].set_xlabel('Temperature (C)'); ax[k].set_ylabel('VREF (mV)')
    ax[k].set_title('%s area scaling (%s)' % (tag, 'W10/L2' if tag=='before' else 'W20/L4'))
    ax[k].legend(); ax[k].grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig15_tc_before_after.png', dpi=150)
print('wrote fig15_tc_before_after.png')

# fig: MC 히스토그램 before/after
if os.path.exists('mc_vref_before.txt') and os.path.exists('mc_vref_after.txt'):
    fig, ax = plt.subplots(1,2, figsize=(13,5), sharex=True)
    for k,(f,lab,col) in enumerate([('mc_vref_before.txt','before (W10/L2)','tab:red'),
                                     ('mc_vref_after.txt','after (W20/L4)','tab:blue')]):
        v=np.loadtxt(f); mu,sd=v.mean(), v.std(ddof=1)
        ax[k].hist(v*1e3, bins=20, color=col, alpha=.75, edgecolor='k')
        ax[k].axvline(mu*1e3, color='k', lw=2)
        ax[k].axvline((mu-3*sd)*1e3, color='orange', ls='--')
        ax[k].axvline((mu+3*sd)*1e3, color='orange', ls='--')
        ax[k].set_xlabel('VREF (mV)'); ax[k].set_ylabel('count')
        ax[k].set_title('%s\nN=%d, sigma=%.2f%%, +-3sigma=+-%.1f%%'%(lab,len(v),sd/mu*100,3*sd/mu*100))
        ax[k].grid(alpha=.3)
        print('%-22s: N=%d mean=%.5f sigma=%.2f%%' % (lab, len(v), mu, sd/mu*100))
    fig.tight_layout(); fig.savefig('fig16_mc_before_after.png', dpi=150)
    print('wrote fig16_mc_before_after.png')
else:
    print('(MC 파일 대기 중 — before MC 끝나면 재실행)')
