v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 70 -280 70 -180 {lab=0}
N 70 -280 70 -180 {lab=0}
N 70 -450 70 -340 {lab=VAPWR}
N 70 -450 310 -450 {lab=VAPWR}
N 310 -450 310 -370 {lab=VAPWR}
N 310 -250 310 -200 {lab=0}
N 70 -200 310 -200 {lab=0}
N 460 -330 530 -330 {lab=VREF_LOW}
N 460 -290 530 -290 {lab=IB_EA}
N 530 -290 530 -190 {lab=IB_EA}
C {vsource.sym} 70 -310 0 0 {name=VSource value=3.3 savecurrent=false}
C {code_shown.sym} 580 -1050 0 0 {name=SIM_CONTROL only_toplevel=false 
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
C {code.sym} 380 -930 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {gnd.sym} 70 -180 0 0 {name=l8 lab=0}
C {bgr_core.sym} 310 -310 0 0 {name=x1}
C {vsource.sym} 530 -160 0 0 {name=Vload value=0.95 savecurrent=false}
C {gnd.sym} 530 -130 0 0 {name=l1 lab=0}
C {lab_pin.sym} 530 -330 1 0 {name=p1 sig_type=std_logic lab=VREF_LOW}
C {lab_pin.sym} 530 -260 2 0 {name=p2 sig_type=std_logic lab=IB_EA}
C {lab_pin.sym} 180 -450 1 0 {name=p3 sig_type=std_logic lab=VAPWR
}
