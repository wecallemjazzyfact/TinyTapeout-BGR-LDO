#!/usr/bin/env python3
"""이중주입 루프이득 합성 (Middlebrook):  T = (Tv*Ti - 1)/(Tv + Ti + 2)"""
import cmath, math, os
D="/foss/designs/designs/bgr_ldo/layout/ldo_top/acdata"
CONDS=[("NL","무부하 (분압만)"),("IS","이상원 1.5 mA"),("SNK","온칩 싱크 ON")]
def read(p):
    o=[]
    for line in open(p):
        t=line.split()
        if len(t)>=4: o.append((float(t[0]),complex(float(t[1]),float(t[3]))))
    return o
def ix(x0,y0,x1,y1,yt):
    if y1==y0: return x0
    a,b=math.log10(x0),math.log10(x1)
    return 10**(a+(b-a)*(yt-y0)/(y1-y0))
def iy(x0,y0,x1,y1,xt):
    a,b,c=math.log10(x0),math.log10(x1),math.log10(xt)
    return y0 if b==a else y0+(y1-y0)*(c-a)/(b-a)
def analyze(f,m,p):
    r={"Tdc":m[0],"UGF":None,"PM":None,"GM":None,"fGM":None}
    for i in range(len(f)-1):
        if m[i]>0>=m[i+1]:
            x=ix(f[i],m[i],f[i+1],m[i+1],0.0)
            r["UGF"]=x; r["PM"]=iy(f[i],p[i],f[i+1],p[i+1],x)+180.0; break
    for i in range(len(f)-1):
        if (p[i]+180)*(p[i+1]+180)<0 and f[i]>1e3:
            x=ix(f[i],p[i],f[i+1],p[i+1],-180.0)
            r["fGM"]=x; r["GM"]=-iy(f[i],m[i],f[i+1],m[i+1],x); break
    return r
rows=[]; bode={}
for k,lab in CONDS:
    a,b=os.path.join(D,k+"_tv.txt"),os.path.join(D,k+"_ti.txt")
    if not(os.path.exists(a) and os.path.exists(b)): print("!!",k,"파일 없음"); continue
    Tv,Ti=read(a),read(b)
    f=[];m=[];p=[];prev=None;off=0.0
    for (f1,tv),(f2,ti) in zip(Tv,Ti):
        T=(tv*ti-1)/(tv+ti+2)
        mm=20*math.log10(abs(T)) if abs(T)>0 else -300.0
        aa=math.degrees(cmath.phase(T))+off
        if prev is not None:
            while aa-prev>180: aa-=360; off-=360
            while aa-prev<-180: aa+=360; off+=360
        prev=aa; f.append(f1); m.append(mm); p.append(aa)
    r=analyze(f,m,p); rows.append((k,lab,r)); bode[k]=(f,m,p)
    with open(os.path.join(D,"bode_"+k+".csv"),"w") as fp:
        fp.write("freq,mag_db,phase_deg\n")
        for x,y,z in zip(f,m,p): fp.write("%.6e,%.4f,%.4f\n"%(x,y,z))
print("="*74)
print("post-layout 루프이득 (이중주입, PEX R+C, tt/27, TRIM=0111)")
print("="*74)
print("%-18s%10s%12s%10s%10s%11s"%("조건","Tdc[dB]","UGF[MHz]","PM[deg]","GM[dB]","fGM[MHz]"))
print("-"*74)
for k,lab,r in rows:
    u="%.4f"%(r["UGF"]/1e6) if r["UGF"] else "-"
    pm="%.2f"%r["PM"] if r["PM"] else "-"
    gm="%.2f"%r["GM"] if r["GM"] else "-"
    fg="%.3f"%(r["fGM"]/1e6) if r["fGM"] else "-"
    print("%-18s%10.2f%12s%10s%10s%11s"%(lab,r["Tdc"],u,pm,gm,fg))
print("-"*74)
print("스펙: PM > 45 (tt 60), GM > 10 dB")
print()
for k,lab,r in rows:
    f,m,p=bode[k]; st=max(1,len(f)//55)
    print("### BODE",k)
    print("freq,mag_db,phase_deg")
    for i in range(0,len(f),st): print("%.4e,%.3f,%.3f"%(f[i],m[i],p[i]))
    print("%.4e,%.3f,%.3f"%(f[-1],m[-1],p[-1]))
    print()
