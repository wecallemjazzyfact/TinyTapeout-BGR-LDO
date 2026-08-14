v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -110 110 210 110 {lab=0}
N 210 80 210 110 {lab=0}
N 210 0 210 20 {lab=DIV_OUT}
N 140 0 210 0 {lab=DIV_OUT}
N -110 -0 -30 -0 {lab=CK_IN}
N -110 -0 -110 30 {lab=CK_IN}
N -250 20 -250 40 {lab=VGND}
N -250 -70 -250 -40 {lab=VDPWR}
N -110 90 -110 110 {lab=0}
N -250 110 -110 110 {lab=0}
N -250 100 -250 110 {lab=0}
N 50 -100 50 -60 {lab=VDPWR}
N -250 -100 50 -100 {lab=VDPWR}
N -250 -100 -250 -70 {lab=VDPWR}
N 50 60 50 80 {lab=VGND}
C {div16_core.sym} 50 0 0 0 {name=x1}
C {vsource.sym} -110 60 0 0 {name=Vclk value=PULSE(0 1.78 0 90p 90p 4.509n 9.018n) savecurrent=false}
C {capa.sym} 210 50 0 0 {name=C1
m=1
value=5f
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} -40 0 3 0 {name=p4 sig_type=std_logic lab=CK_IN


}
C {lab_pin.sym} 160 0 3 0 {name=p1 sig_type=std_logic lab=DIV_OUT


}
C {code.sym} 200 -170 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {code_shown.sym} 400 -190 0 0 {name=SIM_CONTROL only_toplevel=false 
value="
.include /foss/designs/designs/bgr_ldo/ldo/dfxbp_1.spice
.save all
.control
set wr_singlescale
tran 20p 800n
wrdata div_tr.txt v(CK_IN) v(x1.net2) v(x1.net4) v(x1.net6) v(DIV_OUT)
.endc

"}
C {vsource.sym} -250 -10 0 0 {name=Vdd value=1.8 savecurrent=false}
C {lab_pin.sym} -250 30 0 0 {name=p2 sig_type=std_logic lab=VGND


}
C {lab_pin.sym} -250 -70 0 0 {name=p3 sig_type=std_logic lab=VDPWR


}
C {gnd.sym} -80 110 0 0 {name=l1 lab=0}
C {vsource.sym} -250 70 0 0 {name=Vgnd value=0 savecurrent=false}
C {lab_pin.sym} 50 80 0 0 {name=p5 sig_type=std_logic lab=VGND


}
