v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
P 4 1 -190 150 {}
P 4 1 -190 150 {}
P 4 1 -190 150 {}
P 4 1 -190 150 {}
N -130 10 -130 70 {lab=0}
N -210 -20 -170 -20 {lab=0}
N -210 -20 -210 40 {lab=0}
N -210 40 -130 40 {lab=0}
N -310 -240 -130 -240 {lab=VAPWR}
N -310 -240 -310 -100 {lab=VAPWR}
N -310 -40 -310 60 {lab=0}
N -130 -240 -130 -180 {lab=VAPWR}
N -130 -120 -130 -50 {lab=VBE}
N -310 50 -130 50 {lab=0}
N -130 10 -130 70 {lab=0}
N -210 -20 -170 -20 {lab=0}
N -210 -20 -210 40 {lab=0}
N -210 40 -130 40 {lab=0}
N -310 -240 -130 -240 {lab=VAPWR}
N -310 -240 -310 -100 {lab=VAPWR}
N -310 -40 -310 60 {lab=0}
N -130 -240 -130 -180 {lab=VAPWR}
N -130 -120 -130 -50 {lab=VBE}
N -310 50 -130 50 {lab=0}
N -130 10 -130 70 {lab=0}
N -210 -20 -170 -20 {lab=0}
N -210 -20 -210 40 {lab=0}
N -210 40 -130 40 {lab=0}
N -310 -240 -130 -240 {lab=VAPWR}
N -310 -240 -310 -100 {lab=VAPWR}
N -310 -40 -310 60 {lab=0}
N -130 -240 -130 -180 {lab=VAPWR}
N -130 -120 -130 -50 {lab=VBE}
N -310 50 -130 50 {lab=0}
N -130 10 -130 70 {lab=0}
N -210 -20 -170 -20 {lab=0}
N -210 -20 -210 40 {lab=0}
N -210 40 -130 40 {lab=0}
N -310 -240 -130 -240 {lab=VAPWR}
N -310 -240 -310 -100 {lab=VAPWR}
N -310 -40 -310 60 {lab=0}
N -130 -240 -130 -180 {lab=VAPWR}
N -130 -120 -130 -50 {lab=VBE}
N -310 50 -130 50 {lab=0}
C {pnp_05v5.sym} -150 -20 0 0 {name=Q1
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -130 70 0 0 {name=l1 lab=0}
C {gnd.sym} -310 60 0 0 {name=l3 lab=0}
C {vsource.sym} -310 -70 0 0 {name=V1 value=3.3 savecurrent=false}
C {isource.sym} -130 -150 0 0 {name=I0 value=3u
}
C {lab_pin.sym} -180 -240 0 0 {name=p1 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -130 -90 0 0 {name=p2 sig_type=std_logic lab=VBE}
C {code_shown.sym} 60 -130 0 0 {name=SIM_CONTROL only_toplevel=false 
value=".dc I0 1u 10u 0.1u
.dc temp -40 125 5
.control
  run
  write pnp_vbe.raw
  meas dc vbe_val find v(vbe) when i-sweep=3u
  plot v(vbe)
.endc"
}
C {code.sym} 220 -170 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {pnp_05v5.sym} -150 -20 0 0 {name=Q2
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -130 70 0 0 {name=l2 lab=0}
C {gnd.sym} -310 60 0 0 {name=l4 lab=0}
C {vsource.sym} -310 -70 0 0 {name=V2 value=3.3 savecurrent=false}
C {isource.sym} -130 -150 0 0 {name=I1 value=3u
}
C {lab_pin.sym} -180 -240 0 0 {name=p3 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -130 -90 0 0 {name=p4 sig_type=std_logic lab=VBE}
C {code_shown.sym} 60 -130 0 0 {name=SIM_CONTROL1 only_toplevel=false 
value=".dc I0 1u 10u 0.1u
.dc temp -40 125 5
.control
  run
  write pnp_vbe.raw
  meas dc vbe_val find v(vbe) when i-sweep=3u
  plot v(vbe)
.endc"
}
C {code.sym} 220 -170 0 0 {
name=TT_MODELS1
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {pnp_05v5.sym} -150 -20 0 0 {name=Q3
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -130 70 0 0 {name=l5 lab=0}
C {gnd.sym} -310 60 0 0 {name=l6 lab=0}
C {vsource.sym} -310 -70 0 0 {name=V3 value=3.3 savecurrent=false}
C {isource.sym} -130 -150 0 0 {name=I2 value=3u
}
C {lab_pin.sym} -180 -240 0 0 {name=p5 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -130 -90 0 0 {name=p6 sig_type=std_logic lab=VBE}
C {code_shown.sym} 60 -130 0 0 {name=SIM_CONTROL2 only_toplevel=false 
value=".dc I0 1u 10u 0.1u
.dc temp -40 125 5
.control
  run
  write pnp_vbe.raw
  meas dc vbe_val find v(vbe) when i-sweep=3u
  plot v(vbe)
.endc"
}
C {code.sym} 220 -170 0 0 {
name=TT_MODELS2
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {pnp_05v5.sym} -150 -20 0 0 {name=Q4
model=pnp_05v5_W0p68L0p68
m=1
spiceprefix=X
}
C {gnd.sym} -130 70 0 0 {name=l7 lab=0}
C {gnd.sym} -310 60 0 0 {name=l8 lab=0}
C {vsource.sym} -310 -70 0 0 {name=V4 value=3.3 savecurrent=false}
C {isource.sym} -130 -150 0 0 {name=I3 value=3u
}
C {lab_pin.sym} -180 -240 0 0 {name=p7 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} -130 -90 0 0 {name=p8 sig_type=std_logic lab=VBE}
C {code_shown.sym} 60 -130 0 0 {name=SIM_CONTROL3 only_toplevel=false 
value=".dc I0 1u 10u 0.1u
.dc temp -40 125 5
.control
  run
  write pnp_vbe.raw
  meas dc vbe_val find v(vbe) when i-sweep=3u
  plot v(vbe)
.endc"
}
C {code.sym} 220 -170 0 0 {
name=TT_MODELS3
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
