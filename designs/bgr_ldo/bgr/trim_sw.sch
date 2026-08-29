v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 400 -90 400 -30 {lab=SEG0A}
N 320 0 360 0 {lab=TRIM0}
N -20 -90 -20 -30 {lab=SEG2A}
N -100 0 -60 0 {lab=TRIM2}
N -230 -90 -230 -30 {lab=SEG3A}
N -310 0 -270 0 {lab=TRIM3}
N -430 -90 -430 -30 {lab=SEG4A}
N -510 0 -470 0 {lab=TRIM4}
N 400 30 400 90 {lab=SEG0B}
N -20 30 -20 90 {lab=SEG2B}
N -230 30 -230 90 {lab=SEG3B}
N -430 30 -430 90 {lab=SEG4B}
N -120 -200 -120 -10 {lab=VGND}
N 20 -180 20 -10 {lab=VGND}
N -120 -180 20 -180 {lab=VGND}
N 20 -180 230 -180 {lab=VGND}
N 450 -180 450 -10 {lab=VGND}
N -360 -180 -360 -10 {lab=VGND}
N -360 -180 -120 -180 {lab=VGND}
N 400 0 450 0 {lab=VGND}
N 450 -10 450 0 {lab=VGND}
N -430 0 -360 0 {lab=VGND}
N -360 -10 -360 0 {lab=VGND}
N -230 -0 -120 0 {lab=VGND}
N -120 -10 -120 -0 {lab=VGND}
N -20 -0 20 0 {lab=VGND}
N 20 -10 20 0 {lab=VGND}
N 180 -90 180 -30 {lab=SEG1A}
N 100 0 140 0 {lab=TRIM1}
N 180 30 180 90 {lab=SEG1B}
N -690 -90 -690 -30 {lab=SEG5A}
N -770 0 -730 0 {lab=TRIM5}
N -690 30 -690 90 {lab=SEG5B}
N 180 -0 230 -0 {lab=VGND}
N 230 -180 230 -0 {lab=VGND}
N 230 -180 450 -180 {lab=VGND}
N -600 -180 -360 -180 {lab=VGND}
N -600 -180 -600 -0 {lab=VGND}
N -690 0 -600 -0 {lab=VGND}
C {ipin.sym} 320 0 0 0 {name=p9 lab=TRIM0}
C {ipin.sym} -100 0 0 0 {name=p10 lab=TRIM2}
C {ipin.sym} -310 0 0 0 {name=p11 lab=TRIM3}
C {ipin.sym} -510 0 0 0 {name=p12 lab=TRIM4}
C {iopin.sym} 400 -90 3 0 {name=p1 lab=SEG0A}
C {iopin.sym} 400 90 1 0 {name=p2 lab=SEG0B}
C {iopin.sym} -20 -90 3 0 {name=p3 lab=SEG2A}
C {iopin.sym} -230 -90 3 0 {name=p4 lab=SEG3A}
C {iopin.sym} -430 -90 3 0 {name=p5 lab=SEG4A}
C {iopin.sym} -20 90 1 0 {name=p6 lab=SEG2B}
C {iopin.sym} -230 90 1 0 {name=p7 lab=SEG3B}
C {iopin.sym} -430 90 1 0 {name=p8 lab=SEG4B}
C {iopin.sym} -120 -200 3 0 {name=p13 lab=VGND
}
C {nfet_01v8.sym} 380 0 0 0 {name=SWb0
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
C {nfet_01v8.sym} -40 0 0 0 {name=SWb2
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
C {nfet_01v8.sym} -250 0 0 0 {name=SWb3
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
C {nfet_01v8.sym} -450 0 0 0 {name=SWb4
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
C {ipin.sym} 100 0 0 0 {name=p14 lab=TRIM1}
C {iopin.sym} 180 -90 3 0 {name=p15 lab=SEG1A}
C {iopin.sym} 180 90 1 0 {name=p16 lab=SEG1B}
C {nfet_01v8.sym} 160 0 0 0 {name=SWb1
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
C {ipin.sym} -770 0 0 0 {name=p17 lab=TRIM5
}
C {iopin.sym} -690 -90 3 0 {name=p18 lab=SEG5A}
C {iopin.sym} -690 90 1 0 {name=p19 lab=SEG5B}
C {nfet_01v8.sym} -710 0 0 0 {name=SWb5
W=10
L=0.15
nf=1 
mult=6
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
