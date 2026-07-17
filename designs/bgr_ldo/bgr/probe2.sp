.lib /foss/pdks/sky130A/libs.tech/combined/sky130.lib.spice tt
.temp 27
Vvap vapwr 0 3.3
Vg   g     0 2.0
Vout out   0 1.8
XMP out g vapwr vapwr sky130_fd_pr__pfet_g5v0d10v5 L=0.5 W=400 nf=1
.control
op
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[vdsat]
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gm]
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[gds]
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgg]
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgd]
print @m.xmp.msky130_fd_pr__pfet_g5v0d10v5[cgs]
.endc
.end
