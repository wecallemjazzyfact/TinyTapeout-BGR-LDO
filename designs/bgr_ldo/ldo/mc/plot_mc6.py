#!/usr/bin/env python3
"""MC 6-bit 3단계 시각화."""
import json, statistics as st
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = json.load(open("mc_data.json"))
SPEC = 36.0
LAB = {"s1": "stage1  code 28 fixed",
       "s2": "stage2  binary code",
       "s3": "stage3  LUT rank"}

fig, ax = plt.subplots(2, 2, figsize=(13, 9))

# (0,0) 3단계 히스토그램
a = ax[0][0]
for k, c in (("s1", "C3"), ("s2", "C1"), ("s3", "C0")):
    dv = [(x["v"] - 1.8) * 1e3 for x in D[k]]
    dv = [x for x in dv if abs(x) < 150]
    sd = st.pstdev(dv)
    a.hist(dv, bins=60, alpha=.55, color=c,
           label="%s   σ=%.2f mV" % (LAB[k], sd))
a.axvline(-SPEC, color="k", ls="--", lw=1)
a.axvline(SPEC, color="k", ls="--", lw=1, label="spec ±36 mV")
a.set_xlabel("V_DDC − 1.800 V  (mV)"); a.set_ylabel("count")
a.set_title("MC trim compression (tt_mm, 27 °C, N≈300)")
a.legend(fontsize=8); a.grid(alpha=.3)

# (0,1) stage3 확대
a = ax[0][1]
dv = [(x["v"] - 1.8) * 1e3 for x in D["s3"]]
cl = [x for x in dv if abs(x) <= SPEC]
sd = st.pstdev(cl)
a.hist(cl, bins=40, color="C0", alpha=.75, edgecolor="w")
for s, ls in ((1, ":"), (3, "--")):
    for sign in (-1, 1):
        a.axvline(st.mean(cl) + sign * s * sd, color="C3", ls=ls, lw=1.2)
a.set_xlabel("V_DDC − 1.800 V  (mV)"); a.set_ylabel("count")
a.set_title("stage3 detail   σ=%.3f  3σ=%.3f mV   margin %.2f×"
            % (sd, 3 * sd, SPEC / (3 * sd)))
a.grid(alpha=.3)

# (1,0) stage2 vs stage3 산점도
a = ax[1][0]
n = min(len(D["s2"]), len(D["s3"]))
x = [(D["s2"][i]["v"] - 1.8) * 1e3 for i in range(n)]
y = [(D["s3"][i]["v"] - 1.8) * 1e3 for i in range(n)]
a.scatter(x, y, s=12, alpha=.5)
lim = 30
a.plot([-lim, lim], [-lim, lim], "k:", lw=1, label="no change")
a.axhline(0, color="C3", lw=1, alpha=.5); a.axvline(0, color="C3", lw=1, alpha=.5)
a.set_xlim(-lim, lim); a.set_ylim(-lim, lim)
a.set_xlabel("stage2 error (mV)"); a.set_ylabel("stage3 error (mV)")
a.set_title("binary → LUT rank  (removes the +17 mV MSB bias)")
a.legend(fontsize=8); a.grid(alpha=.3)

# (1,1) 코드 분포
a = ax[1][1]
import collections
c3 = collections.Counter(x["code"] for x in D["s3"])
ks = sorted(c3)
a.bar(ks, [c3[k] for k in ks], color="C0", alpha=.8)
a.axvline(28, color="C3", ls="--", lw=1.2, label="nominal 28")
a.set_xlabel("trim code"); a.set_ylabel("count")
a.set_title("codes used   %d…%d  (of 0…63)" % (min(ks), max(ks)))
a.legend(fontsize=8); a.grid(alpha=.3, axis="y")

plt.tight_layout()
plt.savefig("mc6_summary.png", dpi=150)
print("mc6_summary.png")
for k in ("s1", "s2", "s3"):
    dv = [(x["v"] - 1.8) * 1e3 for x in D[k]]
    cl = [x for x in dv if abs(x) <= SPEC]
    print("  %-4s N=%3d  σ=%7.3f  3σ=%7.3f  (|err|≤36: N=%d σ=%.3f)"
          % (k, len(dv), st.pstdev(dv), 3 * st.pstdev(dv), len(cl), st.pstdev(cl)))
