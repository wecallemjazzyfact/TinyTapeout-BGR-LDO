#!/usr/bin/env python3
"""post-layout 시뮬 결과 시각화 -> plots/*.png (7장)
조건: PEX R+C (extract no coupling), tt/27, TRIM=0111(code7), RO_EN=0
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

B  = "/foss/designs/designs/bgr_ldo/layout/ldo_top"
AC, SD, OUT = B+"/acdata", B+"/simdata", B+"/plots"
os.makedirs(OUT, exist_ok=True)
C  = {"NL":"#2a78d6","IS":"#eb6834","SNK":"#1baf7a"}
N  = {"NL":"no load","IS":"ideal 1.5 mA","SNK":"onchip sink"}
DS = {"NL":"-","IS":"--","SNK":"-."}
VMAX = 1.98
plt.rcParams.update({"font.size":9,"axes.grid":True,"grid.alpha":.3,
                     "figure.dpi":130,"savefig.bbox":"tight"})

def rdcsv(p):
    f,m,ph=[],[],[]
    for i,l in enumerate(open(p)):
        if i==0: continue
        t=l.strip().split(",")
        if len(t)>=3: f.append(float(t[0])); m.append(float(t[1])); ph.append(float(t[2]))
    return f,m,ph

def rdwr(p,n):
    X,Y=[],[[] for _ in range(n)]
    for l in open(p):
        t=l.split()
        if len(t)>=2*n:
            X.append(float(t[0]))
            for k in range(n): Y[k].append(float(t[2*k+1]))
    return X,Y

def ok(p): return os.path.exists(p)

# 1 loop bode
fig,ax=plt.subplots(2,1,figsize=(7,6),sharex=True)
for k in ("NL","IS","SNK"):
    p=f"{AC}/bode_{k}.csv"
    if not ok(p): continue
    f,m,ph=rdcsv(p)
    ax[0].semilogx(f,m,DS[k],color=C[k],lw=1.4,label=N[k])
    ax[1].semilogx(f,ph,DS[k],color=C[k],lw=1.4,label=N[k])
ax[0].axhline(0,color="#888781",lw=.8,ls=":")
ax[1].axhline(-180,color="#888781",lw=.8,ls=":")
ax[0].set_ylabel("loop gain (dB)"); ax[1].set_ylabel("phase (deg)")
ax[1].set_xlabel("frequency (Hz)"); ax[1].set_ylim(-400,60)
ax[0].set_title("loop gain (dual injection)   PM 69.8 / 97.6 / 96.6 deg")
ax[0].legend(fontsize=8)
fig.savefig(f"{OUT}/1_loop_bode.png"); plt.close(fig)

# 2 load step
fig,ax=plt.subplots(1,2,figsize=(10,3.6))
if ok(f"{SD}/t1_load.txt"):
    t,(vd,_)=rdwr(f"{SD}/t1_load.txt",2)
    ax[0].plot([x*1e6 for x in t],vd,color="#e34948",lw=1.2)
    ax[0].set_title("extreme: ideal 1.5 mA, 100 ns\nover +160.0 mV")
if ok(f"{SD}/t1b_snken.txt"):
    t,(vd,_)=rdwr(f"{SD}/t1b_snken.txt",2)
    ax[1].plot([x*1e6 for x in t],vd,color="#1baf7a",lw=1.2)
    ax[1].set_title("real: SNK_EN path, 1 us\nover +28.9 mV")
for a in ax:
    a.axhline(VMAX,color="#e34948",lw=1.0,ls="--",label="VDDC abs max 1.98 V")
    a.set_xlabel("time (us)"); a.set_ylabel("VDDC (V)"); a.legend(fontsize=8)
fig.suptitle("load step response",y=1.02)
fig.savefig(f"{OUT}/2_load_step.png"); plt.close(fig)

# 3 line step
fig,ax=plt.subplots(1,2,figsize=(10,3.6))
if ok(f"{SD}/t2_line.txt"):
    t,(vd,_)=rdwr(f"{SD}/t2_line.txt",2)
    ax[0].plot([x*1e6 for x in t],vd,color="#e34948",lw=1.2)
    ax[0].set_title("extreme: 100 ns slew\ndip -142 / over +132 mV")
if ok(f"{SD}/t2b_line_slow.txt"):
    t,(vd,va)=rdwr(f"{SD}/t2b_line_slow.txt",2)
    ax[1].plot([x*1e6 for x in t],vd,color="#1baf7a",lw=1.2)
    ax[1].set_title("real: 10 us slew\ndip -2.78 / over +1.95 mV")
for a in ax:
    a.axhline(VMAX,color="#e34948",lw=1.0,ls="--",label="VDDC abs max 1.98 V")
    a.set_xlabel("time (us)"); a.set_ylabel("VDDC (V)"); a.legend(fontsize=8)
fig.suptitle("line step  VAPWR 3.3 -> 3.0 -> 3.3",y=1.02)
fig.savefig(f"{OUT}/3_line_step.png"); plt.close(fig)

# 4 PSRR
fig,ax=plt.subplots(figsize=(7,3.8))
for k in ("NL","IS","SNK"):
    p=f"{SD}/t3_psrr_{k}.txt"
    if not ok(p): continue
    f,(ps,_)=rdwr(p,2)
    ax.semilogx(f,ps,DS[k],color=C[k],lw=1.4,label=N[k])
ax.set_xlabel("frequency (Hz)"); ax.set_ylabel("PSRR (dB)")
ax.set_title("PSRR  VAPWR -> VDDC   (-51.9 dc / -27.7 @100k / -9.2 @1M)")
ax.legend(fontsize=8)
fig.savefig(f"{OUT}/4_psrr.png"); plt.close(fig)

# 5 startup
if ok(f"{SD}/t4_start.txt"):
    t,(vd,vr,va)=rdwr(f"{SD}/t4_start.txt",3)
    tt=[x*1e6 for x in t]
    fig,ax=plt.subplots(figsize=(7,3.8))
    ax.plot(tt,va,color="#888781",lw=1.0,ls=":",label="VAPWR")
    ax.plot(tt,vd,color="#2a78d6",lw=1.3,label="VDDC")
    ax.plot(tt,vr,color="#1baf7a",lw=1.3,label="VREF_LOW")
    ax.axhline(VMAX,color="#e34948",lw=1.0,ls="--")
    ax.set_xlabel("time (us)"); ax.set_ylabel("voltage (V)")
    ax.set_title("startup  ramp 20 us   settled at 25 us, overshoot +44 mV")
    ax.legend(fontsize=8)
    fig.savefig(f"{OUT}/5_startup.png"); plt.close(fig)

# 6 vg_snk slew
if ok(f"{SD}/t1b_snken.txt"):
    t,(vd,vg)=rdwr(f"{SD}/t1b_snken.txt",2)
    tt=[x*1e6 for x in t]
    fig,ax=plt.subplots(figsize=(7,3.4))
    ax.plot(tt,vg,color="#eb6834",lw=1.3,label="vg_snk (XM_snk gate)")
    ax.plot(tt,vd,color="#2a78d6",lw=1.0,ls=":",label="VDDC")
    ax.set_xlabel("time (us)"); ax.set_ylabel("voltage (V)")
    ax.set_title("slew limiter  XR_slew1/2 + XC_slew  (SNK_EN step at 10 us)")
    ax.legend(fontsize=8)
    fig.savefig(f"{OUT}/6_slew_limiter.png"); plt.close(fig)

# 7 margin summary
fig,ax=plt.subplots(figsize=(7,3.6))
lab=["load\nideal 100ns","load\nSNK_EN 1us","line\n100ns","line\n10us","startup\nramp 20us"]
pk =[1.98724,1.85611,1.95261,1.822132,1.87128]
col=["#e34948" if v>VMAX else "#1baf7a" for v in pk]
ax.bar(lab,pk,color=col,width=.55)
ax.axhline(VMAX,color="#e34948",lw=1.2,ls="--",label="VDDC abs max 1.98 V")
ax.axhline(1.82725,color="#888781",lw=.9,ls=":",label="nominal 1.827 V")
ax.set_ylim(1.75,2.02); ax.set_ylabel("peak VDDC (V)")
for i,v in enumerate(pk): ax.text(i,v+.004,f"{v:.3f}",ha="center",fontsize=8)
ax.set_title("peak VDDC vs absolute maximum")
ax.legend(fontsize=8,loc="lower right")
fig.savefig(f"{OUT}/7_margin.png"); plt.close(fig)

print("생성 완료:")
for f in sorted(os.listdir(OUT)):
    print("  ",f,os.path.getsize(os.path.join(OUT,f)),"bytes")
