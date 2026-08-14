# 골든(bgr_core.spice) -> LVS 넷리스트
#  1) 저항 mult=1 제거 (netgen property error)
#  2) 레이아웃 매칭 더미 추가 (.ends 직전 삽입)
IN=bgr_core.spice
OUT=bgr_core_lvs.spice

sed 's/\(sky130_fd_pr__res_high_po_[0-9]*p[0-9]* L=[0-9.]*\) mult=1/\1/g'  > .tmp

python3 - .tmp  << 'PYEOF'
import sys, re
src=open(sys.argv[1]).read()
d=[]
for i in (1,2):
    d.append('XDUM_B%d VAPWR VAPWR VAPWR VAPWR sky130_fd_pr__pfet_g5v0d10v5 L=2 W=10 nf=1'%i)
for i in (1,2):
    d.append('XDUM_C%d VGND VGND VGND VGND sky130_fd_pr__nfet_g5v0d10v5 L=4 W=20 nf=1'%i)
for i in (1,2):
    d.append('XDUM_D%d VGND VGND VGND VGND sky130_fd_pr__nfet_g5v0d10v5 L=2 W=10 nf=1'%i)
for i in range(1,17):
    d.append('XDUM_Q%d VGND VGND VGND sky130_fd_pr__pnp_05v5_W0p68L0p68'%i)
for i in (1,2):
    d.append('XDUM_RA%d VGND VGND VGND sky130_fd_pr__res_high_po_0p69 L=30.23'%i)
for i in (1,2):
    d.append('XDUM_RB%d VGND VGND VGND sky130_fd_pr__res_high_po_0p69 L=57.15'%i)
blk='* ---- layout matching dummies (LVS only, not in simulation golden) ----\n'+'\n'.join(d)+'\n'
# bgr_core 서브회로의 .ends 앞에 삽입
m=re.search(r'(\.subckt bgr_core.*?)(^\.ends)', src, flags=re.S|re.M)
src=src[:m.end(1)]+blk+src[m.end(1):]
open(sys.argv[2],'w').write(src)
PYEOF
rm -f .tmp
echo -n 'mult 잔여: '; grep -c 'res_high_po.*mult=1' 
echo -n '더미 개수: '; grep -c '^XDUM_' 
echo -n '.subckt: '; grep -c '^.subckt bgr_core' 
