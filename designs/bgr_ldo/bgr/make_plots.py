import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, os

def load_tran(f):
    d = np.loadtxt(f)
    return d[:,0]*1e6, [d[:,2*i+1] for i in range(d.shape[1]//2)]

def tran_fig(csv, png, title, hold=None):
    if not os.path.exists(csv): print('skip', csv); return
    t, s = load_tran(csv)  # vapwr, vref, vbe1, sense, biasn, gtop
    fig, ax = plt.subplots(2,1, figsize=(10,7), sharex=True)
    for a in ax:
        if hold: a.axvspan(hold[0], hold[1], alpha=0.07, color='red')
    ax[0].plot(t,s[0],label='VAPWR'); ax[0].plot(t,s[1],label='VREF_LOW',lw=2)
    ax[0].plot(t,s[2],label='VBE1')
    ax[0].set_ylabel('V'); ax[0].legend(loc='lower right'); ax[0].grid(alpha=.3)
    ax[0].set_title(title)
    ax[1].plot(t,s[3],label='sense_out',lw=2); ax[1].plot(t,s[4],label='V_bias_n')
    ax[1].plot(t,s[5],label='V_gate_top')
    ax[1].set_ylabel('V'); ax[1].set_xlabel('time (us)')
    ax[1].legend(loc='upper right'); ax[1].grid(alpha=.3)
    fig.tight_layout(); fig.savefig(png, dpi=150); plt.close(fig); print('wrote', png)

tran_fig('w1_tt_stair.csv',  'fig1_tt_staircase.png',
         'Power-up: tt/27C staircase (1.5V hold = danger zone)', hold=(3,23))
tran_fig('w2_ss40_stair.csv','fig2_ss40_staircase.png',
         'Power-up: ss/-40C staircase (worst corner)', hold=(3,23))
tran_fig('w3_tt_ramp5u.csv', 'fig3_tt_ramp5us.png',
         'Power-up: tt/27C 5us ramp')

fig, ax = plt.subplots(figsize=(9,5.5))
for f,lab in [('w4_tc_tt.csv','tt'),('w5_tc_ss.csv','ss'),('w6_tc_ff.csv','ff')]:
    if os.path.exists(f):
        d = np.loadtxt(f); ax.plot(d[:,0], d[:,1]*1e3, label=lab, lw=2)
ax.set_xlabel('Temperature (C)'); ax.set_ylabel('VREF (mV)')
ax.set_title('VREF vs Temperature by corner (startup attached, ideal R)')
ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('fig4_tc_corners.png', dpi=150); plt.close(fig)
print('wrote fig4_tc_corners.png')
