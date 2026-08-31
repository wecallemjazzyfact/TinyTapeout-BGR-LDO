#!/usr/bin/env python3
"""코너별 TC 곡선 — DC temp sweep 125..-40, 1도 간격."""
import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

CODE = {"tt":28, "ss":28, "ff":39, "sf":28, "fs":28}
COL  = {"tt":"C0","ss":"C1","ff":"C2","sf":"C3","fs":"C4"}

D={}
for cn in CODE:
    d=np.loadtxt("tcdc/%s.txt"%cn)          # T Vddc T Vref
    o=np.argsort(d[:,0])
    D[cn]={"T":d[o,0], "v":d[o,1], "vr":d[o,3]}

fig, ax = plt.subplots(1,2, figsize=(13,5))

a=ax[0]
for cn in CODE:
    a.plot(D[cn]["T"], D[cn]["v"]*1e3, lw=1.8, color=COL[cn],
           label="%s  code %d"%(cn,CODE[cn]))
a.axhline(1800, color="k", ls=":", lw=1, alpha=.6)
a.axhline(1836, color="k", ls="--", lw=1, alpha=.4)
a.axhline(1764, color="k", ls="--", lw=1, alpha=.4, label="spec ±36 mV")
a.set_xlabel("Temperature (°C)"); a.set_ylabel("V_DDC (mV)")
a.set_title("V_DDC vs temperature — per-corner optimum trim code")
a.grid(alpha=.3); a.legend(fontsize=8)

a=ax[1]
for cn in CODE:
    T,v = D[cn]["T"], D[cn]["v"]
    ref = np.interp(25, T, v)
    a.plot(T, (v-ref)*1e3, lw=1.8, color=COL[cn], label=cn)
    i=int(np.argmax(v)); j=int(np.argmin(v))
    a.plot(T[i],(v[i]-ref)*1e3,"^",ms=7,color=COL[cn])
    a.plot(T[j],(v[j]-ref)*1e3,"v",ms=7,color=COL[cn])
a.axhline(0, color="k", ls=":", lw=1, alpha=.6)
a.set_xlabel("Temperature (°C)"); a.set_ylabel("ΔV_DDC from 25 °C (mV)")
a.set_title("normalised — curvature (▲ peak  ▼ valley)")
a.grid(alpha=.3); a.legend(fontsize=8)

plt.tight_layout(); plt.savefig("tc6_corners.png", dpi=150)
print("tc6_corners.png\n")

print(" corner code  N    peak      valley    spread     TC(box)")
out={}
for cn in CODE:
    T,v = D[cn]["T"], D[cn]["v"]
    sp=(v.max()-v.min())*1e3
    dT=T.max()-T.min()
    tc=sp/1e3/1.8/dT*1e6
    out[cn]={"peak":float(T[np.argmax(v)]), "valley":float(T[np.argmin(v)]),
             "spread_mV":sp, "TC_ppm":tc, "V25":float(np.interp(25,T,v))}
    print("  %-4s  %2d  %3d  %+5.0f°C  %+5.0f°C  %6.3f mV  %6.2f ppm/°C"%(
        cn,CODE[cn],len(T),T[np.argmax(v)],T[np.argmin(v)],sp,tc))
w=max(out,key=lambda k: out[k]["TC_ppm"])
print()
print("  worst  %s  %.2f ppm/°C   |  typ %.2f (others avg)"%(
    w,out[w]["TC_ppm"],
    sum(out[k]["TC_ppm"] for k in out if k!=w)/(len(out)-1)))
print("  25°C spread across corners  %.3f mV"%(
    (max(out[k]["V25"] for k in out)-min(out[k]["V25"] for k in out))*1e3))
json.dump(out, open("tcdc/summary.json","w"), indent=1)
