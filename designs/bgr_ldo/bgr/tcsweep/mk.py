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
assert n == 4, "이름 치환 %d건 (4 기대)" % n
VAL = r"(\{[^}]*\}|\x27[^\x27]*\x27|[-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)"
for k, v in mods.items():
    s, c = re.subn(r"(?<![A-Za-z0-9_])" + k + r"\s*=\s*" + VAL, "%s = %s" % (k, v), s)
    assert c == 1, "%s 치환 %d건 (1 기대)" % (k, c)
    print("  %s -> %s" % (k, v))
open("mod_%s.spice" % tag, "w").write(s)
tb = open("ab_A0.sp").read()
tb = tb.replace("* QA standalone A0 (baseline)", "* QA standalone " + tag)
tb = tb.replace(".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt",
  ".lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt\n.include /foss/designs/designs/bgr_ldo/bgr/tcsweep/mod_%s.spice" % tag)
tb = tb.replace("XQ 0 0 e " + ORIG, "XQ 0 0 e PNPTEST")
tb = tb.replace("q" + ORIG.lower(), "qdut")
open("ab_%s.sp" % tag, "w").write(tb)
print("생성: ab_%s.sp" % tag)
