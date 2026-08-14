v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 100 -120 100 -70 {lab=VDDC}
N 100 70 100 120 {lab=VGND}
N 220 -0 220 30 {lab=#net1}
N 220 90 220 120 {lab=VGND}
N 320 -120 320 -70 {lab=VDDC}
N 320 70 320 120 {lab=VGND}
N 440 0 440 30 {lab=#net2}
N 440 90 440 120 {lab=VGND}
N 540 -120 540 -70 {lab=VDDC}
N 540 70 540 120 {lab=VGND}
N 660 0 660 30 {lab=#net3}
N 660 90 660 120 {lab=VGND}
N 760 -120 760 -70 {lab=VDDC}
N 760 70 760 120 {lab=VGND}
N 880 0 880 30 {lab=#net4}
N 880 90 880 120 {lab=VGND}
N -120 0 0 -0 {lab=#net5}
N -390 -20 -390 240 {lab=#net4}
N -390 -20 -300 -20 {lab=#net4}
N -340 20 -300 20 {lab=RO_EN}
N -230 120 -20 120 {lab=VGND}
N -230 50 -230 120 {lab=VGND}
N -230 -120 -230 -50 {lab=VDDC}
N -550 120 -550 170 {lab=VGND}
N -430 440 -360 440 {lab=RO_OUT}
N -550 120 -230 120 {lab=VGND}
N -670 440 -650 440 {lab=#net6}
N -450 240 -390 240 {lab=#net4}
N -550 510 -550 540 {lab=VGND}
N -550 310 -550 370 {lab=VDDC}
N -670 240 -670 440 {lab=#net6}
N -60 90 -60 120 {lab=VGND}
N -60 0 -60 30 {lab=#net5}
N -230 -120 760 -120 {lab=VDDC}
N -20 120 660 120 {lab=VGND}
N 660 120 880 120 {lab=VGND}
N 880 -0 1000 -0 {lab=#net4}
N -390 240 1000 240 {lab=#net4}
N 1000 0 1000 240 {lab=#net4}
C {ro_inv.sym} 100 0 0 0 {name=x1}
C {ro_nand.sym} -230 0 0 0 {name=x0}
C {cap_mim_m3_1.sym} 220 60 0 0 {name=C1 model=cap_mim_m3_1 W=4.27 L=4.27 MF=1 spiceprefix=X}
C {ro_inv.sym} 320 0 0 0 {name=x2}
C {cap_mim_m3_1.sym} 440 60 0 0 {name=C2 model=cap_mim_m3_1 W=4.27 L=4.27 MF=1 spiceprefix=X}
C {ro_inv.sym} 540 0 0 0 {name=x3}
C {cap_mim_m3_1.sym} 660 60 0 0 {name=C3 model=cap_mim_m3_1 W=4.27 L=4.27 MF=1 spiceprefix=X}
C {cap_mim_m3_1.sym} 880 60 0 0 {name=C4 model=cap_mim_m3_1 W=4.27 L=4.27 MF=1 spiceprefix=X}
C {ro_inv.sym} -550 240 2 0 {name=xB1}
C {ro_inv.sym} -550 440 0 0 {name=xB2}
C {iopin.sym} -60 -120 3 0 {name=p1 lab=VDDC}
C {iopin.sym} -170 120 3 0 {name=p3 lab=VGND}
C {lab_pin.sym} -550 540 2 0 {name=p4 sig_type=std_logic lab=VGND}
C {opin.sym} -360 440 0 0 {name=p5 lab=RO_OUT}
C {cap_mim_m3_1.sym} -60 60 0 0 {name=C5 model=cap_mim_m3_1 W=4.27 L=4.27 MF=1 spiceprefix=X}
C {ipin.sym} -340 20 0 0 {name=p6 lab=RO_EN}
C {ro_inv.sym} 760 0 0 0 {name=x4}
C {lab_pin.sym} -550 340 2 0 {name=p2 sig_type=std_logic lab=VDDC}
