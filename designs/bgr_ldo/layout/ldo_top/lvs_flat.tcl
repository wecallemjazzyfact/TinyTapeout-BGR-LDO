set a [readnet spice ldo_top_flat_chk.spice]
set b [readnet spice /foss/designs/designs/bgr_ldo/ldo/ldo_top_lvs.spice]
readnet spice /foss/designs/designs/bgr_ldo/ldo/dfxbp_1.spice $b
readnet spice /foss/designs/designs/bgr_ldo/ldo/diode_2.spice $b
flatten class "$b ldo_top"
lvs "$a ldo_top_flat" "$b ldo_top" /foss/pdks/sky130A/libs.tech/netgen/sky130A_setup.tcl lvs_flat.txt
