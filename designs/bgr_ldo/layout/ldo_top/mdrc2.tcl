gds maskhints yes
gds read ldo_top_fixed.gds
load ldo_top
select top cell
expand
drc euclidean on
drc style drc(full)
drc check
set r [drc listall why]
set f [open lu_all.txt w]
foreach {e c} $r {
  foreach k $c { puts $f "$e|$k" }
}
close $f
quit -noprompt
