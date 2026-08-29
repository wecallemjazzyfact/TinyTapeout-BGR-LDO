#!/usr/bin/env python3
"""MC 트림 전/후 비교 (단독 플롯)

트림 전: mc/out_*.txt  (stage1, "DATA chunk sample ui vddc vref", ui=6 고정값 사용)
트림 후: mc/out2_*.txt (stage2, "FINAL chunk sample ui" 다음 줄 "v(vddc)=..")
조건: tt_mm / 27C / SNK_EN=1.8 / RO_EN=0 / N~300 / code=15-ui_in
출력: plots/9_mc_before_after.png
"""
import glob, re, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

B  = "/foss/designs/designs/bgr_ldo/layout/ldo_top"
MC = "/foss/designs/designs/bgr_ldo/ldo/mc"
OUT = B + "/plots"
SPEC = 36.0

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .3,
                      "figure.dpi": 150, "savefig.bbox": "tight"})

# ---- 트림 전: ui=6 고정 (stage1) ----
pre = []
for f in sorted(glob.glob(f"{MC}/out_*.txt")):
    for l in open(f):
        m = re.match(r"^DATA\s+\d+\s+\d+\s+6\s+([\d.eE+-]+)\s+[\d.eE+-]+", l)
        if m:
            pre.append((float(m.group(1)) - 1.8) * 1000)

# ---- 트림 후: 실측 최적 ui (stage2) ----
D = {}
for f in sorted(glob.glob(f"{MC}/out2_*.txt")):
    for l in open(f):
        m = re.match(r"^FINAL\s+(\d+)\s+(\d+)\s+(\d+)", l)
        if m:
            k, i, ui = map(int, m.groups())
            D[(k, i)] = {}
        m2 = re.match(r"^v\(vddc\)\s*=\s*([\d.eE+-]+)", l)
        if m2 and D:
            D[list(D)[-1]]["vddc"] = float(m2.group(1))
post = [(v["vddc"] - 1.8) * 1000 for v in D.values() if "vddc" in v]

assert pre and post, "데이터 없음 - mc/out_*.txt, mc/out2_*.txt 경로 확인"

sd_pre, sd_post = st.pstdev(pre), st.pstdev(post)
m_pre, m_post = st.mean(pre), st.mean(post)

fig, ax = plt.subplots(figsize=(9, 5.2))

lo, hi = -130, 130
bins = 40
ax.hist(pre, bins=bins, range=(lo, hi), color="#e34948", alpha=.45,
        edgecolor="white", linewidth=.4, label=f"before trim (\u03c3={sd_pre:.1f} mV)")
ax.hist(post, bins=bins, range=(lo, hi), color="#1baf7a", alpha=.75,
        edgecolor="white", linewidth=.4, label=f"after trim  (\u03c3={sd_post:.1f} mV)")

for x, c in ((-SPEC, "#333"), (SPEC, "#333")):
    ax.axvline(x, color=c, lw=1.4, ls="--")
ax.axvline(-SPEC, color="#333", lw=1.4, ls="--", label=f"spec \u00b1{SPEC:.0f} mV")

ax.set_xlim(lo, hi)
ax.set_xlabel("VDDC deviation from 1.800 V (mV)")
ax.set_ylabel("count")
ax.set_title(
    f"Monte Carlo — trim compression   tt_mm/27\u00b0C, N={len(pre)}\u2192{len(post)}\n"
    f"\u03c3: {sd_pre:.2f} mV \u2192 {sd_post:.2f} mV  "
    f"({sd_pre/sd_post:.1f}\u00d7 reduction)   "
    f"3\u03c3 after: {3*sd_post:.2f} mV (spec margin {SPEC/(3*sd_post):.1f}\u00d7)",
    fontsize=10.5)
ax.legend(fontsize=9, loc="upper right")

fig.savefig(f"{OUT}/9_mc_before_after.png")
print("wrote", f"{OUT}/9_mc_before_after.png")
print(f"  before: N={len(pre)}  mean={m_pre:+.2f}mV  sigma={sd_pre:.2f}mV")
print(f"  after : N={len(post)}  mean={m_post:+.2f}mV  sigma={sd_post:.2f}mV  3sigma={3*sd_post:.2f}mV")
