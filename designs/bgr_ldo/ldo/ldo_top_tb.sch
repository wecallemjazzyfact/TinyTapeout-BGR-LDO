v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -20 -130 -20 -80 {lab=VAPWR}
N -20 -130 340 -130 {lab=VAPWR}
N 340 -130 340 -40 {lab=VAPWR}
N 20 -110 20 -80 {lab=VDPWR}
N 20 -110 300 -110 {lab=VDPWR}
N 300 -110 300 -40 {lab=VDPWR}
N 300 20 300 100 {lab=0}
N -0 100 300 100 {lab=0}
N 340 20 340 100 {lab=0}
N 300 100 340 100 {lab=0}
N -180 70 -150 70 {lab=#net1}
N -180 130 -180 150 {lab=0}
N -250 130 -250 150 {lab=0}
N -440 110 -440 130 {lab=0}
N -510 110 -510 130 {lab=0}
N -590 110 -590 130 {lab=0}
N -660 110 -660 130 {lab=0}
N -660 130 -560 130 {lab=0}
N -440 10 -440 50 {lab=#net2}
N -360 -30 -150 -30 {lab=#net3}
N -510 -10 -510 50 {lab=#net3}
N -440 -50 -150 -50 {lab=#net4}
N -590 -30 -590 50 {lab=#net4}
N -660 -50 -660 50 {lab=#net5}
N 150 20 210 20 {lab=DIV_OUT}
N 150 0 210 0 {lab=VDDC}
N 150 -20 210 -20 {lab=VREF_LOW}
N -560 130 -440 130 {lab=0}
N -660 -70 -150 -70 {lab=#net5}
N -660 -70 -660 -50 {lab=#net5}
N -590 -50 -440 -50 {lab=#net4}
N -590 -50 -590 -30 {lab=#net4}
N -510 -30 -360 -30 {lab=#net3}
N -510 -30 -510 -10 {lab=#net3}
N -440 -10 -150 -10 {lab=#net2}
N -440 -10 -440 10 {lab=#net2}
N -360 110 -360 130 {lab=0}
N -360 10 -360 50 {lab=#net6}
N -440 130 -320 130 {lab=0}
N -360 10 -150 10 {lab=#net6}
N -290 30 -150 30 {lab=#net7}
N -290 30 -290 50 {lab=#net7}
N -320 130 -290 130 {lab=0}
N -290 110 -290 130 {lab=0}
N -290 130 -290 150 {lab=0}
N -290 150 -30 150 {lab=0}
N -30 100 -30 150 {lab=0}
N -30 100 -0 100 {lab=0}
N 0 100 0 140 {lab=0}
N -250 50 -150 50 {lab=#net8}
N -250 50 -250 70 {lab=#net8}
C {gnd.sym} 0 140 0 0 {name=l1 lab=0}
C {vsource.sym} 340 -10 0 0 {name=VAPWR value=3.3 savecurrent=false}
C {vsource.sym} 300 -10 0 0 {name=VDPWR value=1.8 savecurrent=false}
C {lab_pin.sym} 340 -100 0 1 {name=p1 sig_type=std_logic lab=VAPWR}
C {lab_pin.sym} 300 -100 2 1 {name=p2 sig_type=std_logic lab=VDPWR}
C {vsource.sym} -180 100 0 0 {name=VRO_EN value=1.8 savecurrent=false}
C {vsource.sym} -250 100 0 0 {name=VSNK_EN value=1.8 savecurrent=false}
C {vsource.sym} -440 80 0 0 {name=VTRIM3 value=1.8 savecurrent=false}
C {vsource.sym} -510 80 0 0 {name=VTRIM2 value=1.8 savecurrent=false}
C {vsource.sym} -590 80 0 0 {name=VTRIM1 value=1.8 savecurrent=false}
C {vsource.sym} -660 80 0 0 {name=VTRIM0 value=1.8 savecurrent=false}
C {code.sym} 180 -280 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {code_shown.sym} 350 -280 0 0 {name=SIM_CONTROL only_toplevel=false 
value="
.save all
.control
.endc"}
C {ldo_top_forsimul.sym} 0 0 0 0 {name=x1}
C {lab_pin.sym} 180 20 0 1 {name=p3 sig_type=std_logic lab=DIV_OUT}
C {lab_pin.sym} 180 0 0 1 {name=p4 sig_type=std_logic lab=VDDC}
C {lab_pin.sym} 180 -20 0 1 {name=p5 sig_type=std_logic lab=VREF_LOW
}
C {vsource.sym} -360 80 0 0 {name=VTRIM4 value=1.8 savecurrent=false}
C {vsource.sym} -290 80 0 0 {name=VTRIM5 value=1.8 savecurrent=false}
