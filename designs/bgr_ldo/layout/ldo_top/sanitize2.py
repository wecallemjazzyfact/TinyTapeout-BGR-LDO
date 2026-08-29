import re, sys
src, dst = sys.argv[1], sys.argv[2]
n=0
out=[]
for line in open(src):
    s=line.rstrip("\n")
    if not s or s[0] in "*.":
        out.append(s); continue
    toks=s.split()
    for i,t in enumerate(toks):
        if "=" in t or "." not in t: continue
        if re.fullmatch(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", t): continue
        toks[i]=t.replace(".","_"); n+=1
    out.append(" ".join(toks))
open(dst,"w").write("\n".join(out)+"\n")
a=sum(1 for _ in open(src)); b=sum(1 for _ in open(dst))
print("행 %d -> %d  %s | 토큰 치환 %d"%(a,b,"OK" if a==b else "★불일치",n))
s=open(dst).read()
print("X %d / R %d / C %d"%(len(re.findall(r"(?im)^X",s)),len(re.findall(r"(?im)^R",s)),len(re.findall(r"(?im)^C",s))))
rest=sum(1 for l in open(dst) if l.strip() and l[0] not in "*." for t in l.split() if "=" not in t and "." in t and not re.fullmatch(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?",t))
print("잔여 점 %d"%rest)
