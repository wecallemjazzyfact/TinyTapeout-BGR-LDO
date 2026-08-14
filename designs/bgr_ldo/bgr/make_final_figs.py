import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# --- fig13: MC 히스토그램 (전/후 비교) ---
fig, ax = plt.subplots(1, 2, figsize=(13,5))
for k,(f,lab,col) in enumerate([('mc_vref.txt','before (W10/L2)','tab:red'),
                                 ('mc_vref.txt','after (W20/L4)','tab:blue')]):
    if not os.path.exists(f): 
        print('skip', f); continue
    v = np.loadtxt(f); mu, sd = v.mean(), v.std(ddof=1)
    ax[k].hist(v*1e3, bins=20, color=col, alpha=.75, edgecolor='k')
    ax[k].axvline(mu*1e3, color='k', lw=2, label='mean %.1f mV'%(mu*1e3))
    ax[k].axvline((mu-3*sd)*1e3, color='orange', ls='--', label='±3σ')
    ax[k].axvline((mu+3*sd)*1e3, color='orange', ls='--')
    ax[k].set_xlabel('VREF (mV)'); ax[k].set_ylabel('count')
    ax[k].set_title('%s\nN=%d, σ=%.2f%%, ±3σ=±%.1f%%'%(lab,len(v),sd/mu*100,3*sd/mu*100))
    ax[k].legend(fontsize=8); ax[k].grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig13_mc_hist.png', dpi=150)
print('wrote fig13_mc_hist.png')

# --- fig14: MM vs PR 기여도 ---
fig, ax = plt.subplots(figsize=(7,5))
labels = ['MM\n(local mismatch)', 'PR\n(global process)']
sigmas = [4.58, 1.38]
bars = ax.bar(labels, sigmas, color=['tab:red','tab:blue'], alpha=.8, edgecolor='k')
for b,s in zip(bars,sigmas):
    ax.text(b.get_x()+b.get_width()/2, s+0.1, '%.2f%%'%s, ha='center', fontweight='bold')
ax.set_ylabel('σ of VREF (%)')
ax.set_title('MC variance decomposition (20 samples each)\nMM accounts for 91.5%% of variance → area scaling is the fix')
ax.grid(alpha=.3, axis='y')
fig.tight_layout(); fig.savefig('fig14_mc_split.png', dpi=150)
print('wrote fig14_mc_split.png')
