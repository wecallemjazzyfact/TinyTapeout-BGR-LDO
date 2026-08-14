v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -260 -140 -260 -30 {lab=0}
N -260 -30 140 -30 {lab=0}
N 140 -30 140 -20 {lab=0}
N 140 -90 140 -30 {lab=0}
N -260 -420 -260 -200 {lab=VAPWR}
N 140 -30 350 -30 {lab=0}
N -20 -110 50 -110 {lab=VNB1}
N -260 -240 -80 -240 {lab=VAPWR}
N -80 -240 -80 -110 {lab=VAPWR}
N 140 -420 140 -250 {lab=VAPWR}
N -140 -200 40 -200 {lab=#net1}
N 40 -200 50 -190 {lab=#net1}
N -140 -140 -140 -30 {lab=0}
N 230 -170 290 -170 {lab=V_EA}
N 20 -200 50 -150 {lab=#net1}
N -260 -420 140 -420 {lab=VAPWR}
C {ea_fc.sym} 130 -170 0 0 {name=x1}
C {vsource.sym} -260 -170 0 0 {name=VSource value=3.3 savecurrent=false}
C {gnd.sym} 140 -20 0 0 {name=l1 lab=0}
C {isource.sym} -50 -110 3 0 {name=I0 value=2.564228u}
C {vsource.sym} -140 -170 0 0 {name=VSource1 value=1.186591 savecurrent=false}
C {code.sym} 250 -600 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {lab_pin.sym} -140 -420 0 0 {name=p7 sig_type=std_logic lab=VAPWR
}
C {lab_pin.sym} 20 -110 3 0 {name=p1 sig_type=std_logic lab=VNB1
}
C {lab_pin.sym} 270 -170 3 0 {name=p2 sig_type=std_logic lab=V_EA
}
C {code_shown.sym} 420 -600 0 0 {name=SIM_CONTROL only_toplevel=false 
value=".save all @m.xxm_su_n1.msky130_fd_pr__nfet_g5v0d10v5[id]
.dc vsource 0 3.3 0.01

.control
  run
  echo ==========================================
  echo TEST 3: VAPWR DC Sweep (0V -> 3.3V)
  echo ==========================================
  plot v(vref_low)
  plot v(sense_out)
  write startup_dc.raw
.endc"}
