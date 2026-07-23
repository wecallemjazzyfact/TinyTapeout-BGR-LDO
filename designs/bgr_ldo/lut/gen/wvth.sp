.title thin-ox Vth vs W   L=0.15 / 2.0, VGS=VDS=0.9, tt/27
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.temp 27
Vgn gn 0 0.9
Vdn dn 0 0.9
Vgp gp 0 -0.9
Vdp dp 0 -0.9
XN1 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=0.42 L=0.15
XN2 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=1 L=0.15
XN3 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=2 L=0.15
XN4 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=5 L=0.15
XN5 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=10 L=0.15
XN6 dn gn 0 0 sky130_fd_pr__nfet_01v8 W=10 L=2
XP1 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=0.42 L=0.15
XP2 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=1 L=0.15
XP3 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=2 L=0.15
XP4 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=5 L=0.15
XP5 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=10 L=0.15
XP6 dp gp 0 0 sky130_fd_pr__pfet_01v8 W=10 L=2
.control
op
print @m.xn1.msky130_fd_pr__nfet_01v8[vth]
print @m.xn2.msky130_fd_pr__nfet_01v8[vth]
print @m.xn3.msky130_fd_pr__nfet_01v8[vth]
print @m.xn4.msky130_fd_pr__nfet_01v8[vth]
print @m.xn5.msky130_fd_pr__nfet_01v8[vth]
print @m.xn6.msky130_fd_pr__nfet_01v8[vth]
print @m.xp1.msky130_fd_pr__pfet_01v8[vth]
print @m.xp2.msky130_fd_pr__pfet_01v8[vth]
print @m.xp3.msky130_fd_pr__pfet_01v8[vth]
print @m.xp4.msky130_fd_pr__pfet_01v8[vth]
print @m.xp5.msky130_fd_pr__pfet_01v8[vth]
print @m.xp6.msky130_fd_pr__pfet_01v8[vth]
.endc
.end
