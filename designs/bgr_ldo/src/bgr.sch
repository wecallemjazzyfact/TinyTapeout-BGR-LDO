v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 4 1 40 -10 {}
N 100 -150 100 -90 {lab=0}
N 310 -150 310 -90 {lab=0}
N 20 -180 60 -180 {lab=0}
N 20 -180 20 -120 {lab=0}
N 20 -120 100 -120 {lab=0}
N 240 -180 270 -180 {lab=0}
N 240 -180 240 -120 {lab=0}
N 240 -120 310 -120 {lab=0}
N 100 -400 100 -210 {lab=#net1}
N -80 -400 100 -400 {lab=#net1}
N -80 -400 -80 -260 {lab=#net1}
N -80 -200 -80 -100 {lab=0}
N 100 -400 300 -400 {lab=#net1}
N 300 -400 310 -400 {lab=#net1}
N 310 -400 310 -210 {lab=#net1}
C {pnp_05v5.sym} 80 -180 0 0 {name=Q1
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} 100 -90 0 0 {name=l1 lab=0}
C {pnp_05v5.sym} 290 -180 0 0 {name=Q2
model=pnp_05v5_W0p68L0p68
m=8
spiceprefix=X
}
C {gnd.sym} 310 -90 0 0 {name=l2 lab=0}
C {isource.sym} -80 -230 2 0 {name=I0 value=1u
}
C {gnd.sym} -80 -100 0 0 {name=l3 lab=0}
