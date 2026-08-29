import re, sys
src, dst = sys.argv[1], sys.argv[2]
NUM = re.compile(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?[a-zA-Z]*$")
n = 0; out = []
for line in open(src):
    s = line.rstrip("\n")
    if not s or s[0] in "*.":
        out.append(s); continue
    toks = s.split()
    for i, t in enumerate(toks):
        if "=" in t or "." not in t: continue
        if NUM.fullmatch(t): continue
        toks[i] = t.replace(".", "_"); n += 1
    out.append(" ".join(toks))
open(dst, "w").write("\n".join(out) + "\n")
a = sum(1 for _ in open(src)); b = sum(1 for _ in open(dst))
s = open(dst).read()
print("행 %d->%d %s | 치환 %d" % (a, b, "OK" if a == b else "★", n))
print("X %d / R %d / C %d" % (len(re.findall(r"(?im)^X", s)), len(re.findall(r"(?im)^R", s)), len(re.findall(r"(?im)^C", s))))
print("잔여점 %d" % sum(1 for l in open(dst) if l.strip() and l[0] not in "*." for t in l.split() if "=" not in t and "." in t and not NUM.fullmatch(t)))
print("샘플:")
for l in open(dst):
    if l.startswith(("X0 ", "X1 ", "C0 ", "C1 ")): print("  " + l.strip()[:110])
