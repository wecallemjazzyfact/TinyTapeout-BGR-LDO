import numpy as np, glob, re
def rd(p):
    T=[];V=[]
    for i,l in enumerate(open(p)):
        if i==0: continue
        v=l.replace(",", " ").split()
        if len(v)>2:
            try: T.append(float(v[0])); V.append(float(v[2]))
            except ValueError: pass
    return np.array(T), np.array(V)
res={}
for p in sorted(glob.glob("res_*.csv")):
    t=re.search(r"res_(.+)\.csv",p).group(1)
    T,V=rd(p)
    if len(T)<10: continue
    c=np.polyfit((T-27)/300.15,V,3); res[t]=(c[1]*1e3,c[0]*1e3)
b=res["A0"]
print("%-10s %9s %9s %8s | %9s %9s"%("case","a2","a3","a3/a2","기여a2","기여a3"))
for k in sorted(res):
    a2,a3=res[k]
    print("%-10s %9.3f %9.3f %8.3f | %9.3f %9.3f"%(k,a2,a3,a3/a2,b[0]-a2,b[1]-a3))
