import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
# fig6: N=40 tt 단독 정밀
d = np.loadtxt('final_tc_tt.csv'); t,v = d[:,0], d[:,1]*1e3
tc = (v.max()-v.min())/(v.mean()*165)*1e6
fig, ax = plt.subplots(figsize=(9,5.5))
ax.plot(t, v, lw=2, color='tab:blue')
ax.axhline(v.max(), ls='--', c='gray', lw=.8); ax.axhline(v.min(), ls='--', c='gray', lw=.8)
ax.set_title('BGR VREF vs Temperature — N=40, real res_high_po (tt)\nTC = %.1f ppm/C, swing = %.2f mV' % (tc, v.max()-v.min()))
ax.set_xlabel('Temperature (C)'); ax.set_ylabel('VREF (mV)'); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig6_tc_N40_tt.png', dpi=150)
# fig7: 코너 3종
fig, ax = plt.subplots(figsize=(9,5.5))
print('corner | Vref@27C | swing(mV) | TC(ppm/C)')
for c in ['tt','ss','ff']:
    d = np.loadtxt('final_tc_%s.csv'%c); t,v = d[:,0], d[:,1]*1e3
    tc = (v.max()-v.min())/(v.mean()*165)*1e6
    v27 = v[np.argmin(abs(t-27))]
    print('%s | %.4f V | %.2f | %.1f' % (c, v27/1e3, v.max()-v.min(), tc))
    ax.plot(t, v, lw=2, label='%s (%.1f ppm, %.4fV@27C)'%(c,tc,v27/1e3))
ax.set_xlabel('Temperature (C)'); ax.set_ylabel('VREF (mV)')
ax.set_title('VREF vs T by corner — N=40, real resistors')
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig7_tc_corners_real.png', dpi=150)
print('wrote fig6, fig7')

