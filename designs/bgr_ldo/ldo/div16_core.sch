v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -160 -10 -90 -10 {lab=CK_IN}
N 90 10 120 10 {lab=#net1}
N 120 10 120 80 {lab=#net1}
N -120 80 120 80 {lab=#net1}
N -120 10 -120 80 {lab=#net1}
N -120 10 -90 10 {lab=#net1}
N 90 -10 160 -10 {lab=#net2}
N 340 10 370 10 {lab=#net3}
N 370 10 370 80 {lab=#net3}
N 130 80 370 80 {lab=#net3}
N 130 10 130 80 {lab=#net3}
N 130 10 160 10 {lab=#net3}
N 340 -10 410 -10 {lab=#net4}
N 590 10 620 10 {lab=#net5}
N 620 10 620 80 {lab=#net5}
N 380 80 620 80 {lab=#net5}
N 380 10 380 80 {lab=#net5}
N 380 10 410 10 {lab=#net5}
N 590 -10 660 -10 {lab=#net6}
N 840 10 870 10 {lab=#net7}
N 870 10 870 80 {lab=#net7}
N 630 80 870 80 {lab=#net7}
N 630 10 630 80 {lab=#net7}
N 630 10 660 10 {lab=#net7}
N 840 -10 910 -10 {lab=DIV_OUT}
C {dfxbp_1.sym} 0 0 0 0 {name=x1 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__ }
C {ipin.sym} -160 -10 0 0 {name=p1 lab=CK_IN}
C {opin.sym} 910 -10 0 0 {name=p2 lab=DIV_OUT}
C {dfxbp_1.sym} 250 0 0 0 {name=x2 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__ }
C {dfxbp_1.sym} 500 0 0 0 {name=x3 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__ }
C {dfxbp_1.sym} 750 0 0 0 {name=x4 VGND=VGND VNB=VGND VPB=VDPWR VPWR=VDPWR prefix=sky130_fd_sc_hd__ }
C {iopin.sym} 200 -100 0 0 {name=p3 lab=VDPWR}
C {iopin.sym} 200 -60 0 0 {name=p4 lab=VGND}
