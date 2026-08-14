import re, os, csv, subprocess
D = "/foss/designs/designs/bgr_ldo/bgr/tcsweep"
os.chdir(D)

# --- Stage 1 실측 Ie 로드 ---
rows = []
with open("s1_raw.csv") as f:
    hdr = f.readline().split()
    for l in f:
        v = l.replace(",", " ").split()
        if len(v) >= 9:
            rows.append([float(x) for x in v])
IE = [(r[0], abs(r[5]) + abs(r[6])) for r in rows]   # T, Ie_A
print("Stage1 점수:", len(IE), " Ie 범위 %.4f~%.4f uA" % (IE[0][1]*1e6, IE[-1][1]*1e6))

base = open("pnp_model.txt").read()

CASES = {
 "A0": {},
 "A1": {"tikf1": "0"},
 "A2": {"tikf1": "0", "ikf": "1"},
 "A3": {"tikf1": "0", "ikf": "1", "xtb": "0"},
 "A4": {"tikf1": "0", "ikf": "1", "xtb": "0", "ise": "1e-30"},
 "A5": {"tikf1": "0", "ikf": "1", "xtb": "0", "ise": "1e-30", "tnf1": "0", "tnf2": "0"},
 "A6": {"tikf1": "0", "ikf": "1", "xtb": "0", "ise": "1e-30", "tnf1": "0", "tnf2": "0",
        "re": "0", "rb": "0", "rc": "0", "rbm": "0"},
 "A7": {"tikf1": "0", "ikf": "1", "xtb": "0", "ise": "1e-30", "tnf1": "0", "tnf2": "0",
        "re": "0", "rb": "0", "rc": "0", "rbm": "0", "vaf": "1e12", "var": "1e12"},
 # 개별 효과 (one-at-a-time)
 "B_ikf":  {"tikf1": "0", "ikf": "1"},
 "B_xtb":  {"xtb": "0"},
 "B_ise":  {"ise": "1e-30"},
 "B_tnf":  {"tnf1": "0", "tnf2": "0"},
 "B_rser": {"re": "0", "rb": "0", "rc": "0", "rbm": "0"},
 "B_vaf":  {"vaf": "1e12", "var": "1e12"},
 "B_xti":  {"xti": "0"},
}
VALPAT = r"(\{[^}]*\}|\x27[^\x27]*\x27|[-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)"

for tag, mods in CASES.items():
    m = base.replace("sky130_fd_pr__pnp_05v5_W0p68L0p68", "PNP_" + tag)
    for k, v in mods.items():
        m2, n = re.subn(r"(?<![A-Za-z0-9_])(" + k + r")\s*=\s*" + VALPAT, r"\1 = " + v, m)
        if n == 0:
            print("  !! %s: %s 치환 실패" % (tag, k))
        m = m2
    open("mod_%s.spice" % tag, "w").write(m)

    L = ['* QA standalone ablation %s (Ie forced from real BGR)' % tag,
         '.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt',
         '.include %s/mod_%s.spice' % (D, tag),
         'IE 0 e 1u',
         'XQ 0 0 e PNP_%s' % tag,
         '.control',
         'echo temp_C,ie_A,vbe_V,ic_A,ib_A']
    for T, ie in IE:
        L += ['set temp = %g' % T,
              'alter IE = %.9g' % ie,
              'op',
              'echo $&tt_dummy' if False else
              'echo %g,%.9g,$&v(e),$&@q.xq.qPNP_%s[ic],$&@q.xq.qPNP_%s[ib]' % (T, ie, tag, tag)]
    L += ['.endc', '.end']
    open("ab_%s.sp" % tag, "w").write("\n".join(L) + "\n")

print("생성 완료:", len(CASES), "케이스")
