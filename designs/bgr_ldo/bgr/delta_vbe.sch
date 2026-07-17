v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 4 1 -270 160 {}
P 4 1 -270 160 {}
N -210 20 -210 80 {lab=0}
N -290 -10 -250 -10 {lab=0}
N -290 -10 -290 50 {lab=0}
N -290 50 -210 50 {lab=0}
N -390 -230 -210 -230 {lab=VAPWR}
N -390 -230 -390 -90 {lab=VAPWR}
N -390 -30 -390 70 {lab=0}
N -210 -230 -210 -170 {lab=VAPWR}
N -210 -110 -210 -40 {lab=VBE1}
N -390 60 -210 60 {lab=0}
N -210 20 -210 80 {lab=0}
N -290 -10 -250 -10 {lab=0}
N -290 -10 -290 50 {lab=0}
N -290 50 -210 50 {lab=0}
N -390 -230 -210 -230 {lab=VAPWR}
N -390 -230 -390 -90 {lab=VAPWR}
N -390 -30 -390 70 {lab=0}
N -210 -230 -210 -170 {lab=VAPWR}
N -210 -110 -210 -40 {lab=VBE1}
N -390 60 -210 60 {lab=0}
N -70 -10 -30 -10 {lab=0}
N -70 -10 -70 50 {lab=0}
N -70 50 10 50 {lab=0}
N 10 -110 10 -40 {lab=VBE8}
N -70 -10 -30 -10 {lab=0}
N -70 -10 -70 50 {lab=0}
N -70 50 10 50 {lab=0}
N 10 -110 10 -40 {lab=VBE8}
N 10 20 10 50 {lab=0}
N -210 50 10 50 {lab=0}
N -210 -230 10 -230 {lab=VAPWR}
N 10 -230 10 -170 {lab=VAPWR}
C {pnp_05v5.sym} -230 -10 0 0 {name=QA
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -210 80 0 0 {name=l6 lab=0}
C {vsource.sym} -390 -60 0 0 {name=VSource value=3.3 savecurrent=false}
C {isource.sym} -210 -140 0 0 {name=I0 value=3u
}
C {code_shown.sym} 100 -400 0 0 {name=SIM_CONTROL only_toplevel=false 
value=".dc temp -40 125 5
.control
  run
  write delta_vbe.raw

  let delta_vbe = v(vbe1) - v(vbe8)
  meas dc dvbe_27 find delta_vbe when temp=27

  plot delta_vbe
.endc"}
C {code.sym} 450 -160 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {gnd.sym} -390 70 0 0 {name=l8 lab=0}
C {lab_pin.sym} -260 -230 0 0 {name=p7 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -210 -90 0 0 {name=p8 sig_type=std_logic lab=VBE1
}
C {pnp_05v5.sym} -10 -10 0 0 {name=QB
model=pnp_05v5_W0p68L0p68
m=8
spiceprefix=X
}
C {isource.sym} 10 -140 0 0 {name=I1 value=3u
}
C {lab_pin.sym} 10 -80 0 0 {name=p1 sig_type=std_logic lab=VBE8
}
