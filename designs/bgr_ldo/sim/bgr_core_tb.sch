v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 4 1 -260 180 {}
P 4 1 -260 180 {}
N -200 40 -200 100 {lab=0}
N -460 -10 -460 90 {lab=0}
N -200 40 -200 100 {lab=0}
N -380 -660 -200 -660 {lab=VAPWR}
N -460 -410 -460 -270 {lab=VAPWR}
N -460 -10 -460 90 {lab=0}
N -200 -90 -200 -20 {lab=VBE1}
N -60 10 -20 10 {lab=0}
N -60 10 -60 70 {lab=0}
N -60 70 20 70 {lab=0}
N -60 10 -20 10 {lab=0}
N -60 10 -60 70 {lab=0}
N -60 70 20 70 {lab=0}
N 20 -90 20 -20 {lab=VBE8}
N 20 40 20 70 {lab=0}
N -200 70 20 70 {lab=0}
N -200 -660 20 -660 {lab=VAPWR}
N 20 -660 20 -600 {lab=VAPWR}
N -460 -270 -460 -70 {lab=VAPWR}
N -460 -660 -380 -660 {lab=VAPWR}
N -330 -20 -330 70 {lab=0}
N -460 70 -200 70 {lab=0}
N -240 10 -240 70 {lab=0}
N -330 -110 -330 -80 {lab=VBE1}
N -330 -110 -200 -110 {lab=VBE1}
N 110 -50 110 -0 {lab=0}
N 110 -0 150 -0 {lab=0}
N 150 -20 150 -0 {lab=0}
N 150 -20 150 -0 {lab=0}
N 150 0 150 70 {lab=0}
N 20 70 150 70 {lab=0}
N 150 -120 150 -80 {lab=#net1}
N -370 -50 -370 -0 {lab=0}
N -370 -0 -330 0 {lab=0}
N 20 -190 150 -190 {lab=#net1}
N 150 -190 150 -120 {lab=#net1}
N -460 -660 -460 -410 {lab=VAPWR}
N -200 -210 -200 -90 {lab=VBE1}
N 20 -190 20 -150 {lab=#net1}
N -200 -260 -200 -210 {lab=VBE1}
N 20 -260 20 -190 {lab=#net1}
N -200 -660 -200 -600 {lab=VAPWR}
N 20 -410 20 -260 {lab=#net1}
N -200 -540 -200 -260 {lab=VBE1}
N 20 -540 20 -410 {lab=#net1}
N -200 -360 -140 -360 {lab=VBE1}
N -140 -320 -140 -190 {lab=#net1}
N -140 -190 20 -190 {lab=#net1}
N -100 -420 -100 -370 {lab=V_ctrl}
N -100 -310 -100 70 {lab=0}
C {pnp_05v5.sym} -220 10 0 0 {name=QA
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -200 100 0 0 {name=l6 lab=0}
C {vsource.sym} -460 -40 0 0 {name=VSource value=3.3 savecurrent=false}
C {code_shown.sym} 420 -910 0 0 {name=SIM_CONTROL only_toplevel=false 
value=".nodeset v(vbe1)=0.88 v(net1)=0.88 v(v_ctrl)=1.5
.param R7_val=180k
.save all
.save @r1[i]
.save @r6[i]
.dc temp -40 125 5

.control
  let r_start = 110k
  let r_stop = 130k
  let r_step = 3k
  let r_curr = r_start

  while r_curr <= r_stop
    alterparam R7_val = $&r_curr
    reset
    nodeset v(vbe1)=0.88 v(net1)=0.88 v(v_ctrl)=1.5
    run
    let r_curr = r_curr + r_step
  end

  plot dc1.@r1[i]+dc1.@r6[i] dc2.@r1[i]+dc2.@r6[i] dc3.@r1[i]+dc3.@r6[i] dc4.@r1[i]+dc4.@r6[i] dc5.@r1[i]+dc5.@r6[i] dc6.@r1[i]+dc6.@r6[i] dc7.@r1[i]+dc7.@r6[i]
.endc"}
C {code.sym} 460 -140 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {gnd.sym} -460 90 0 0 {name=l8 lab=0}
C {lab_pin.sym} -250 -660 0 0 {name=p7 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -200 -70 0 0 {name=p8 sig_type=std_logic lab=VBE1
}
C {pnp_05v5.sym} 0 10 0 0 {name=QB
model=pnp_05v5_W0p68L0p68
m=8
spiceprefix=X
}
C {lab_pin.sym} 20 -60 0 0 {name=p1 sig_type=std_logic lab=VBE8
}
C {res.sym} 20 -120 0 0 {name=R1
value=17.7k
footprint=1206
device=resistor
m=1}
C {res.sym} 150 -50 0 0 {name=R7
value=\{R7_val\}
footprint=1206
device=resistor
m=1}
C {res.sym} -330 -50 0 0 {name=R6
value=\{R7_val\}
footprint=1206
device=resistor
m=1}
C {vcvs.sym} -100 -340 0 0 {name=E1 value=1e5}
C {bsource.sym} -200 -570 0 0 {name=B1 VAR=I FUNC="10u * V(V_ctrl) * u(V(V_ctrl))" m=1}
C {bsource.sym} 20 -570 0 0 {name=B2 VAR=I FUNC="10u * V(V_ctrl) * u(V(V_ctrl))" m=1}
C {lab_pin.sym} -100 -410 0 0 {name=p2 sig_type=std_logic lab=V_ctrl
}
