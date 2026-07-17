import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# fig13: MC 히스토그램
v = np.loadtxt('mc_vref.txt')
mu, sd = v.mean(), v.std(ddof=1)
fig, ax = plt.subplots(figsize=(9,5.5))
ax.hist(v*1000, bins=20, edgecolor='k', alpha=.75, color='steelblue')
ax.axvline(mu*1000, color='r', lw=2, label='mean %.1f mV' % (mu*1000))
for k,c in [(-3,'orange'),(3,'orange')]:
    ax.axvline((mu+k*sd)*1000, color=c, ls='--', lw=1.5,
               label='%+dsigma' % k if k>0 else None)
ax.axvline(1200, color='g', lw=2, ls=':', label='target 1200 mV')
ax.set_xlabel('VREF (mV)'); ax.set_ylabel('count')
ax.set_title('Monte Carlo VREF (N=%d, MM+PR)\nsigma=%.2f%%, 3sigma=+-%.2f%%  [after area scaling]'
             % (len(v), sd/mu*100, 3*sd/mu*100))
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig13_mc_final.png', dpi=150)
print('fig13: N=%d mean=%.5f sigma=%.5f (%.2f%%) 3sig=+-%.2f%%'
      % (len(v), mu, sd, sd/mu*100, 3*sd/mu*100))

# fig14: MM/PR 분해 막대
fig, ax = plt.subplots(figsize=(7,5))
labels = ['MM\n(local mismatch)', 'PR\n(global process)', 'Total\n(before)', 'Total\n(after area x4)']
vals = [4.58, 1.38, 4.00, sd/mu*100]
colors = ['tomato','steelblue','gray','seagreen']
bars = ax.bar(labels, vals, color=colors, edgecolor='k')
for b,v_ in zip(bars, vals):
    ax.text(b.get_x()+b.get_width()/2, v_+0.08, '%.2f%%'%v_, ha='center', fontweight='bold')
ax.set_ylabel('sigma of VREF (%)')
ax.set_title('MC variance decomposition\nMM dominates (91% of variance) -> area scaling effective')
ax.grid(alpha=.3, axis='y')
fig.tight_layout(); fig.savefig('fig14_mc_decomp.png', dpi=150)
print('fig14 written')
