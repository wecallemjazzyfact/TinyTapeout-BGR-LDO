v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N -370 -140 -370 -30 {lab=#net1}
N -370 -140 -0 -140 {lab=#net1}
N 0 -140 0 -50 {lab=#net1}
N 0 50 0 110 {lab=0}
N -370 110 0 110 {lab=0}
N -370 30 -370 110 {lab=0}
N -270 0 -150 -0 {lab=RO_EN}
N -270 60 -270 110 {lab=0}
N 150 -0 220 0 {lab=RO_OUT}
N 220 0 240 0 {lab=RO_OUT}
N 240 0 240 10 {lab=RO_OUT}
N 240 70 240 110 {lab=0}
N 0 110 240 110 {lab=0}
C {ring_osc_core.sym} 0 0 0 0 {name=x1}
C {code.sym} 210 -240 0 0 {
name=TT_MODELS
only_toplevel=true
format="tcleval( @value )"
value="
** opencircuitdesign pdks install
.lib $::SKYWATER_MODELS/sky130.lib.spice tt
"
spice_ignore=false
      }
C {code_shown.sym} 370 -240 0 0 {name=SIM_CONTROL only_toplevel=false 
value="

.save all

.control
set wr_singlescale
tran 5p 300n

echo ===== frequency (ring internal node) =====
meas tran t1 WHEN v(x1.net5)=0.9 RISE=20
meas tran t2 WHEN v(x1.net5)=0.9 RISE=40
let fosc = 20/(t2-t1)
print fosc

echo ===== supply current =====
meas tran iavg AVG i(Vdd) from=150n to=300n

echo ===== output swing =====
meas tran vhi MAX v(RO_OUT) from=150n to=300n
meas tran vlo MIN v(RO_OUT) from=150n to=300n

echo ===== duty (RO_OUT) =====
meas tran tr1 WHEN v(RO_OUT)=0.9 RISE=20
meas tran tf1 WHEN v(RO_OUT)=0.9 FALL=20
meas tran tr2 WHEN v(RO_OUT)=0.9 RISE=21
let duty = (tf1-tr1)/(tr2-tr1)*100
print duty

wrdata ro_tr.txt v(RO_EN) v(x1.net5) v(RO_OUT)
.endc

"}
C {vsource.sym} -370 0 0 0 {name=Vdd value=1.8 savecurrent=false}
C {gnd.sym} -370 110 0 0 {name=l1 lab=0}
C {vsource.sym} -270 30 0 0 {name=Ven value=PULSE(0 1.8 5n 100p 100p 500n 1u) savecurrent=false}
C {lab_pin.sym} -180 0 3 0 {name=p2 sig_type=std_logic lab=RO_EN}
C {lab_pin.sym} 170 0 3 0 {name=p1 sig_type=std_logic lab=RO_OUT}
C {capa.sym} 240 40 0 0 {name=Cdivin
m=1
value=5f
footprint=1206
device="ceramic capacitor"}
