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
N -300 20 -300 80 {lab=0}
N -300 -350 -300 -40 {lab=VAPWR}
N -300 90 440 90 {lab=0}
N -300 80 -300 90 {lab=0}
N 200 -210 400 -210 {lab=#net2}
N 110 -350 110 -290 {lab=VAPWR}
N -80 -190 20 -190 {lab=#net3}
N -140 -230 -140 -30 {lab=#net4}
N -140 -230 20 -230 {lab=#net4}
N 640 90 650 90 {lab=0}
N 650 -10 650 90 {lab=0}
N 650 -150 650 -70 {lab=VDDC}
N 390 -150 440 -150 {lab=VDDC}
N 310 -150 330 -150 {lab=#net5}
N 230 -150 250 -150 {lab=#net2}
N 230 -210 230 -150 {lab=#net2}
N 20 -150 20 -130 {lab=#net6}
N 20 -70 70 -70 {lab=VAPWR}
N -140 -30 50 -30 {lab=#net4}
N 110 -30 190 -30 {lab=#net7}
N 250 -30 440 -30 {lab=#net1}
N 150 70 150 90 {lab=0}
N 150 -30 150 10 {lab=#net7}
N 280 -130 280 -60 {lab=0}
N 400 -90 420 -90 {lab=0}
N 400 -90 400 20 {lab=0}
N 400 20 420 20 {lab=0}
N 400 20 400 90 {lab=0}
N 280 -60 400 -60 {lab=0}
C {vsource.sym} -80 -160 0 0 {name=Vref value=1.2 savecurrent=false}
C {pfet_g5v0d10v5.sym} 420 -210 0 0 {name=XM_top2
W=10
L=0.5
nf=1
mult=40
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
C {gnd.sym} 440 140 0 0 {name=l1 lab=0}
C {lab_pin.sym} 650 -150 2 0 {name=p1 sig_type=std_logic lab=VDDC


}
C {ea_fc.sym} 100 -210 0 0 {name=x1}
C {gnd.sym} 110 -130 0 0 {name=l2 lab=0}
C {gnd.sym} -80 -130 0 0 {name=l3 lab=0}
C {isource.sym} 650 -40 0 0 {name=Iload value=1n}
C {isource.sym} 20 -100 2 0 {name=I0 value=2.564228u}
C {lab_pin.sym} 70 -70 2 0 {name=p2 sig_type=std_logic lab=VAPWR


}
C {res_high_po_0p69.sym} 440 -90 0 0 {name=RF1
L=26.5447
model=res_high_po_0p69
spiceprefix=X
mult=1}
C {res_high_po_0p69.sym} 440 20 0 0 {name=RF2
L=54.2057
model=res_high_po_0p69
spiceprefix=X
mult=1}
C {res_high_po_0p69.sym} 280 -150 1 1 {name=Rz
L=15.4804
model=res_high_po_0p69
spiceprefix=X
mult=1}
C {cap_mim_m3_1.sym} 550 -40 0 0 {name=Cload model=cap_mim_m3_1 W=18.3147 L=18.3147 MF=44 spiceprefix=X}
C {cap_mim_m3_1.sym} 360 -150 3 0 {name=Cc model=cap_mim_m3_1 W=18.3147 L=18.3147 MF=4 spiceprefix=X}
C {vsource.sym} 220 -30 3 0 {name=Vprb1 value=0 savecurrent=false}
C {vsource.sym} 80 -30 3 0 {name=Vprb2 value=0 savecurrent=false}
C {isource.sym} 150 40 0 0 {name=Iprb value=0}
