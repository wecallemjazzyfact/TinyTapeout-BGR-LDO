import re, sys, os
os.chdir("/foss/designs/designs/bgr_ldo/bgr/tcsweep")
ORIG = "sky130_fd_pr__pnp_05v5_W0p68L0p68"
tag = sys.argv[1]
mods = dict(a.split("=", 1) for a in sys.argv[2:])
s = open("pnp_model.txt").read()
n = 0
s, c = re.subn(r"(?im)^(\s*\.subckt\s+)" + re.escape(ORIG) + r"(?=\s)", r"\1PNPTEST", s); n += c
s, c = re.subn(r"(?im)^(\s*\.ends\s+)" + re.escape(ORIG) + r"\s*$", r"\1PNPTEST", s); n += c
s, c = re.subn(r"(?im)^(\s*\.model\s+)" + re.escape(ORIG) + r"_model(?=\s)", r"\1MODTEST", s); n += c
s, c = re.subn(r"(?im)^(Q)" + re.escape(ORIG) + r"(\s+\S+\s+\S+\s+\S+\s+\S+\s+)" + re.escape(ORIG) + r"_model\s*$", r"QDUT\2MODTEST", s); n += c
assert n == 4, "이름치환 %d" % n
VAL = r"(\{[^}]*\}|\x27[^\x27]*\x27|[-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)"
for k, v in mods.items():
    s, c = re.subn(r"(?<![A-Za-z0-9_])" + k + r"\s*=\s*" + VAL, "%s = %s" % (k, v), s)
    assert c == 1, "%s 치환 %d" % (k, c)
open("modp_%s.spice" % tag, "w").write(s)

rows = []
with open("s1_raw.csv") as f:
    f.readline()
    for l in f:
        v = l.replace(",", " ").split()
        if len(v) >= 9: rows.append([float(x) for x in v])
IE = [(r[0], abs(r[5])+abs(r[6]), abs(r[7])+abs(r[8])) for r in rows]
L = ["* pair ablation " + tag,
     ".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt",
     ".include /foss/designs/designs/bgr_ldo/bgr/tcsweep/modp_%s.spice" % tag,
     "IEA 0 ea 3u", "IEB 0 eb 3u", "XQA 0 0 ea PNPTEST"]
for i in range(8): L.append("XQB%d 0 0 eb PNPTEST" % i)
L += [".control", "echo temp_C,vbeA_V,vbeB_V"]
for T, ia, ib1 in IE:
    L += ["set temp = %g" % T, "alter IEA = %.9g" % ia, "alter IEB = %.9g" % (ib1*8),
          "op", "echo %g,$&v(ea),$&v(eb)" % T]
L += [".endc", ".end"]
open("pab_%s.sp" % tag, "w").write("\n".join(L) + "\n")
print("ok " + tag)
