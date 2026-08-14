v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 10 -30 10 30 {lab=Y}
N 10 190 10 220 {lab=VGND}
N 10 0 80 0 {lab=Y}
N 10 -60 50 -60 {lab=VDDC}
N 50 -110 50 -60 {lab=VDDC}
N 50 -120 50 -110 {lab=VDDC}
N 80 0 140 0 {lab=Y}
N -70 -60 -30 -60 {lab=B}
N -230 -120 -230 -90 {lab=VDDC}
N -230 -60 -190 -60 {lab=VDDC}
N -190 -120 -190 -60 {lab=VDDC}
N 10 -120 10 -90 {lab=VDDC}
N -230 -120 50 -120 {lab=VDDC}
N -310 -60 -270 -60 {lab=A}
N -290 -60 -290 60 {lab=A}
N 10 90 10 130 {lab=n_nandmid}
N -230 0 10 -0 {lab=Y}
N -230 -30 -230 0 {lab=Y}
N -50 -60 -50 160 {lab=B}
N -50 160 -30 160 {lab=B}
N -290 60 -30 60 {lab=A}
N 10 160 60 160 {lab=VGND}
N 60 160 60 200 {lab=VGND}
N 10 200 60 200 {lab=VGND}
N 10 60 60 60 {lab=VGND}
N 60 60 60 160 {lab=VGND}
C {pfet_01v8.sym} -10 -60 0 0 {name=MP1
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {iopin.sym} -80 -120 3 0 {name=p1 lab=VDDC}
C {iopin.sym} 10 220 1 0 {name=p2 lab=VGND}
C {ipin.sym} -310 -60 0 0 {name=p3 lab=A}
C {opin.sym} 140 0 0 0 {name=p4 lab=Y}
C {pfet_01v8.sym} -250 -60 0 0 {name=MP2
W=1
L=0.15
nf=1
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {ipin.sym} -70 -60 0 0 {name=p5 lab=B}
C {nfet_01v8.sym} -10 60 0 0 {name=MN1
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {nfet_01v8.sym} -10 160 0 0 {name=MN2
W=1
L=0.15
nf=1 
mult=1
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {lab_pin.sym} 10 110 0 0 {name=p6 sig_type=std_logic lab=n_nandmid}
