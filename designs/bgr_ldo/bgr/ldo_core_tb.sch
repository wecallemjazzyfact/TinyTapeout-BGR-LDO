v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -300 -350 440 -350 {lab=VAPWR}
N 440 -350 440 -240 {lab=VAPWR}
N 440 -210 490 -210 {lab=VAPWR}
N 490 -270 490 -210 {lab=VAPWR}
N 440 -270 490 -270 {lab=VAPWR}
N 440 -180 440 -120 {lab=VDDC}
N 440 -60 440 -10 {lab=#net1}
N 440 50 440 140 {lab=0}
N 440 90 640 90 {lab=0}
N 440 -150 650 -150 {lab=VDDC}
N 550 -150 550 -70 {lab=VDDC}
N 550 -10 550 90 {lab=0}
N -300 80 440 90 {lab=0}
N -300 20 -300 80 {lab=0}
N -300 -350 -300 -40 {lab=VAPWR}
C {vsource.sym} -80 -230 0 0 {name=Vref value=1.2 savecurrent=false}
C {pfet_g5v0d10v5.sym} 420 -210 0 0 {name=XM_top2
W=100
L=0.5
nf=1
mult=4
ad="expr('int((@nf + 1)/2) * @W / @nf * 0.29')"
pd="expr('2*int((@nf + 1)/2) * (@W / @nf + 0.29)')"
as="expr('int((@nf + 2)/2) * @W / @nf * 0.29')"
ps="expr('2*int((@nf + 2)/2) * (@W / @nf + 0.29)')"
nrd="expr('0.29 / @W ')" nrs="expr('0.29 / @W ')"
sa=0 sb=0 sd=0
model=pfet_g5v0d10v5
spiceprefix=X
}
C {vsource.sym} -300 -10 0 0 {name=VSource value=3.3 savecurrent=false}
C {lab_pin.sym} 240 -350 0 0 {name=p12 sig_type=std_logic lab=VAPWR


}
C {res.sym} 440 -90 0 0 {name=RF1
value=1k
footprint=1206
device=resistor
m=1}
C {res.sym} 440 20 0 0 {name=RF2
value=1k
footprint=1206
device=resistor
m=1}
C {gnd.sym} 440 140 0 0 {name=l1 lab=0}
C {capa.sym} 550 -40 0 0 {name=C1
m=1
value=50f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 440 -150 0 0 {name=p1 sig_type=std_logic lab=VDDC


}
