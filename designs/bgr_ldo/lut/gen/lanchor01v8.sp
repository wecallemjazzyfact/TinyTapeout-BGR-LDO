.title thin-ox L-axis anchors  W=1, VGS=VDS=0.9, VSB=0, tt/27
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
XN0 n0 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XN1 n1 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.18
XN2 n2 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.25
XN3 n3 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.5
XN4 n4 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=1
XN5 n5 gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=2
Vp0 p0 dcp 0
Vp1 p1 dcp 0
Vp2 p2 dcp 0
Vp3 p3 dcp 0
Vp4 p4 dcp 0
Vp5 p5 dcp 0
XP0 p0 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.15
XP1 p1 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.18
XP2 p2 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.25
XP3 p3 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.5
XP4 p4 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=1
XP5 p5 gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=2
.control
op
print i(Vn0)
print i(Vn1)
print i(Vn2)
print i(Vn3)
print i(Vn4)
print i(Vn5)
print i(Vp0)
print i(Vp1)
print i(Vp2)
print i(Vp3)
print i(Vp4)
print i(Vp5)
.endc
.end
