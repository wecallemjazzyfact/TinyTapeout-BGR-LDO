.title thin-ox W scan  L=0.15, VGS=VDS=0.9, tt/27
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.temp 27
Vdn dcn 0 0.9
Vgn gn 0 0.9
Vdp dcp 0 -0.9
Vgp gp 0 -0.9
Vn0 n0 dcn 0
Vn1 n1 dcn 0
Vn2 n2 dcn 0
Vn3 n3 dcn 0
Vn4 n4 dcn 0
Vn5 n5 dcn 0
Vn6 n6 dcn 0
Vn7 n7 dcn 0
XN0 n0 gn 0 0 sky130_fd_pr__nfet_01v8 W=0.42 L=0.15
XN1 n1 gn 0 0 sky130_fd_pr__nfet_01v8 W=0.65 L=0.15
XN2 n2 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XN3 n3 gn 0 0 sky130_fd_pr__nfet_01v8 W=1.5 L=0.15
XN4 n4 gn 0 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XN5 n5 gn 0 0 sky130_fd_pr__nfet_01v8 W=3 L=0.15
XN6 n6 gn 0 0 sky130_fd_pr__nfet_01v8 W=5 L=0.15
XN7 n7 gn 0 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
Vp0 p0 dcp 0
Vp1 p1 dcp 0
Vp2 p2 dcp 0
Vp3 p3 dcp 0
Vp4 p4 dcp 0
Vp5 p5 dcp 0
Vp6 p6 dcp 0
Vp7 p7 dcp 0
XP0 p0 gp 0 0 sky130_fd_pr__pfet_01v8 W=0.42 L=0.15
XP1 p1 gp 0 0 sky130_fd_pr__pfet_01v8 W=0.65 L=0.15
XP2 p2 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.15
XP3 p3 gp 0 0 sky130_fd_pr__pfet_01v8 W=1.5 L=0.15
XP4 p4 gp 0 0 sky130_fd_pr__pfet_01v8 W=2 L=0.15
XP5 p5 gp 0 0 sky130_fd_pr__pfet_01v8 W=3 L=0.15
XP6 p6 gp 0 0 sky130_fd_pr__pfet_01v8 W=5 L=0.15
XP7 p7 gp 0 0 sky130_fd_pr__pfet_01v8 W=10 L=0.15
.control
op
print i(Vn0) i(Vn1) i(Vn2) i(Vn3) i(Vn4) i(Vn5) i(Vn6) i(Vn7)
print @m.xn0.msky130_fd_pr__nfet_01v8[gds] @m.xn1.msky130_fd_pr__nfet_01v8[gds] @m.xn2.msky130_fd_pr__nfet_01v8[gds] @m.xn3.msky130_fd_pr__nfet_01v8[gds]
print @m.xn4.msky130_fd_pr__nfet_01v8[gds] @m.xn5.msky130_fd_pr__nfet_01v8[gds] @m.xn6.msky130_fd_pr__nfet_01v8[gds] @m.xn7.msky130_fd_pr__nfet_01v8[gds]
print @m.xn0.msky130_fd_pr__nfet_01v8[gm] @m.xn1.msky130_fd_pr__nfet_01v8[gm] @m.xn2.msky130_fd_pr__nfet_01v8[gm] @m.xn3.msky130_fd_pr__nfet_01v8[gm]
print @m.xn4.msky130_fd_pr__nfet_01v8[gm] @m.xn5.msky130_fd_pr__nfet_01v8[gm] @m.xn6.msky130_fd_pr__nfet_01v8[gm] @m.xn7.msky130_fd_pr__nfet_01v8[gm]
print i(Vp0) i(Vp1) i(Vp2) i(Vp3) i(Vp4) i(Vp5) i(Vp6) i(Vp7)
print @m.xp0.msky130_fd_pr__pfet_01v8[gds] @m.xp1.msky130_fd_pr__pfet_01v8[gds] @m.xp2.msky130_fd_pr__pfet_01v8[gds] @m.xp3.msky130_fd_pr__pfet_01v8[gds]
print @m.xp4.msky130_fd_pr__pfet_01v8[gds] @m.xp5.msky130_fd_pr__pfet_01v8[gds] @m.xp6.msky130_fd_pr__pfet_01v8[gds] @m.xp7.msky130_fd_pr__pfet_01v8[gds]
.endc
.end
