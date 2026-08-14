v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 0 -30 0 30 {lab=Y}
N 0 90 0 120 {lab=VGND}
N -50 -60 -40 -60 {lab=A}
N -50 -60 -50 60 {lab=A}
N -50 60 -40 60 {lab=A}
N -90 0 -50 0 {lab=A}
N 0 0 70 0 {lab=Y}
N 0 -60 40 -60 {lab=VDDC}
N 40 -110 40 -60 {lab=VDDC}
N 40 -120 40 -110 {lab=VDDC}
N 0 -120 40 -120 {lab=VDDC}
N 0 -170 0 -90 {lab=VDDC}
N 70 0 130 0 {lab=Y}
N -160 0 -90 0 {lab=A}
C {nfet3_01v8.sym} -20 60 0 0 {name=MN
W=0.42
L=0.15
body=GND
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
C {pfet_01v8.sym} -20 -60 0 0 {name=MP
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
C {iopin.sym} 0 -170 3 0 {name=p1 lab=VDDC}
C {iopin.sym} 0 120 1 0 {name=p2 lab=VGND}
C {ipin.sym} -160 0 0 0 {name=p3 lab=A}
C {opin.sym} 130 0 0 0 {name=p4 lab=Y}
