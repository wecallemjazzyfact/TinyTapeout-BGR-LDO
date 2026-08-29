set a [readnet spice ldo_top_lay.spice]
readnet spice dfxbp_stub_a.spice $a
readnet spice diode_stub_a.spice $a
set b [readnet spice /foss/designs/designs/bgr_ldo/ldo/ldo_top.spice]
readnet spice dfxbp_stub_b.spice $b
readnet spice diode_stub_b.spice $b
lvs "$a ldo_top" "$b ldo_top" /foss/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl lvs_top2.txt
