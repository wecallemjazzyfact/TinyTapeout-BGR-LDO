import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
fig, ax = plt.subplots(figsize=(9,5.5))
print('N | R6/R7(k) | Vref@27C | swing(mV) | TC(ppm/C)')
for N in [39,40,41,42,43]:
    d = np.loadtxt('n%d_tc.csv'%N); t, v = d[:,0], d[:,1]
    tc = (v.max()-v.min())/(v.mean()*165)*1e6
    v27 = v[np.argmin(abs(t-27))]
    print('%d | %.1f | %.5f | %.2f | %.1f' % (N, N*2.95, v27, (v.max()-v.min())*1e3, tc))
    ax.plot(t, v*1e3, label='N=%d (%.1f ppm)'%(N,tc))
ax.set_xlabel('Temperature (C)'); ax.set_ylabel('VREF (mV)')
ax.set_title('VREF vs T — real res_high_po_0p69, N x 2.95k units')
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig5_nsweep_realres.png', dpi=150)
print('wrote fig5_nsweep_realres.png')
