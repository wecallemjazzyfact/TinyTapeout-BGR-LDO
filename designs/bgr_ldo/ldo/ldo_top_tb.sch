v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 0 80 0 120 {lab=0}
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
N -180 -50 -150 -50 {lab=#net1}
N -180 -30 -150 -30 {lab=#net2}
N -180 -10 -150 -10 {lab=#net3}
N -180 10 -150 10 {lab=#net4}
N -180 30 -150 30 {lab=#net5}
N -180 50 -150 50 {lab=#net6}
N -0 120 -0 140 {lab=0}
N -0 130 0 140 {lab=0}
N -440 130 0 130 {lab=0}
N -180 110 -180 130 {lab=0}
N -250 30 -180 30 {lab=#net5}
N -250 30 -250 50 {lab=#net5}
N -250 110 -250 130 {lab=0}
N -320 110 -320 130 {lab=0}
N -390 110 -390 130 {lab=0}
N -470 110 -470 130 {lab=0}
N -540 110 -540 130 {lab=0}
N -540 130 -440 130 {lab=0}
N -320 10 -180 10 {lab=#net4}
N -320 10 -320 50 {lab=#net4}
N -390 -10 -180 -10 {lab=#net3}
N -390 -10 -390 50 {lab=#net3}
N -470 -30 -180 -30 {lab=#net2}
N -470 -30 -470 50 {lab=#net2}
N -540 -50 -180 -50 {lab=#net1}
N -540 -50 -540 50 {lab=#net1}
N 150 20 210 20 {lab=DIV_OUT}
N 150 0 210 0 {lab=VDDC}
N 150 -20 210 -20 {lab=VREF_LOW}
C {gnd.sym} 0 140 0 0 {name=l1 lab=0}
C {vsource.sym} 340 -10 0 0 {name=VAPWR value=3.3 savecurrent=false}
C {vsource.sym} 300 -10 0 0 {name=VDPWR value=1.8 savecurrent=false}
C {lab_pin.sym} 340 -100 0 1 {name=p1 sig_type=std_logic lab=VAPWR}
C {lab_pin.sym} 300 -100 2 1 {name=p2 sig_type=std_logic lab=VDPWR}
C {vsource.sym} -180 80 0 0 {name=VRO_EN value=1.8 savecurrent=false}
C {vsource.sym} -250 80 0 0 {name=VSNK_EN value=1.8 savecurrent=false}
C {vsource.sym} -320 80 0 0 {name=VTRIM3 value=1.8 savecurrent=false}
C {vsource.sym} -390 80 0 0 {name=VTRIM2 value=1.8 savecurrent=false}
C {vsource.sym} -470 80 0 0 {name=VTRIM1 value=1.8 savecurrent=false}
C {vsource.sym} -540 80 0 0 {name=VTRIM0 value=1.8 savecurrent=false}
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
