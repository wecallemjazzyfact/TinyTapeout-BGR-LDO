v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -210 -280 -210 -180 {lab=0}
N -210 -280 -210 -180 {lab=0}
N -210 -450 -210 -340 {lab=VAPWR}
N 70 -450 310 -450 {lab=VAPWR}
N 310 -450 310 -370 {lab=VAPWR}
N 310 -250 310 -200 {lab=0}
N 70 -200 310 -200 {lab=0}
N 460 -320 530 -320 {lab=VREF_LOW}
N 460 -300 530 -300 {lab=IB_EA}
N 530 -300 530 -280 {lab=IB_EA}
N 530 -280 530 -190 {lab=IB_EA}
N 530 -350 530 -320 {lab=VREF_LOW}
N 130 -340 160 -340 {lab=#net1}
N 130 -320 160 -320 {lab=#net2}
N 130 -300 160 -300 {lab=#net3}
N 130 -280 160 -280 {lab=#net4}
N -210 -200 70 -200 {lab=0}
N -210 -450 70 -450 {lab=VAPWR}
N 60 -280 130 -280 {lab=#net4}
N 60 -280 60 -260 {lab=#net4}
N -10 -300 130 -300 {lab=#net3}
N -10 -300 -10 -260 {lab=#net3}
N -80 -320 130 -320 {lab=#net2}
N -80 -320 -80 -260 {lab=#net2}
N -150 -340 130 -340 {lab=#net1}
N -150 -340 -150 -260 {lab=#net1}
C {vsource.sym} -210 -310 0 0 {name=VSource value=3.3 savecurrent=false}
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
C {gnd.sym} -210 -180 0 0 {name=l8 lab=0}
C {vsource.sym} 530 -160 0 0 {name=Vload value=0.95 savecurrent=false}
C {gnd.sym} 530 -130 0 0 {name=l1 lab=0}
C {lab_pin.sym} 530 -330 1 0 {name=p1 sig_type=std_logic lab=VREF_LOW}
C {lab_pin.sym} 530 -260 2 0 {name=p2 sig_type=std_logic lab=IB_EA}
C {lab_pin.sym} 180 -450 1 0 {name=p3 sig_type=std_logic lab=VAPWR
}
C {bgr_core.sym} 310 -310 0 0 {name=x1}
C {vsource.sym} -150 -230 0 0 {name=Vtrim0 value=1.8 savecurrent=false}
C {vsource.sym} -80 -230 0 0 {name=Vtrim1 value=1.8 savecurrent=false}
C {vsource.sym} -10 -230 0 0 {name=Vtrim2 value=1.8 savecurrent=false}
C {vsource.sym} 60 -230 0 0 {name=Vtrim3 value=1.8 savecurrent=false}
