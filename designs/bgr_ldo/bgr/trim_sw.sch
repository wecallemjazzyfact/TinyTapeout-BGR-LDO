v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 180 -90 180 -30 {lab=SEG0A}
N 100 0 140 0 {lab=TRIM0}
N -20 -90 -20 -30 {lab=SEG1A}
N -100 0 -60 0 {lab=TRIM1}
N -230 -90 -230 -30 {lab=SEG2A}
N -310 0 -270 0 {lab=TRIM2}
N -430 -90 -430 -30 {lab=SEG3A}
N -510 0 -470 0 {lab=TRIM3}
N 180 30 180 90 {lab=SEG0B}
N -20 30 -20 90 {lab=SEG1B}
N -230 30 -230 90 {lab=SEG2B}
N -430 30 -430 90 {lab=SEG3B}
N -120 -200 -120 -10 {lab=VGND}
N 20 -180 20 -10 {lab=VGND}
N -120 -180 20 -180 {lab=VGND}
N 20 -180 230 -180 {lab=VGND}
N 230 -180 230 -10 {lab=VGND}
N -360 -180 -360 -10 {lab=VGND}
N -360 -180 -120 -180 {lab=VGND}
N 180 0 230 0 {lab=VGND}
N 230 -10 230 0 {lab=VGND}
N -430 0 -360 0 {lab=VGND}
N -360 -10 -360 0 {lab=VGND}
N -230 -0 -120 0 {lab=VGND}
N -120 -10 -120 -0 {lab=VGND}
N -20 -0 20 0 {lab=VGND}
N 20 -10 20 0 {lab=VGND}
C {ipin.sym} 100 0 0 0 {name=p9 lab=TRIM0}
C {ipin.sym} -100 0 0 0 {name=p10 lab=TRIM1}
C {ipin.sym} -310 0 0 0 {name=p11 lab=TRIM2}
C {ipin.sym} -510 0 0 0 {name=p12 lab=TRIM3}
C {iopin.sym} 180 -90 3 0 {name=p1 lab=SEG0A}
C {iopin.sym} 180 90 1 0 {name=p2 lab=SEG0B}
C {iopin.sym} -20 -90 3 0 {name=p3 lab=SEG1A}
C {iopin.sym} -230 -90 3 0 {name=p4 lab=SEG2A}
C {iopin.sym} -430 -90 3 0 {name=p5 lab=SEG3A}
C {iopin.sym} -20 90 1 0 {name=p6 lab=SEG1B}
C {iopin.sym} -230 90 1 0 {name=p7 lab=SEG2B}
C {iopin.sym} -430 90 1 0 {name=p8 lab=SEG3B}
C {iopin.sym} -120 -200 3 0 {name=p13 lab=VGND
}
C {nfet_01v8.sym} 160 0 0 0 {name=SWb0
W=10
L=0.15
nf=1 
mult=22
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {nfet_01v8.sym} -40 0 0 0 {name=SWb1
W=10
L=0.15
nf=1 
mult=22
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {nfet_01v8.sym} -250 0 0 0 {name=SWb2
W=10
L=0.15
nf=1 
mult=22
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {nfet_01v8.sym} -450 0 0 0 {name=SWb3
W=10
L=0.15
nf=1 
mult=22
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
