.title Ron worst-case  nfet_01v8 W=10 L=0.15 m=18  VS=0.159  ss/125
.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice ss
.temp 125
Vd1 d1 0 0.209
Vg1 g1 0 1.8
Vs1 s1 0 0.159
Vb1 b1 0 0
XM1 d1 g1 s1 b1 sky130_fd_pr__nfet_01v8 W=10 L=0.15 nf=1 m=18
.control
op
print i(Vd1)
.endc
.end
