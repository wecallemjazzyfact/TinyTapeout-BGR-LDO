gds maskhints yes
gds read ldo_top.gds
load ldo_top
select top cell
expand
drc style drc(full)
drc euclidean on
drc check
set r [drc listall why]
set f [open lu45.txt w]
foreach {e c} $r { foreach k $c { puts $f "$e|$k" } }
close $f
quit -noprompt
